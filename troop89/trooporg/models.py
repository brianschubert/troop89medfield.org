import datetime

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class ScoutMembership(models.Model):
    """
    A scouting membership that relates a user to troop organization models.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='scout_membership',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.username


class Patrol(models.Model):
    """
    A scout patrol.
    """
    name = models.CharField(max_length=32, unique=True)

    date_created = models.DateField(default=datetime.date.today)

    date_retired = models.DateField(null=True, blank=True)

    members = models.ManyToManyField(ScoutMembership, through='PatrolMembership')

    def __str__(self):
        return "{} Patrol".format(self.name)

    @property
    def is_active(self) -> bool:
        return self.date_retired is None or self.active_on(datetime.date.today())

    def active_on(self, day: datetime.date) -> bool:
        return self.date_created <= day < self.date_retired


class PatrolMembership(models.Model):
    """
    A membership to a scout patrol.
    """
    LEADER = 'L'

    ASSISTANT = 'A'

    MEMBER = 'M'

    PATROL_MEMBERSHIP_TYPE_CHOICES = (
        (LEADER, 'Leader'),
        (ASSISTANT, 'Assistant'),
        (MEMBER, 'Member'),
    )

    scout = models.ForeignKey(
        ScoutMembership,
        related_name='patrol_memberships',
        on_delete=models.CASCADE
    )

    patrol = models.ForeignKey(
        Patrol,
        related_name='memberships',
        on_delete=models.PROTECT
    )

    date_joined = models.DateField(default=datetime.date.today)

    date_expired = models.DateField(null=True, blank=True)

    type = models.CharField(
        max_length=1,
        choices=PATROL_MEMBERSHIP_TYPE_CHOICES,
        default=MEMBER
    )

    def __str__(self):
        return '{name} ({patrol} {pos})'.format(
            name=self.scout.user.get_full_name(),
            patrol=self.patrol.name,
            pos=self.type
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_scout_membership(sender, instance, created, **kwargs):
    """Create a scout membership upon user creation."""
    if created:
        ScoutMembership.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_scout_membership(sender, instance, created, **kwargs):
    """Save the scout membership when the user is saved."""
    instance.scout_membership.save()
