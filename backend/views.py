from djoser.views import UserViewSet as BaseUserViewSet

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from backend.models import User
from backend.serializers import UserSerializer

from rest_framework import status


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class ConfirmUserViewSet(BaseUserViewSet):
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['data'] = {
            'email': self.kwargs.get('email'),
            'token': self.kwargs.get('token'),
        }

    def activation(self, request, *args, **kwargs):
        super().activation(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
