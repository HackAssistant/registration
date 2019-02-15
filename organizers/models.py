from __future__ import unicode_literals

from django.db import models
# Votes weight
from django.db.models import Avg, F
from django.utils import timezone

from applications.models import Application
from user.models import User

TECH_WEIGHT = 0.44
PERSONAL_WEIGHT = 0.33
PASSION_WEIGHT = 0.23
CULTURE_WEIGHT = 0.0

VOTES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
)
VOTES_INTERNATIONAL = (
    (1, 'Kosice'),
    (2, 'CZ/SK'),
    (3, 'Europe'),
    (4, 'Extreme')
)


class Vote(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User)

    tech = models.IntegerField(choices=VOTES, null=True)
    personal = models.IntegerField(choices=VOTES, null=True)
    passion = models.IntegerField(choices=VOTES, null=True)
    culture = models.IntegerField(choices=VOTES_INTERNATIONAL, null=True)

    calculated_vote = models.FloatField(null=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        We are overriding this in order to standarize each review vote with the
        new vote.
        Also we store a calculated vote for each vote so that we don't need to
        do it later.

        Thanks to Django awesomeness we do all the calculations with only 3
        queries to the database. 2 selects and 1 update. The performance is way
        faster than I thought.
        If improvements need to be done using a better DB than SQLite should
        increase performance. As long as the database can handle aggregations
        efficiently this will be good.

        By casassg
        """
        super(Vote, self).save(force_insert, force_update, using,
                               update_fields)

        # only recalculate when values are different than None
        if not self.personal or not self.tech or not self.passion or not self.culture:
            return

        # Retrieve averages
        avgs = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg('vote__tech'),
            pers=Avg('vote__personal'),
            passion=Avg('vote__passion'),
            culture=Avg('vote__culture')
        )
        p_avg = round(avgs['pers'], 2)
        t_avg = round(avgs['tech'], 2)
        pa_avg = round(avgs['passion'], 2)
        c_avg = round(avgs['culture'], 2)

        # Calculate standard deviation for each scores
        sds = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg((F('vote__tech') - t_avg) * (F('vote__tech') - t_avg)),
            pers=Avg((F('vote__personal') - p_avg) * (F('vote__personal') - p_avg)),
            passion=Avg((F('vote__passion') - pa_avg) * (F('vote__passion') - pa_avg)),
            culture=Avg((F('vote__culture') - c_avg) * (F('vote__culture') - c_avg))
        )

        # Alternatively, if standard deviation is 0.0, set it as 1.0 to avoid
        # division by 0.0 in the update statement
        p_sd = round(sds['pers'], 2) or 1.0
        t_sd = round(sds['tech'], 2) or 1.0
        pa_sd = round(sds['passion'], 2) or 1.0
        c_sd = round(sds['culture'], 2) or 1.0

        # Apply standarization. Standarization formula:
        # x(new) = (x - u)/o
        # where u is the mean and o is the standard deviation
        #
        # See this: http://www.dataminingblog.com/standardization-vs-
        # normalization/
        tech = TECH_WEIGHT * (F('tech') - t_avg) / t_sd
        personal = PERSONAL_WEIGHT * (F('personal') - p_avg) / p_sd
        passion = PASSION_WEIGHT * (F('passion') - pa_avg) / pa_sd
        culture = CULTURE_WEIGHT * (F('culture') - c_avg) / c_sd
        Vote.objects.filter(user=self.user).update(calculated_vote=personal + tech + passion + culture)

    class Meta:
        unique_together = ('application', 'user')


class ApplicationComment(models.Model):
    application = models.ForeignKey(Application, null=False)
    author = models.ForeignKey(User)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
