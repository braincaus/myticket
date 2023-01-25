from django.urls import path, include
from rest_framework import routers

from api.views import RoomViewSet, EventViewSet, BookViewSet, RegisterUser, LoginUser

router = routers.DefaultRouter()
router.register('rooms', RoomViewSet)
router.register('events', EventViewSet)
router.register('books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('signin', RegisterUser.as_view()),
    path('login', LoginUser.as_view())
]
