import datetime

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Member(auth.get_user_model()):
    """
    A scouting member.
    """

    class Meta:
        proxy = True

    def __str__(self):
        return self.username


class TermManager(models.Manager):
    def current(self):
        """Return the term that overlaps with the current date."""
        today = datetime.date.today()
        return self.for_date(today)

    def for_date(self, date: datetime.date):
        """Return the term that overlaps with the given date."""
        return self.get_queryset().get(start__lte=date, end__gt=date)


class Term(models.Model):
    nickname = models.CharField(null=True, blank=True, max_length=32, unique=True)

    start = models.DateField(default=datetime.date.today)

    end = models.DateField()

    objects = TermManager()

    class Meta:
        ordering = ('-start',)
        get_latest_by = ('start',)

    def __str__(self):
        form = '{} - {}'.format(
            self.start.strftime("%b %Y"),
            self.end.strftime("%b %Y")
        )
        if self.nickname:
            form += ' ("{}")'.format(self.nickname)
        return form

    def clean(self):
        # Calling parent in case it is given a non-empty body in the future (currently it is empty).
        super().clean()

        if not self.start < self.end:
            raise ValidationError('Term start MUST occur before the term\'s end.')

        one_day = datetime.timedelta(days=1)

        if Term.objects.exclude(pk=self.pk).filter(
            # Allow one term's end date to coincide with another term's start date
            Q(start__range=(self.start, self.end - one_day)) |
            Q(end__range=(self.start + one_day, self.end)) |
            Q(start__lt=self.start, end__gt=self.end)
        ).exists():
            raise ValidationError('Term overlaps with an existing term.')


class PatrolQuerySet(models.QuerySet):
    pass


class Patrol(models.Model):
    """A scout patrol."""
    name = models.CharField(max_length=32, unique=True)

    slug = models.SlugField(
        unique=True,
        help_text="URL Slug that identifies this patrol. "
                  "Changing this will invalidate any existing urls pointing to this patrol."
    )

    date_created = models.DateField(default=datetime.date.today)

    members = models.ManyToManyField(Member, through='PatrolMembership')

    objects = PatrolQuerySet.as_manager()

    def __str__(self):
        return "{} Patrol".format(self.name)

    def is_active(self) -> bool:
        """Return True if there exists an active membership for this patrol."""
        try:
            return self.memberships.active().exists()
        except Term.DoesNotExist:
            return False

    is_active.boolean = True


class PatrolMembershipQuerySet(models.QuerySet):
    def active(self):
        """Exclude memberships not associated with the current term."""
        current_term = Term.objects.current()
        return self.filter(term=current_term)


class PatrolMembership(models.Model):
    """A membership to a scout patrol."""
    LEADER = 0

    ASSISTANT = 1

    MEMBER = 2

    PATROL_MEMBERSHIP_TYPE_CHOICES = (
        (LEADER, 'Leader'),
        (ASSISTANT, 'Assistant'),
        (MEMBER, 'Member'),
    )

    scout = models.ForeignKey(
        Member,
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

    type = models.SmallIntegerField(
        choices=PATROL_MEMBERSHIP_TYPE_CHOICES,
        default=MEMBER
    )

    objects = PatrolMembershipQuerySet.as_manager()

    class Meta:
        ordering = ('-term__start', 'type')

    def __str__(self):
        return '{name} ({patrol} {pos})'.format(
            name=self.scout.get_full_name(),
            patrol=self.patrol.name,
            pos=self.type
        )
