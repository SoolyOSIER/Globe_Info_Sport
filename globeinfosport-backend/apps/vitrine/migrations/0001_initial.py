import apps.vitrine.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbonneNewsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('actif', models.BooleanField(default=True)),
                ('token_desabonnement', models.CharField(default=apps.vitrine.models.generer_token_desabonnement, editable=False, max_length=64, unique=True)),
            ],
            options={
                'verbose_name': 'abonné newsletter',
                'verbose_name_plural': 'abonnés newsletter',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=255)),
                ('reponse', models.TextField()),
                ('ordre', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
                'ordering': ['ordre', 'question'],
            },
        ),
        migrations.CreateModel(
            name='MessageContact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nom', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('sujet', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('traite', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'message de contact',
                'verbose_name_plural': 'messages de contact',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PageContenu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cle', models.SlugField(max_length=80, unique=True)),
                ('titre', models.CharField(max_length=180)),
                ('contenu', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='pages/')),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'contenu de page',
                'verbose_name_plural': 'contenus de pages',
                'ordering': ['cle'],
            },
        ),
        migrations.CreateModel(
            name='Partenaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=150)),
                ('logo', models.ImageField(upload_to='partenaires/')),
                ('url', models.URLField(blank=True)),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('actif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'partenaire',
                'verbose_name_plural': 'partenaires',
                'ordering': ['ordre', 'nom'],
            },
        ),
    ]
