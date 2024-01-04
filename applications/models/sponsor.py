from .base import *


class SponsorApplication(models.Model):
    attendance = MultiSelectField(choices=ATTENDANCE)

    name = models.CharField(
        verbose_name='Full name',
        max_length=255,
    )
    # When was the application submitted
    submission_date = models.DateTimeField(default=timezone.now)

    # When was the last status update
    status_update_date = models.DateTimeField(blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(User, related_name='%(class)s_application', null=True, on_delete=models.SET_NULL)
    # Application status
    status = models.CharField(choices=STATUS,
                              default=APP_CONFIRMED,
                              max_length=2)
    phone_number = models.CharField(blank=True, null=True, max_length=16,
                                    validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                                               message="Phone number must be entered in the format: \
                                                                          '+#########'. Up to 15 digits allowed.")])

    # Info for swag and food
    diet = models.CharField(max_length=300, choices=DIETS, default=D_NONE)
    other_diet = models.CharField(max_length=600, blank=True, null=True)
    tshirt_size = models.CharField(max_length=5, default=DEFAULT_TSHIRT_SIZE, choices=TSHIRT_SIZES)
    position = models.CharField(max_length=50, null=False)

    email = models.EmailField(verbose_name='email', max_length=255, null=True)

    @property
    def uuid_str(self):
        return str(self.uuid)

    def __str__(self):
        return self.name + ' from ' + self.user.name

    def save(self, **kwargs):
        self.status_update_date = timezone.now()
        super(SponsorApplication, self).save(**kwargs)

    def check_in(self):
        self.status = APP_ATTENDED
        self.status_update_date = timezone.now()
        self.save()

    def get_diet_color(self):
        colors = {
            D_NONE: 'white',
            D_VEGETERIAN: '#7ABE6F',
        }
        return colors.get(self.diet, '#42A2CB')

    class META:
        unique_together = [['name', 'user']]
