from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project, ProjectMembership
from projects.api_views import get_accessible_project
from .models import Task, Label
from .serializers import TaskSerializer, LabelSerializer


def _can_write(membership, user):
    """Return True if user has owner or member role (not viewer-only)."""
    if user.is_staff:
        return True
    return membership is not None and membership.role in (
        ProjectMembership.OWNER, ProjectMembership.MEMBER
    )


def _is_owner_role(membership, user):
    if user.is_staff:
        return True
    return membership is not None and membership.role == ProjectMembership.OWNER


class ProjectTaskListView(APIView):
    def get(self, request, pk):
        project, _ = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        tasks = project.tasks.select_related('assignee', 'created_by').prefetch_related('labels').all()
        return Response(TaskSerializer(tasks, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _can_write(membership, request.user):
            return Response({'error': 'Viewers cannot create tasks.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        task = serializer.save(project=project, created_by=request.user)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    def _get_task_and_project(self, task_pk, user):
        try:
            task = Task.objects.select_related('project').get(pk=task_pk)
        except Task.DoesNotExist:
            return None, None, None
        project, membership = get_accessible_project(task.project_id, user)
        if project is None:
            return None, None, None
        return task, project, membership

    def get(self, request, pk):
        task, _, _ = self._get_task_and_project(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        task, _, membership = self._get_task_and_project(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner_or_creator = (
            request.user.is_staff
            or (membership and membership.role == ProjectMembership.OWNER)
            or task.created_by_id == request.user.pk
        )
        if not is_owner_or_creator:
            return Response({'error': 'Only the project owner or task creator can fully update this task.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        task, _, membership = self._get_task_and_project(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _can_write(membership, request.user):
            return Response({'error': 'Viewers cannot update tasks.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        task, _, membership = self._get_task_and_project(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_owner_or_creator = (
            request.user.is_staff
            or (membership and membership.role == ProjectMembership.OWNER)
            or task.created_by_id == request.user.pk
        )
        if not is_owner_or_creator:
            return Response({'error': 'Only the project owner or task creator can delete this task.'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectLabelListView(APIView):
    def get(self, request, pk):
        project, _ = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        labels = project.labels.all()
        return Response(LabelSerializer(labels, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        project, membership = get_accessible_project(pk, request.user)
        if project is None:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _can_write(membership, request.user):
            return Response({'error': 'Viewers cannot create labels.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LabelSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        label = serializer.save(project=project)
        return Response(LabelSerializer(label).data, status=status.HTTP_201_CREATED)


class LabelDetailView(APIView):
    def _get_label_and_project(self, label_pk, user):
        try:
            label = Label.objects.select_related('project').get(pk=label_pk)
        except Label.DoesNotExist:
            return None, None, None
        project, membership = get_accessible_project(label.project_id, user)
        if project is None:
            return None, None, None
        return label, project, membership

    def put(self, request, pk):
        label, _, membership = self._get_label_and_project(pk, request.user)
        if label is None:
            return Response({'error': 'Label not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _is_owner_role(membership, request.user):
            return Response({'error': 'Only the project owner can update labels.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = LabelSerializer(label, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        label, _, membership = self._get_label_and_project(pk, request.user)
        if label is None:
            return Response({'error': 'Label not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _is_owner_role(membership, request.user):
            return Response({'error': 'Only the project owner can delete labels.'}, status=status.HTTP_403_FORBIDDEN)
        label.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
