from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('actualites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='auteur',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='article',
            name='categorie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='articles', to='actualites.categorie'),
        ),
        migrations.AddField(
            model_name='article',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='articles', to='actualites.tag'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['statut', '-date_publication'], name='actualites__statut_e1c67a_idx'),
        ),
        migrations.AddIndex(
            model_name='article',
            index=models.Index(fields=['a_la_une', '-date_publication'], name='actualites__a_la_un_fb40ce_idx'),
        ),
    ]
