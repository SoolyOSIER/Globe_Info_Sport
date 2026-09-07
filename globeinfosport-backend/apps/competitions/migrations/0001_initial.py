from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('joueurs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ButeurMatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minute', models.PositiveSmallIntegerField()),
                ('type_but', models.CharField(choices=[('BUT', 'But'), ('PENALTY', 'Penalty'), ('CSC', 'Contre son camp')], default='BUT', max_length=15)),
            ],
            options={
                'verbose_name': 'buteur du match',
                'verbose_name_plural': 'buteurs des matchs',
                'ordering': ['minute', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='ClassementLigne',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('matchs_joues', models.PositiveIntegerField(default=0)),
                ('victoires', models.PositiveIntegerField(default=0)),
                ('nuls', models.PositiveIntegerField(default=0)),
                ('defaites', models.PositiveIntegerField(default=0)),
                ('buts_pour', models.PositiveIntegerField(default=0)),
                ('buts_contre', models.PositiveIntegerField(default=0)),
                ('points', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'ligne de classement',
                'verbose_name_plural': 'lignes de classement',
                'ordering': ['-points', '-buts_pour', '-buts_contre', 'club__nom'],
            },
        ),
        migrations.CreateModel(
            name='Club',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nom', models.CharField(max_length=150, unique=True)),
                ('ville', models.CharField(blank=True, max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='clubs/')),
                ('stade', models.CharField(blank=True, max_length=150)),
                ('fondation', models.PositiveIntegerField(blank=True, null=True)),
                ('palmares', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Competition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
                ('type', models.CharField(choices=[('CHAMPIONNAT_NATIONAL', 'Championnat National'), ('ELIMINATOIRES_CDM', 'Éliminatoires Coupe du Monde'), ('LIGUE_NATIONS', 'Ligue des Nations CONCACAF'), ('AUTRE', 'Autre')], max_length=30)),
                ('saison', models.CharField(help_text='Ex. « 2025-2026 ».', max_length=20)),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['-actif', '-saison', 'nom'],
            },
        ),
        migrations.CreateModel(
            name='StatistiqueJoueur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('matchs_joues', models.PositiveIntegerField(default=0)),
                ('buts', models.PositiveIntegerField(default=0)),
                ('passes_decisives', models.PositiveIntegerField(default=0)),
                ('cartons_jaunes', models.PositiveIntegerField(default=0)),
                ('cartons_rouges', models.PositiveIntegerField(default=0)),
                ('clean_sheets', models.PositiveIntegerField(default=0)),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistiques_joueurs', to='competitions.competition')),
                ('joueur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='statistiques', to='joueurs.joueur')),
            ],
            options={
                'verbose_name': 'statistique joueur',
                'verbose_name_plural': 'statistiques joueurs',
                'ordering': ['-buts', '-passes_decisives', '-clean_sheets', 'joueur__nom'],
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('adversaire_texte', models.CharField(blank=True, max_length=150)),
                ('date_heure', models.DateTimeField()),
                ('lieu', models.CharField(blank=True, max_length=200)),
                ('diffusion_tv', models.CharField(blank=True, max_length=150)),
                ('score_domicile', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('score_exterieur', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('A_VENIR', 'À venir'), ('EN_COURS', 'En cours'), ('TERMINE', 'Terminé'), ('REPORTE', 'Reporté')], default='A_VENIR', max_length=20)),
                ('resume', models.TextField(blank=True)),
                ('club_domicile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matchs_domicile', to='competitions.club')),
                ('club_exterieur', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='matchs_exterieur', to='competitions.club')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='matchs', to='competitions.competition')),
            ],
            options={
                'ordering': ['date_heure'],
            },
        ),
        migrations.AddConstraint(
            model_name='competition',
            constraint=models.UniqueConstraint(fields=('nom', 'type', 'saison'), name='competition_nom_type_saison_unique'),
        ),
        migrations.AddField(
            model_name='classementligne',
            name='club',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classements', to='competitions.club'),
        ),
        migrations.AddField(
            model_name='classementligne',
            name='competition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classement', to='competitions.competition'),
        ),
        migrations.AddField(
            model_name='buteurmatch',
            name='joueur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='joueurs.joueur'),
        ),
        migrations.AddField(
            model_name='buteurmatch',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buteurs', to='competitions.match'),
        ),
        migrations.AddConstraint(
            model_name='statistiquejoueur',
            constraint=models.UniqueConstraint(fields=('joueur', 'competition'), name='statistique_joueur_competition_unique'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['competition', 'statut', 'date_heure'], name='competition_competi_f8fa5c_idx'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['statut', 'date_heure'], name='competition_statut_a216d5_idx'),
        ),
        migrations.AddConstraint(
            model_name='classementligne',
            constraint=models.UniqueConstraint(fields=('competition', 'club'), name='classement_ligne_competition_club_unique'),
        ),
        migrations.AddIndex(
            model_name='buteurmatch',
            index=models.Index(fields=['match', 'joueur'], name='competition_match_i_6ee152_idx'),
        ),
    ]
