import datetime

from django.contrib import auth
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse


class Member(auth.get_user_model()):
    """
    A scouting member.
    """

    class Meta:
        proxy = True

    def __str__(self):
        # NOTICE: Printing out user objects should *NEVER* occur on the live
        # site as doing so bypasses information safeguards for youth members.
        return self.get_full_name()

    def get_safe_display(self) -> str:
        """
        Return the proper display name for this member based on their
        youth/adult status.
        """
        if self.is_adult():
            return self.get_full_name()
        first = self.get_first_name()
        last = self.get_last_name()[:1]
        return f'{first} {last}.'

    def is_adult(self) -> bool:
        """
        Return True if this member is an adult.

        A member is considered to be an adult if they have held an adult
        position in the troop.
        """
        return self.position_types.filter(is_adult=True).exists()

    def is_active_member(self) -> bool:
        """Return True if this member is an active member of the troop."""
        return self.position_instances.current().exists() or self.patrol_memberships.current().exists()


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
        period = self.period_str()
        if self.nickname:
            period += f' ("{self.nickname}")'
        return period

    def get_absolute_url(self):
        args = self.start.strftime('%Y %m %d').split()
        return reverse('trooporg:term-detail', args=args)

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

    def period_str(self) -> str:
        """
        Return a string representation of the month period that this term
        overlaps with.
        """
        start = self.start.strftime("%b %Y")
        end = self.end.strftime("%b %Y")
        return f'{start} - {end}'

    def is_current(self) -> bool:
        """Return True if this term overlaps with today."""
        today = datetime.date.today()
        return self.start <= today < self.end


class AbstractByTermQuerySet(models.QuerySet):
    """Query set that may be filtered by a related term."""
    term_field = 'term'

    def current(self):
        """Filter by the current term."""
        current = Term.objects.current()
        return self.filter(**{self.term_field: current})


class PositionType(models.Model):
    """A position that a troop member can hold."""

    title = models.CharField(max_length=40, unique=True)

    precedence = models.PositiveSmallIntegerField(
        help_text='Used to help define the order in which similar positions '
                  'should be displayed. Positions with greater precedence will '
                  'generally be displayed first.',
        default=0,
    )

    members = models.ManyToManyField(
        Member,
        related_name='position_types',
        through='PositionInstance',
    )

    is_adult = models.BooleanField(
        help_text='Whether or not this position signifies that a member is an'
                  'adult. This criteria is used for display purposes only.',
    )

    is_leader = models.BooleanField(
        help_text="Whether or not this position is primarily a leadership role."
                  "This criteria is used for partitioning positions for display "
                  "in some cases."
    )

    class Meta:
        ordering = ('precedence',)

    def __str__(self):
        return self.title


class PositionInstanceQuerySet(AbstractByTermQuerySet):
    """
    Query set for position instances.

    Provided to ease future expansion.
    """
    pass


class PositionInstance(models.Model):
    """
    Connects a member to a position type and to the term during which they
    fulfilled that position.
    """

    incumbent = models.ForeignKey(
        Member,
        related_name='position_instances',
        on_delete=models.CASCADE,
    )

    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
    )

    type = models.ForeignKey(
        PositionType,
        related_name='instances',
        on_delete=models.PROTECT
    )

    objects = PositionInstanceQuerySet.as_manager()

    class Meta:
        unique_together = ('incumbent', 'term', 'type')

    def __str__(self):
        name = self.incumbent.get_full_name()
        title = self.type.title
        period = self.term.period_str()
        return f'{name} ({title} for {period})'


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

    def __str__(self):
        return f'{self.name} Patrol'

    def get_absolute_url(self):
        return reverse('trooporg:patrol-detail', args=(self.slug,))

    def is_active(self) -> bool:
        """Return True if there exists an active membership for this patrol."""
        try:
            return self.memberships.current().exists()
        except Term.DoesNotExist:
            return False

    is_active.boolean = True


class PatrolMembershipQuerySet(AbstractByTermQuerySet):
    """
    Query set for patrol memberships.

    Provided to ease future expansion.
    """
    pass


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

    def __str__(self):
        name = self.scout.get_full_name(),
        patrol = self.patrol.name,
        pos = self.get_type_display()
        return f'{name} ({patrol} {pos})'
