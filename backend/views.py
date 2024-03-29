from djoser.views import UserViewSet as BaseUserViewSet

from rest_framework.permissions import IsAuthenticatedOrReadOnly


from backend.models import User
from backend.serializers import UserSerializer


class UserViewSet(BaseUserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = IsAuthenticatedOrReadOnly

