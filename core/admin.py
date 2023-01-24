from django.contrib import admin

from core.models import Event, Room, Book


# Register your models here.


class EventInline(admin.TabularInline):
    model = Event
    extra = 0


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    inlines = [EventInline, ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass
