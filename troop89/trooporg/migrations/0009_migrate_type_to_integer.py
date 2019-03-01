# Generated by Django 2.1 on 2018-08-05 17:41
# Perfected once more by Brian Schubert at roughly the same time

# Part one: data migration

from django.db import migrations, models

TRANSITION_FIELD_NAME = 'type_transition'

TYPE_TRANSFORM_LOOKUP = {
    'L': 0,
    'A': 1,
    'M': 2,
}


def transform_type(apps, schema_editor):
    """Convert char-based type to int-based type"""
    PatrolMembership = apps.get_model('trooporg', 'PatrolMembership')
    db_alias = schema_editor.connection.alias

    for m in PatrolMembership.objects.using(db_alias).all():
        setattr(m, TRANSITION_FIELD_NAME, TYPE_TRANSFORM_LOOKUP[m.type])
        m.save()


def reverse_transform_type(apps, schema_editor):
    """Convert int-based type back to char-based type"""
    PatrolMembership = apps.get_model('trooporg', 'PatrolMembership')
    db_alias = schema_editor.connection.alias
    reverse_mapping = {v: k for k, v in TYPE_TRANSFORM_LOOKUP.items()}

    for m in PatrolMembership.objects.using(db_alias).all():
        m.type = reverse_mapping[getattr(m, TRANSITION_FIELD_NAME)]
        m.save()


class Migration(migrations.Migration):
    dependencies = [
        ('trooporg', '0008_prepopulate_slug_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='patrolmembership',
            name=TRANSITION_FIELD_NAME,
            field=models.SmallIntegerField(choices=[(0, 'Leader'), (1, 'Assistant'), (2, 'Member')], default=2),
        ),
        migrations.RunPython(
            transform_type,
            reverse_code=reverse_transform_type,
        ),
    ]