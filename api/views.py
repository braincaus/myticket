from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import permissions, status, authentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from api.serializers import RoomSerializer, EventSerializer, BookSerializer, UserSerializer, HLBookSerializer
from core.models import Room, Event, Book


# Create your views here.


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]

    def get_permissions(self):
        if self.request.user.is_superuser:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.request.user.is_authenticated:
            self.permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        result = super(RoomViewSet, self).get_permissions()
        return result


class EventViewSet(ModelViewSet):
    queryset = Event.objects.filter(status=True)
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]

    def get_permissions(self):
        if self.request.user.is_superuser:
            self.permission_classes = [permissions.IsAdminUser]
        elif self.request.user.is_authenticated:
            self.permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
        else:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        result = super(EventViewSet, self).get_permissions()
        return result

    def get_queryset(self):
        result = super(EventViewSet, self).get_queryset()
        today = datetime.today().date()
        result = result.filter(date__gte=today)
        if not self.request.user.is_superuser:
            result = result.filter(type='public')
        return result


class BookViewSet(ModelViewSet):
    queryset = Book.objects.filter(status=True)
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication, authentication.SessionAuthentication]

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = HLBookSerializer
        else:
            self.serializer_class = BookSerializer
        return super(BookViewSet, self).get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        return super(BookViewSet, self).get_serializer()

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

    def create(self, request, *args, **kwargs):
        event = request.data.get('event', None)
        event = Event.objects.get(id=event)

        if event.status is False:
            return Response(data={'error': 'Event not available'}, status=status.HTTP_400_BAD_REQUEST)

        elif event.places_available == 0:
            return Response(data={'error': 'Event without places available'}, status=status.HTTP_400_BAD_REQUEST)

        books = Book.objects.filter(event=event, customer=request.user, status=True)
        if books:
            return Response(data={'error': 'Event already booked'}, status=status.HTTP_400_BAD_REQUEST)

        return super(BookViewSet, self).create(request=request)

    def get_queryset(self):
        result = super(BookViewSet, self).get_queryset()
        if not self.request.user.is_superuser:
            result = result.filter(customer=self.request.user)

        return result

    @action(methods=['POST', 'GET'], detail=True, url_path='cancel', url_name='cancel_book')
    def cancel_book(self, request, pk):
        book = self.get_object()
        book.event.places_available += 1
        book.event.save()
        book.status = False
        book.save()
        return Response(data=None, status=status.HTTP_204_NO_CONTENT)


class RegisterUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        if None in [email, password]:
            return Response(data={"error": "email and password ar required"}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=email, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response(data={"token": token.key}, status=status.HTTP_201_CREATED)


class LoginUser(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email', None)
        password = data.get('password', None)
        if None in [email, password]:
            return Response(data={"error": "email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response(data={"token": token.key}, status=status.HTTP_200_OK)

        return Response(data={"error": "email and password not found"}, status=status.HTTP_400_BAD_REQUEST)
