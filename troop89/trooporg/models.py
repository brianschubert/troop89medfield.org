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


class TermManager(models.Manager):
    def current(self):
        today = datetime.date.today()
        return self.for_date(today)

    def for_date(self, date: datetime.date):
        return self.get_queryset().get(start__lte=date, end__gt=date)


class Term(models.Model):
    nickname = models.CharField(null=True, blank=True, max_length=32, unique=True)

    start = models.DateField(default=datetime.date.today)

    end = models.DateField()

    objects = TermManager()

    def __str__(self):
        form = '{} - {}'.format(
            self.start.strftime("%b %Y"),
            self.end.strftime("%b %Y")
        )
        if self.nickname:
            form += ' ("{}")'.format(self.nickname)
        return form


class PatrolQuerySet(models.QuerySet):
    pass


class Patrol(models.Model):
    """
    A scout patrol.
    """
    name = models.CharField(max_length=32, unique=True)

    date_created = models.DateField(default=datetime.date.today)

    members = models.ManyToManyField(ScoutMembership, through='PatrolMembership')

    objects = PatrolQuerySet.as_manager()

    def __str__(self):
        return "{} Patrol".format(self.name)

    def is_active(self) -> bool:
        try:
            return self.memberships.active().exists()
        except Term.DoesNotExist:
            return False

    is_active.boolean = True


class PatrolMembershipQuerySet(models.QuerySet):
    def active(self):
        current_term = Term.objects.current()
        return self.filter(term=current_term)


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

    term = models.ForeignKey(
        Term,
        related_name='patrol_memberships',
        on_delete=models.PROTECT
    )

    type = models.CharField(
        max_length=1,
        choices=PATROL_MEMBERSHIP_TYPE_CHOICES,
        default=MEMBER
    )

    objects = PatrolMembershipQuerySet.as_manager()

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
