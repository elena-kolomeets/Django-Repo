from django.contrib.auth.models import User
from django.db import models


def save_image(instance, filename):
    # image will be uploaded to a folder with the username
    return f'{instance.user.username}/{filename}'


class Image(models.Model):
    image = models.ImageField(upload_to=save_image)
    # an entire image analysis result
    result = models.JSONField(blank=True, default='')
    # image description extracted from the result
    description = models.CharField(max_length=200, blank=True, default='')
    # image tags extracted from the result
    tags = models.CharField(max_length=250, blank=True, default='')
    # image HEX colors extracted from the result
    colors = models.CharField(max_length=50, blank=True, default='')
    # the associated user
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        # display image paths in admin
        return self.image.name
