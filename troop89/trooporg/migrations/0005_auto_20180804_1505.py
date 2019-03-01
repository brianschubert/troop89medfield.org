# Generated by Django 2.1 on 2018-08-04 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trooporg', '0004_prepopulate_term_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patrolmembership',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='patrol_memberships', to='trooporg.Term'),
        ),
    ]