from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('joueurs', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubEtranger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
                ('pays', models.CharField(max_length=100)),
                ('ligue', models.CharField(blank=True, max_length=150)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='clubs_etrangers/')),
            ],
            options={
                'verbose_name': 'club étranger',
                'verbose_name_plural': 'clubs étrangers',
                'ordering': ['pays', 'nom'],
            },
        ),
        migrations.CreateModel(
            name='Transfert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('club_origine', models.CharField(max_length=150)),
                ('club_destination', models.CharField(max_length=150)),
                ('date_transfert', models.DateField()),
                ('type_transfert', models.CharField(choices=[('DEFINITIF', 'Transfert définitif'), ('PRET', 'Prêt')], max_length=15)),
                ('montant', models.CharField(blank=True, max_length=50)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('joueur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transferts', to='joueurs.joueur')),
            ],
            options={
                'verbose_name': 'transfert',
                'verbose_name_plural': 'transferts',
                'ordering': ['-date_transfert', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JoueurExpatrie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('date_arrivee', models.DateField(blank=True, null=True)),
                ('statut', models.CharField(choices=[('ACTIF', 'Actif'), ('PRETE', 'Prêté'), ('BLESSE', 'Blessé'), ('LIBRE', 'Libre')], default='ACTIF', max_length=20)),
                ('en_vedette', models.BooleanField(default=False)),
                ('club_etranger', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='joueurs_expatries', to='expatries.clubetranger')),
                ('joueur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fiche_expatrie', to='joueurs.joueur')),
            ],
            options={
                'verbose_name': 'joueur expatrié',
                'verbose_name_plural': 'joueurs expatriés',
                'ordering': ['-en_vedette', 'joueur__nom', 'joueur__prenom'],
            },
        ),
        migrations.AddConstraint(
            model_name='clubetranger',
            constraint=models.UniqueConstraint(fields=('nom', 'pays', 'ligue'), name='club_etranger_nom_pays_ligue_unique'),
        ),
    ]
