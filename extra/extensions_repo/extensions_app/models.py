from django.db import models

from bd_models.models import Ball, Special, BallInstance

class SpecialExtra(models.Model):
    enable_background = models.BooleanField(help_text="Whether or not the built-in background is enabled", default=False)