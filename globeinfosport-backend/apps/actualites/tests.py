from datetime import timedelta
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from apps.comptes.models import RoleRedaction, Utilisateur
from apps.competitions.models import Competition
from .models import Article, Categorie, Sport, Pays, Selection, Video
from .tasks import publier_articles_programmes


@override_settings(CELERY_TASK_ALWAYS_EAGER=True, CELERY_TASK_EAGER_PROPAGATES=False)
class EditorialWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        role, _ = RoleRedaction.objects.get_or_create(nomRole="REDACTEUR")
        editor_role, _ = RoleRedaction.objects.get_or_create(nomRole="EDITEUR_EN_CHEF")
        self.author = Utilisateur.objects.create_user("writer", "TestPass123!", nom="Writer", role_redaction=role)
        self.other = Utilisateur.objects.create_user("other", "TestPass123!", nom="Other", role_redaction=role)
        self.editor = Utilisateur.objects.create_user("editor", "TestPass123!", nom="Editor", role_redaction=editor_role)
        self.category = Categorie.objects.create(nom="Test")
        self.article = Article.objects.create(titre="Une histoire", chapo="Chapeau", contenu="<p>Texte</p>", categorie=self.category, auteur=self.author)
        self.url = f"/api/v1/articles/{self.article.pk}/"

    def test_author_submit_but_cannot_publish_or_schedule(self):
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.post(self.url + "soumettre/").status_code, 200)
        self.assertEqual(self.client.post(self.url + "publier/").status_code, 403)
        self.assertEqual(self.client.post(self.url + "programmer/").status_code, 403)
        self.assertEqual(self.client.patch(self.url, {"statut": "PUBLIE"}).status_code, 400)
        self.assertEqual(self.client.patch(self.url, {"statut": "PROGRAMME"}).status_code, 400)

    def test_writer_cannot_modify_another_authors_published_article(self):
        self.article.statut = Article.Statut.PUBLIE
        self.article.save()
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(self.url, {"titre": "Intrusion"}).status_code, 403)
        self.assertEqual(self.client.get(self.url + "historique/").status_code, 403)
        self.assertEqual(self.client.post(self.url + "commentaires/", {"texte": "Intrusion"}).status_code, 403)

    def test_schedule_is_private_then_publishes_once_when_due(self):
        self.client.force_authenticate(self.editor)
        due = timezone.now() + timedelta(hours=1)
        response = self.client.post(self.url + "programmer/", {"date_publication": due.isoformat()})
        self.assertEqual(response.status_code, 200, response.data)
        self.client.force_authenticate(None)
        public_url = f"/api/v1/public/articles/{self.article.slug}/"
        self.assertEqual(self.client.get(public_url).status_code, 404)
        self.assertEqual(publier_articles_programmes(), 0)
        Article.objects.filter(pk=self.article.pk).update(date_publication=timezone.now() - timedelta(minutes=1))
        self.assertEqual(publier_articles_programmes(), 1)
        self.assertEqual(publier_articles_programmes(), 0)
        self.assertEqual(self.client.get(public_url).status_code, 200)

    def test_invalid_schedule_rejected_and_revision_records_edits(self):
        self.client.force_authenticate(self.editor)
        for value in ["invalid", "2020-01-01T12:00:00Z", "2099-01-01T12:00:00"]:
            self.assertEqual(self.client.post(self.url + "programmer/", {"date_publication": value}).status_code, 400)
        self.assertEqual(self.client.patch(self.url, {"titre": "Nouveau titre"}).status_code, 200)
        self.assertEqual(self.article.revisions.last().donnees["titre"], "Nouveau titre")

    def test_global_sport_and_country_filters(self):
        sport = Sport.objects.create(nom="Basketball")
        country = Pays.objects.create(nom="Japon", code="JP", region="Asie")
        self.article.sport = sport
        self.article.statut = Article.Statut.PUBLIE
        self.article.save()
        self.article.pays.add(country)
        result = self.client.get("/api/v1/public/articles/", {"zone": "international", "sport": sport.pk, "pays": country.pk})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["count"], 1)
        self.assertEqual(self.client.get("/api/v1/public/articles/", {"zone": "haiti"}).data["count"], 0)

    def test_public_video_does_not_expose_draft(self):
        Video.objects.create(titre="Interview confidentielle", url_embed="https://www.youtube.com/watch?v=abcdefghijk", article_lie=self.article)
        result = self.client.get("/api/v1/public/videos/")
        self.assertEqual(result.data["count"], 0)

    def test_author_can_attach_videos_to_an_article(self):
        self.client.force_authenticate(self.author)
        response = self.client.patch(
            self.url,
            {"video_urls": ["https://www.youtube.com/watch?v=abcdefghijk"]},
            format="json",
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(self.article.videos.count(), 1)

    def test_reference_write_requires_admin(self):
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.post("/api/v1/sports/", {"nom": "Nouveau sport"}).status_code, 403)
        self.assertEqual(self.client.get("/api/v1/sports/").status_code, 200)

    def test_public_selection_exposes_its_sport_country_and_competitions(self):
        sport = Sport.objects.create(nom="Volley-ball")
        country = Pays.objects.create(nom="Haïti", code="HT", region="Caraïbes")
        competition = Competition.objects.create(
            nom="Coupe des Caraïbes", type=Competition.Type.AUTRE, saison="2026", sport=sport, pays=country
        )
        selection = Selection.objects.create(nom="Haïti féminin", pays=country, sport=sport, entraineur="Coach")
        selection.competitions.add(competition)
        self.client.force_authenticate(None)
        response = self.client.get(f"/api/v1/public/selections/{selection.pk}/")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["pays_detail"]["code"], "HT")
        self.assertEqual(response.data["sport_detail"]["nom"], "Volley-ball")
        self.assertEqual(response.data["competitions_detail"][0]["nom"], "Coupe des Caraïbes")

    def test_multipart_article_preserves_explicit_empty_relations(self):
        import json
        from .models import Tag
        tag = Tag.objects.create(nom="Interview")
        self.article.tags.add(tag)
        Video.objects.create(titre="Video", url_embed="https://example.com/video", article_lie=self.article)
        self.client.force_authenticate(self.author)
        response = self.client.patch(self.url, {"payload": json.dumps({"tags": [], "video_urls": []})}, format="multipart")
        self.assertEqual(response.status_code, 200, response.data)
        self.assertFalse(self.article.tags.exists())
        self.assertFalse(self.article.videos.exists())

    def test_return_to_draft_requires_editor_and_clears_schedule(self):
        self.article.statut = Article.Statut.PROGRAMME
        self.article.date_publication = timezone.now() + timedelta(hours=2)
        self.article.save()
        self.client.force_authenticate(self.author)
        self.assertEqual(self.client.patch(self.url, {"statut": "BROUILLON"}).status_code, 400)
        self.assertEqual(self.client.post(self.url + "reprendre/").status_code, 403)
        self.client.force_authenticate(self.editor)
        response = self.client.post(self.url + "reprendre/")
        self.assertEqual(response.status_code, 200, response.data)
        self.article.refresh_from_db()
        self.assertEqual(self.article.statut, Article.Statut.BROUILLON)
        self.assertIsNone(self.article.date_publication)
        self.assertEqual(self.client.get(self.url + "historique/").data[0]["action"], "BROUILLON")

    def test_bilateral_article_appears_in_both_regions_once(self):
        haiti = Pays.objects.create(nom="Haiti", code="HT", region="Caraïbes")
        france = Pays.objects.create(nom="France", code="FR", region="Europe")
        self.article.pays.add(haiti, france)
        self.article.statut = Article.Statut.PUBLIE
        self.article.save()
        for zone in ["haiti", "international"]:
            response = self.client.get("/api/v1/public/articles/", {"zone": zone})
            self.assertEqual(response.data["count"], 1)

    def test_public_directories_apply_region_zone_and_search(self):
        from apps.competitions.models import Club
        sport = Sport.objects.create(nom="Tennis")
        haiti = Pays.objects.create(nom="Haiti", code="HT", region="Caraïbes")
        france = Pays.objects.create(nom="France", code="FR", region="Europe")
        for model in [Club, Selection, Competition]:
            for country in [haiti, france]:
                values = {"nom": "Equipe " + country.code, "pays": country, "sport": sport}
                if model == Competition:
                    values.update(type=Competition.Type.AUTRE, saison="2026")
                model.objects.create(**values)
        for resource in ["clubs", "selections", "competitions"]:
            response = self.client.get(f"/api/v1/public/{resource}/", {"zone": "haiti"})
            self.assertEqual(response.status_code, 200, response.data)
            self.assertEqual([item["nom"] for item in response.data["results"]], ["Equipe HT"])
            response = self.client.get(f"/api/v1/public/{resource}/", {"region": "Europe", "search": "Equipe FR"})
            self.assertEqual(response.data["count"], 1)
            response = self.client.get(f"/api/v1/public/{resource}/", {"search": "absent"})
            self.assertEqual(response.data["count"], 0)

    def test_article_navigation_never_exposes_drafts_or_future_articles(self):
        self.article.statut = Article.Statut.PUBLIE
        self.article.save()
        values = {"chapo": "Chapeau", "contenu": "Texte", "categorie": self.category, "auteur": self.author}
        older = Article.objects.create(titre="Older", statut=Article.Statut.PUBLIE, date_publication=timezone.now()-timedelta(days=1), **values)
        Article.objects.create(titre="Draft", **values)
        Article.objects.create(titre="Future", statut=Article.Statut.PUBLIE, date_publication=timezone.now()+timedelta(days=1), **values)
        response = self.client.get(f"/api/v1/public/articles/{self.article.slug}/")
        self.assertEqual(response.data["precedent"]["slug"], older.slug)
        self.assertIsNone(response.data["suivant"])

    def test_inactive_editor_has_no_permission(self):
        from apps.core.permissions import has_minimum_role
        self.editor.is_active = False
        self.assertFalse(has_minimum_role(self.editor, "REDACTEUR"))

    def test_create_non_football_athlete_without_position_and_validate_fields(self):
        sport = Sport.objects.create(nom="Natation")
        country = Pays.objects.create(nom="Japon", code="JP", region="Asie")
        self.client.force_authenticate(self.author)
        response = self.client.post("/api/v1/joueurs/", {"nom": "Athlete", "sport": sport.pk, "pays": country.pk}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIsNone(response.data["poste"])
        url = f"/api/v1/joueurs/{response.data['id']}/"
        response = self.client.patch(url, {"taille_cm": 2}, format="json")
        self.assertEqual(response.status_code, 400)
        self.client.force_authenticate(None)
        response = self.client.get("/api/v1/public/joueurs/", {"sport": sport.pk, "region": "Asie"})
        self.assertEqual(response.data["count"], 1)

    @override_settings(PUBLIC_SITE_URL="https://example.com")
    def test_sitemap_only_indexes_public_articles(self):
        self.article.statut = Article.Statut.PUBLIE
        self.article.save()
        response = self.client.get("/sitemap.xml?page=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "https://example.com/actualites/" + self.article.slug)
        self.article.statut = Article.Statut.BROUILLON
        self.article.save()
        self.assertNotContains(self.client.get("/sitemap.xml?page=1"), self.article.slug)
        self.assertEqual(self.client.get("/sitemap.xml?page=invalid").status_code, 404)
        self.assertContains(self.client.get("/robots.txt"), "https://example.com/sitemap.xml")
