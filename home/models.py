from django.db import models
from base.models import BaseModel


class Feedback(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    subject = models.CharField(max_length=100)
    message = models.TextField()
    
    def __str__(self):
        return self.name + str(' ') + str(self.subject)