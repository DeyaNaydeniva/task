from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, UserPatchSerializer


class UserListView(APIView):
    def get(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin access required.'}, status=status.HTTP_403_FORBIDDEN)
        users = User.objects.all()
        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)


class UserDetailView(APIView):
    def _get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self._get_user(pk)
        if user is None:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        user = self._get_user(pk)
        if user is None:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.pk != user.pk and not request.user.is_staff:
            return Response({'error': 'You can only edit your own profile.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserPatchSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = self._get_user(pk)
        if user is None:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        if request.user.pk != user.pk and not request.user.is_staff:
            return Response({'error': 'You can only delete your own account.'}, status=status.HTTP_403_FORBIDDEN)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
