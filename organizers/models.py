from __future__ import unicode_literals

from django.db import models
# Votes weight
from django.db.models import Avg, F
from django.utils import timezone

from app.settings import MAX_VOTES
from applications.models import Application
from user.models import User

TECH_WEIGHT = 0.2
PERSONAL_WEIGHT = 0.8

VOTES = []
for i in range(MAX_VOTES):
    VOTES.append((i + 1, str(i + 1)))


class Vote(models.Model):
    application = models.ForeignKey(Application)
    user = models.ForeignKey(User)
    tech = models.IntegerField(choices=VOTES, null=True)
    personal = models.IntegerField(choices=VOTES, null=True)
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
        if not self.personal or not self.tech:
            return

        # Retrieve averages
        avgs = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg('vote__tech'),
            pers=(Avg('vote__personal')))
        p_avg = round(avgs['pers'], 2)
        t_avg = round(avgs['tech'], 2)

        # Calculate standard deviation for each scores
        sds = User.objects.filter(id=self.user_id).aggregate(
            tech=Avg((F('vote__tech') - t_avg) * (F('vote__tech') - t_avg)),
            pers=Avg((F('vote__personal') - p_avg) * (F('vote__personal') - p_avg)))

        # Alternatively, if standard deviation is 0.0, set it as 1.0 to avoid
        # division by 0.0 in the update statement
        p_sd = round(sds['pers'], 2) or 1.0
        t_sd = round(sds['tech'], 2) or 1.0

        # Apply standarization. Standarization formula:
        # x(new) = (x - u)/o
        # where u is the mean and o is the standard deviation
        #
        # See this: http://www.dataminingblog.com/standardization-vs-
        # normalization/
        personal = PERSONAL_WEIGHT * ((F('personal')) - p_avg) / p_sd
        tech = TECH_WEIGHT * ((F('tech')) - t_avg) / t_sd
        Vote.objects.filter(user=self.user).update(calculated_vote=(personal + tech) * MAX_VOTES / 10)

    class Meta:
        unique_together = ('application', 'user')


class ApplicationComment(models.Model):
    application = models.ForeignKey(Application, null=False)
    author = models.ForeignKey(User)
    text = models.CharField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
