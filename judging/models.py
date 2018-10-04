from django.db import models
from django.db.models import Count, Q

from user.models import User


class Challenge(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class Project(models.Model):
    title = models.CharField(max_length=200, unique=True)
    url = models.URLField(blank=True)
    description = models.CharField(max_length=2000)
    video = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    desired_prizes = models.CharField(max_length=400)
    built_with = models.CharField(blank=True, null=True, max_length=400)
    submitter_screen_name = models.CharField(blank=True, null=True, max_length=200)
    submitter_first_name = models.CharField(blank=True, null=True, max_length=100)
    submitter_last_name = models.CharField(blank=True, null=True, max_length=100)
    submitter_email = models.CharField(blank=True, null=True, max_length=200)
    university = models.CharField(blank=True, null=True, max_length=300)
    additional_team_member_count = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class Room(models.Model):
    name = models.CharField(max_length=40, unique=True)
    challenge = models.ForeignKey(Challenge, null=True, on_delete=models.SET_NULL)
    main_judge = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'is_organizer': True}
    )

    def get_current_presentations(self):
        return Presentation.objects.filter(done=False, room=self)

    def __str__(self):
        return self.name


class PresentationManager(models.Manager):

    def create_from_projects(self, projects):
        for project in projects:
            challenge_names = {d.strip() for d in project.desired_prizes.split(',')}
            for challenge_name in challenge_names:
                challenge, _ = Challenge.objects.get_or_create(name=challenge_name)
                num_pending_presentations = Count('presentation', filter=Q(presentation__done=False))
                rooms = Room.objects \
                    .filter(challenge=challenge) \
                    .annotate(queue_len=num_pending_presentations) \
                    .order_by('queue_len')
                room_to_assign = rooms.first()

                if room_to_assign is None:
                    room_name = challenge_name + ' 00'
                    room_to_assign = Room.objects.create(name=room_name, challenge=challenge)
                    room_to_assign.queue_len = 0

                Presentation.objects.get_or_create(project=project, room=room_to_assign,
                                                   defaults={
                                                       'done': False,
                                                       'turn': room_to_assign.queue_len
                                                   })
        return None

    def get_last_turn(self, room):
        return Presentation.objects.filter(room=room).order_by('turn').last().turn


class Presentation(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    turn = models.IntegerField(null=True)
    done = models.BooleanField(default=False)

    objects = PresentationManager()

    def __str__(self):
        return str(self.project) + ' @ ' + str(self.room)

    class Meta:
        unique_together = (('project', 'room'),)


JUDGE_ALIASES = [
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C')
]

VOTES = (
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5')
)


class PresentationEvaluation(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE)
    judge_alias = models.CharField(choices=JUDGE_ALIASES, max_length=1)
    tech = models.IntegerField(choices=VOTES)
    design = models.IntegerField(choices=VOTES)
    completion = models.IntegerField(choices=VOTES)
    learning = models.IntegerField(choices=VOTES)

    class Meta:
        unique_together = (('presentation', 'judge_alias'))
