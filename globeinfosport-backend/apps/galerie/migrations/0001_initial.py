from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('competitions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumGalerie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('titre', models.CharField(max_length=150)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('match_lie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='albums', to='competitions.match')),
            ],
            options={
                'verbose_name': 'album galerie',
                'verbose_name_plural': 'albums galerie',
                'ordering': ['-created_at', 'titre'],
            },
        ),
        migrations.CreateModel(
            name='ImageGalerie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(upload_to='galerie/')),
                ('legende', models.CharField(blank=True, max_length=200)),
                ('ordre', models.PositiveIntegerField(default=0)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='galerie.albumgalerie')),
            ],
            options={
                'verbose_name': 'image galerie',
                'verbose_name_plural': 'images galerie',
                'ordering': ['ordre', '-created_at'],
                'indexes': [models.Index(fields=['album', 'ordre'], name='galerie_ima_album_i_bc1dbd_idx')],
            },
        ),
    ]
