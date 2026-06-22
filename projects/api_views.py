from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Project, ProjectMembership
from .serializers import ProjectSerializer, MembershipSerializer, MembershipRolePatchSerializer


def get_membership(project, user):
    """Return the user's ProjectMembership for a project, or None."""
    try:
        return ProjectMembership.objects.get(project=project, user=user)
    except ProjectMembership.DoesNotExist:
        return None


def get_accessible_project(pk, user):
    """
    Return (project, membership) if the user can access the project,
    else return (None, None) — callers should 404 in that case.
    Admin users have full access.
    """
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return None, None

    if user.is_staff:
        membership = get_membership(project, user)
        return project, membership

    membership = get_membership(project, user)
    if membership is None:
        return None, None
    return project, membership


class ProjectListView(APIView):
    def get(self, request):
        if request.user.is_staff:
            projects = Project.objects.all()
        else:
            member_project_ids = ProjectMembership.objects.filter(
                user=request.user
            ).values_list('project_id', flat=True)
            projects = Project.objects.filter(id__in=member_project_ids)
        return Response(ProjectSerializer(projects, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        project = serializer.save(owner=request.user)
        # Create owner membership
        ProjectMembership.objects.create(
            project=project,
            user=request.user,
            role=ProjectMembership.OWNER,
        )
        return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)


class ProjectDetailView(APIView):
    def get(self, request, pk):
        project, _ = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProjectSerializer(project).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can update this project.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can update this project.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can delete this project.'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemberListView(APIView):
    def get(self, request, pk):
        project, _ = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        memberships = project.memberships.select_related('user').all()
        return Response(MembershipSerializer(memberships, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can add members.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = MembershipSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user_id = serializer.validated_data['user_id']
        role = serializer.validated_data.get('role', ProjectMembership.MEMBER)

        if ProjectMembership.objects.filter(project=project, user_id=user_id).exists():
            return Response({'error': 'User is already a member of this project.'}, status=status.HTTP_400_BAD_REQUEST)

        new_membership = ProjectMembership.objects.create(
            project=project,
            user_id=user_id,
            role=role,
        )
        return Response(MembershipSerializer(new_membership).data, status=status.HTTP_201_CREATED)


class MemberDetailView(APIView):
    def _get_target_membership(self, project, uid):
        try:
            return ProjectMembership.objects.get(project=project, user_id=uid)
        except ProjectMembership.DoesNotExist:
            return None

    def patch(self, request, pk, uid):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can change roles.'}, status=status.HTTP_403_FORBIDDEN)
        target = self._get_target_membership(project, uid)
        if target is None:
            return Response({'error': 'Membership not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MembershipRolePatchSerializer(target, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(MembershipSerializer(target).data, status=status.HTTP_200_OK)

    def delete(self, request, pk, uid):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner = request.user.is_staff or (membership and membership.role == ProjectMembership.OWNER)
        if not is_owner:
            return Response({'error': 'Only the project owner can remove members.'}, status=status.HTTP_403_FORBIDDEN)
        target = self._get_target_membership(project, uid)
        if target is None:
            return Response({'error': 'Membership not found.'}, status=status.HTTP_404_NOT_FOUND)
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
