from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Event(models.Model):
    EVENT_TYPES = (
        ('public', 'PUBLIC'),
        ('private', 'PRIVATE'),
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    event = models.CharField(max_length=250)
    type = models.CharField(max_length=10, default='public', choices=EVENT_TYPES)
    date = models.DateField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.event


class Book(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.BooleanField(default=True)
