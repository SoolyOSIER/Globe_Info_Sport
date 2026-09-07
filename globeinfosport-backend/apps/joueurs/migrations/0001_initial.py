from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Legende',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nom', models.CharField(max_length=150)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='legendes/')),
                ('periode_active', models.CharField(blank=True, max_length=50)),
                ('poste', models.CharField(blank=True, max_length=50)),
                ('biographie', models.TextField()),
                ('exploits', models.TextField(blank=True)),
                ('ordre_affichage', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'légende',
                'verbose_name_plural': 'légendes',
                'ordering': ['ordre_affichage', 'nom'],
            },
        ),
        migrations.CreateModel(
            name='Poste',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Joueur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nom', models.CharField(max_length=150)),
                ('prenom', models.CharField(blank=True, max_length=150)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='joueurs/')),
                ('date_naissance', models.DateField(blank=True, null=True)),
                ('club_actuel', models.CharField(blank=True, max_length=150)),
                ('numero_maillot', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('taille_cm', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('pied_fort', models.CharField(blank=True, choices=[('GAUCHE', 'Gauche'), ('DROIT', 'Droit')], max_length=10)),
                ('biographie', models.TextField(blank=True)),
                ('selection_nationale', models.BooleanField(default=True)),
                ('nb_selections', models.PositiveIntegerField(default=0)),
                ('nb_buts_selection', models.PositiveIntegerField(default=0)),
                ('emblematique', models.BooleanField(default=False)),
                ('poste', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='joueurs', to='joueurs.poste')),
            ],
            options={
                'verbose_name': 'joueur',
                'verbose_name_plural': 'joueurs',
                'ordering': ['nom', 'prenom'],
                'indexes': [models.Index(fields=['selection_nationale', 'emblematique'], name='joueurs_jou_selecti_e2de96_idx')],
            },
        ),
    ]
