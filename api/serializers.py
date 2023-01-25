from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import Room, Event, Book


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class RoomSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

    def create(self, validated_data):
        event = super(EventSerializer, self).create(validated_data=validated_data)
        event.places_available = event.room.capacity
        event.save()
        return event


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'event', 'status', ]
        read_only_fields = ['status']

    def create(self, validated_data):
        book = super(BookSerializer, self).create(validated_data=validated_data)
        book.event.places_available -= 1
        book.event.save()
        return book


class HLBookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'url', 'event', 'status', ]
        read_only_fields = ['status']

    def create(self, validated_data):
        book = super(HLBookSerializer, self).create(validated_data=validated_data)
        book.event.places_available -= 1
        book.event.save()
        return book
