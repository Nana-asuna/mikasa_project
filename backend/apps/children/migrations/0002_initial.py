# Generated by Django 4.2.7 on 2025-07-02 20:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('children', '0001_initial'),
        ('families', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='child',
            name='adoption_family',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adopted_children', to='families.family', verbose_name='Famille adoptive'),
        ),
        migrations.AddField(
            model_name='child',
            name='case_worker',
            field=models.ForeignKey(limit_choices_to={'role__in': ['assistant_social', 'admin']}, on_delete=django.db.models.deletion.CASCADE, related_name='case_children', to=settings.AUTH_USER_MODEL, verbose_name='Assistant social responsable'),
        ),
        migrations.AddField(
            model_name='child',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_children', to=settings.AUTH_USER_MODEL, verbose_name='Créé par'),
        ),
        migrations.AddField(
            model_name='child',
            name='sponsor',
            field=models.ForeignKey(limit_choices_to={'role__in': ['parrain', 'donateur']}, on_delete=django.db.models.deletion.CASCADE, related_name='sponsored_children', to=settings.AUTH_USER_MODEL, verbose_name='Parrain/Marraine'),
        ),
    ]
