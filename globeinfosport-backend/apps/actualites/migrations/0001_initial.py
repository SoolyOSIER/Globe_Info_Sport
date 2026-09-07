from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('titre', models.CharField(max_length=250)),
                ('slug', models.SlugField(blank=True, max_length=270, unique=True)),
                ('chapo', models.CharField(max_length=300)),
                ('contenu', models.TextField()),
                ('image_une', models.ImageField(blank=True, null=True, upload_to='articles/')),
                ('statut', models.CharField(choices=[('BROUILLON', 'Brouillon'), ('A_VALIDER', 'À valider'), ('PUBLIE', 'Publié'), ('ARCHIVE', 'Archivé')], default='BROUILLON', max_length=15)),
                ('a_la_une', models.BooleanField(default=False)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('date_publication', models.DateTimeField(blank=True, null=True)),
                ('compteur_vues', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['-date_publication', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Categorie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name': 'catégorie',
                'verbose_name_plural': 'catégories',
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='ChiffreCle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('libelle', models.CharField(max_length=100)),
                ('valeur', models.CharField(max_length=30)),
                ('icone', models.CharField(blank=True, max_length=50)),
                ('calcule_auto', models.BooleanField(default=True)),
                ('code_calcul', models.CharField(blank=True, max_length=50)),
                ('ordre', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'chiffre clé',
                'verbose_name_plural': 'chiffres clés',
                'ordering': ['ordre'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'ordering': ['nom'],
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('titre', models.CharField(max_length=200)),
                ('url_embed', models.URLField()),
                ('a_la_une', models.BooleanField(default=False)),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('article_lie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='videos', to='actualites.article')),
            ],
            options={
                'ordering': ['ordre', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('auteur_nom', models.CharField(max_length=150)),
                ('auteur_fonction', models.CharField(blank=True, max_length=150)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='citations/')),
                ('texte', models.TextField()),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('article_lie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='citations', to='actualites.article')),
            ],
            options={
                'ordering': ['ordre', '-created_at'],
            },
        ),
    ]
