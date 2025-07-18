# Generated by Django 4.2.7 on 2025-07-02 21:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('report_type', models.CharField(choices=[('children_summary', 'Résumé des enfants'), ('donations_summary', 'Résumé des dons'), ('inventory_report', "Rapport d'inventaire"), ('financial_report', 'Rapport financier'), ('staff_report', 'Rapport du personnel'), ('family_report', 'Rapport des familles'), ('medical_report', 'Rapport médical'), ('custom_report', 'Rapport personnalisé')], max_length=30, verbose_name='Type de rapport')),
                ('template_config', models.JSONField(default=dict, verbose_name='Configuration du modèle')),
                ('default_parameters', models.JSONField(default=dict, verbose_name='Paramètres par défaut')),
                ('custom_query', models.TextField(blank=True, verbose_name='Requête personnalisée')),
                ('header_template', models.TextField(blank=True, verbose_name="Modèle d'en-tête")),
                ('footer_template', models.TextField(blank=True, verbose_name='Modèle de pied de page')),
                ('css_styles', models.TextField(blank=True, verbose_name='Styles CSS')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif')),
                ('allowed_roles', models.JSONField(default=list, verbose_name='Rôles autorisés')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Modèle de rapport',
                'verbose_name_plural': 'Modèles de rapports',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('report_type', models.CharField(choices=[('children_summary', 'Résumé des enfants'), ('donations_summary', 'Résumé des dons'), ('inventory_report', "Rapport d'inventaire"), ('financial_report', 'Rapport financier'), ('staff_report', 'Rapport du personnel'), ('family_report', 'Rapport des familles'), ('medical_report', 'Rapport médical'), ('custom_report', 'Rapport personnalisé')], max_length=30, verbose_name='Type de rapport')),
                ('parameters', models.JSONField(blank=True, default=dict, verbose_name='Paramètres')),
                ('date_from', models.DateField(blank=True, null=True, verbose_name='Date de début')),
                ('date_to', models.DateField(blank=True, null=True, verbose_name='Date de fin')),
                ('format', models.CharField(choices=[('pdf', 'PDF'), ('excel', 'Excel'), ('csv', 'CSV'), ('json', 'JSON')], default='pdf', max_length=10, verbose_name='Format')),
                ('file', models.FileField(blank=True, null=True, upload_to='reports/', verbose_name='Fichier')),
                ('file_size', models.PositiveIntegerField(blank=True, null=True, verbose_name='Taille du fichier')),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('generating', 'En cours de génération'), ('completed', 'Terminé'), ('failed', 'Échoué')], default='pending', max_length=20, verbose_name='Statut')),
                ('error_message', models.TextField(blank=True, verbose_name="Message d'erreur")),
                ('is_scheduled', models.BooleanField(default=False, verbose_name='Planifié')),
                ('schedule_frequency', models.CharField(blank=True, choices=[('daily', 'Quotidien'), ('weekly', 'Hebdomadaire'), ('monthly', 'Mensuel'), ('quarterly', 'Trimestriel'), ('yearly', 'Annuel')], max_length=20, verbose_name='Fréquence')),
                ('next_generation_date', models.DateTimeField(blank=True, null=True, verbose_name='Prochaine génération')),
                ('is_public', models.BooleanField(default=False, verbose_name='Public')),
                ('allowed_roles', models.JSONField(blank=True, default=list, verbose_name='Rôles autorisés')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('generated_at', models.DateTimeField(blank=True, null=True, verbose_name='Généré le')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Rapport',
                'verbose_name_plural': 'Rapports',
                'ordering': ['-created_at'],
                'permissions': [('can_generate_reports', 'Peut générer des rapports'), ('can_view_all_reports', 'Peut voir tous les rapports'), ('can_schedule_reports', 'Peut planifier des rapports')],
            },
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Nom')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('layout_config', models.JSONField(default=dict, verbose_name='Configuration de mise en page')),
                ('widgets', models.JSONField(default=list, verbose_name='Widgets')),
                ('refresh_interval', models.PositiveIntegerField(default=300, verbose_name='Intervalle de rafraîchissement (secondes)')),
                ('is_default', models.BooleanField(default=False, verbose_name='Par défaut')),
                ('is_public', models.BooleanField(default=False, verbose_name='Public')),
                ('allowed_roles', models.JSONField(default=list, verbose_name='Rôles autorisés')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Créé le')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Modifié le')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboards', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Tableau de bord',
                'verbose_name_plural': 'Tableaux de bord',
                'ordering': ['name'],
            },
        ),
    ]
