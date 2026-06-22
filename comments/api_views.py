from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import ProjectMembership
from projects.api_views import get_accessible_project
from tasks.models import Task
from .models import Comment
from .serializers import CommentSerializer


def _can_write(membership, user):
    if user.is_staff:
        return True
    return membership is not None and membership.role in (
        ProjectMembership.OWNER, ProjectMembership.MEMBER
    )


class TaskCommentListView(APIView):
    def _get_task(self, task_pk, user):
        try:
            task = Task.objects.select_related('project').get(pk=task_pk)
        except Task.DoesNotExist:
            return None, None, None
        project, membership = get_accessible_project(task.project_id, user)
        if project is None:
            return None, None, None
        return task, project, membership

    def get(self, request, pk):
        task, _, _ = self._get_task(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        comments = task.comments.select_related('author').all()
        return Response(CommentSerializer(comments, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        task, _, membership = self._get_task(pk, request.user)
        if task is None:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not _can_write(membership, request.user):
            return Response({'error': 'Viewers cannot post comments.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        comment = serializer.save(task=task, author=request.user)
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CommentDetailView(APIView):
    def _get_comment(self, comment_pk, user):
        try:
            comment = Comment.objects.select_related('task__project', 'author').get(pk=comment_pk)
        except Comment.DoesNotExist:
            return None, None, None
        project, membership = get_accessible_project(comment.task.project_id, user)
        if project is None:
            return None, None, None
        return comment, project, membership

    def patch(self, request, pk):
        comment, _, membership = self._get_comment(pk, request.user)
        if comment is None:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_author = comment.author_id == request.user.pk
        if not is_author and not request.user.is_staff:
            return Response({'error': 'Only the comment author can edit this comment.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(CommentSerializer(comment).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        comment, _, membership = self._get_comment(pk, request.user)
        if comment is None:
            return Response({'error': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_author = comment.author_id == request.user.pk
        is_project_owner = request.user.is_staff or (
            membership and membership.role == ProjectMembership.OWNER
        )
        if not is_author and not is_project_owner:
            return Response({'error': 'Only the comment author or project owner can delete this comment.'}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
