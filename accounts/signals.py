# accounts/signals.py

import os
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import ProcessedFile, UserProfile
from django.contrib.auth.models import User

@receiver(post_delete, sender=ProcessedFile)
def delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

