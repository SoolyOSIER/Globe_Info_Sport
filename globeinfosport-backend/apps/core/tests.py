import json
from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient

from apps.actualites.models import Pays, Sport, Selection
from apps.competitions.models import Club, Competition
from apps.comptes.models import RoleRedaction, Utilisateur


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class EditorialPagesApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        role = RoleRedaction.objects.create(nomRole="ADMINISTRATEUR", pk=41)
        writer_role = RoleRedaction.objects.create(nomRole="REDACTEUR", pk=43)
        cls.admin = Utilisateur.objects.create_user("admin-test", "TestOnly!2026", nom="Admin", role_redaction=role)
        cls.writer = Utilisateur.objects.create_user("writer-test", "TestOnly!2026", nom="Writer", role_redaction=writer_role)
        cls.sport = Sport.objects.create(nom="Sport test")
        cls.country = Pays.objects.create(nom="Pays test", code="TT", region="Caraïbes")
        cls.club = Club.objects.create(nom="Club test", sport=cls.sport, pays=cls.country)
        cls.competition = Competition.objects.create(nom="Competition test", type="AUTRE", saison="2026")

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_every_editorial_collection_is_accessible_to_admin(self):
        for resource in ["articles", "categories", "tags", "sports", "pays", "selections", "joueurs", "postes", "competitions", "clubs", "parcours-clubs", "matchs", "clubs-etrangers", "joueurs-expatries", "transferts", "albums", "images", "legendes", "flux-syndication", "messages-contact", "newsletter", "faq", "pages-contenu", "partenaires", "utilisateurs", "roles", "videos", "citations"]:
            with self.subTest(resource=resource):
                response = self.client.get(f"/api/v1/{resource}/")
                self.assertEqual(response.status_code, 200, response.data)
                self.assertIsInstance(response.data["results"], list)

    def test_writer_reads_catalog_but_cannot_change_it(self):
        self.client.force_authenticate(self.writer)
        for resource in ["clubs", "competitions", "parcours-clubs", "clubs-etrangers", "joueurs-expatries", "transferts", "selections"]:
            with self.subTest(resource=resource):
                self.assertEqual(self.client.get(f"/api/v1/{resource}/").status_code, 200)
                self.assertEqual(self.client.post(f"/api/v1/{resource}/", {}, format="json").status_code, 403)
        self.assertEqual(self.client.get("/api/v1/roles/").status_code, 403)

    def test_roles_use_database_ids(self):
        response = self.client.get("/api/v1/roles/")
        self.assertEqual({role["nomRole"]: role["id"] for role in response.data["results"]}, {"ADMINISTRATEUR": 41, "REDACTEUR": 43})
        response = self.client.post("/api/v1/utilisateurs/", {"identifiant": "created", "nom": "Created", "password": "UniquePassword!2026", "role_redaction": 43}, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Utilisateur.objects.get(identifiant="created").role_redaction_id, 43)

    def test_image_upload_clears_empty_many_to_many_lists(self):
        selection = Selection.objects.create(nom="Selection test", sport=self.sport, pays=self.country)
        selection.competitions.add(self.competition)
        content = BytesIO()
        Image.new("RGB", (2, 2)).save(content, format="PNG")
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            response = self.client.patch(f"/api/v1/selections/{selection.pk}/", {
                "payload": json.dumps({"competitions": []}),
                "logo": SimpleUploadedFile("logo.png", content.getvalue(), content_type="image/png"),
            }, format="multipart")
            self.assertEqual(response.status_code, 200, response.data)
            self.assertFalse(selection.competitions.exists())
            selection.refresh_from_db()
            self.assertTrue(selection.logo)

    def test_protected_delete_returns_actionable_conflict(self):
        response = self.client.delete(f"/api/v1/sports/{self.sport.pk}/")
        self.assertEqual(response.status_code, 409, response.data)
        self.assertTrue(Sport.objects.filter(pk=self.sport.pk).exists())

    def test_malformed_multipart_payload_is_rejected(self):
        for payload in ["not-json", "[]", "null"]:
            response = self.client.post("/api/v1/clubs/", {"payload": payload}, format="multipart")
            self.assertEqual(response.status_code, 400, response.data)
