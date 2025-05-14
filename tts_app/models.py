from django.db import models
from django.contrib.auth.models import User

class ClonedVoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_audio = models.FileField(upload_to='cloned_voices/originals/')
    text = models.TextField()
    cloned_audio = models.FileField(upload_to='cloned_voices/outputs/')
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=10, default='en')

    def __str__(self):
        return f"Cloned Voice by {self.user.username} at {self.created_at}"
