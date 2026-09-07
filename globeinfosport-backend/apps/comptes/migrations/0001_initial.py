import apps.comptes.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleRedaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nomRole', models.CharField(choices=[('REDACTEUR', 'Rédacteur'), ('EDITEUR_EN_CHEF', 'Éditeur en chef'), ('ADMINISTRATEUR', 'Administrateur')], max_length=30, unique=True)),
            ],
            options={
                'verbose_name': 'rôle de rédaction',
                'verbose_name_plural': 'rôles de rédaction',
                'ordering': ['nomRole'],
            },
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('identifiant', models.CharField(max_length=150, unique=True)),
                ('nom', models.CharField(max_length=150)),
                ('prenom', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='redaction/')),
                ('bio', models.CharField(blank=True, max_length=255)),
                ('date_creation_compte', models.DateTimeField(auto_now_add=True)),
                ('dernier_acces', models.DateTimeField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('role_redaction', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='utilisateurs', to='comptes.roleredaction')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'utilisateur',
                'verbose_name_plural': 'utilisateurs',
                'ordering': ['nom', 'prenom', 'identifiant'],
            },
            managers=[
                ('objects', apps.comptes.models.UtilisateurManager()),
            ],
        ),
    ]
