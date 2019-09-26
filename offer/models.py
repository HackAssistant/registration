from django.core.validators import FileExtensionValidator
from django.db import models


class Offer(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="offer/logo",
                             validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "gif"])])
    codes = models.FileField(upload_to="offer/codes", validators=[FileExtensionValidator(allowed_extensions=["csv"])])
    description = models.TextField(max_length=1000, blank=True, null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        codes = {c for c in self.codes.read().decode("utf-8").replace("\"", "").replace(" ", "").split("\n") if c}
        codes -= set(Code.objects.filter(offer_id=self.id).values_list("code", flat=True))
        Code.objects.bulk_create([Code(offer=self, code=c) for c in codes])


class Code(models.Model):
    offer = models.ForeignKey("offer.Offer", on_delete=models.CASCADE)
    user = models.ForeignKey("user.User", on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=255)
