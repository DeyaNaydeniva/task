from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Task, Label
from projects.models import Project, ProjectMembership
from comments.models import Comment

User = get_user_model()


def _has_project_access(user, project):
    return (
        project.owner == user
        or ProjectMembership.objects.filter(project=project, user=user).exists()
    )


@login_required
def task_detail(request, pk):
    task = get_object_or_404(
        Task.objects.select_related('project', 'assignee', 'created_by'), pk=pk
    )
    project = task.project

    if not _has_project_access(request.user, project):
        return HttpResponseForbidden('You do not have access to this task.')

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Comment.objects.create(task=task, author=request.user, body=body)
        return redirect('tasks:task_detail', pk=pk)

    comments = Comment.objects.filter(task=task).select_related('author')
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')
    member_users = [project.owner] + [m.user for m in memberships if m.user != project.owner]

    task_labels = task.labels.all()
    available_labels = Label.objects.filter(project=project).exclude(
        pk__in=task_labels.values_list('pk', flat=True)
    )

    context = {
        'task': task,
        'project': project,
        'comments': comments,
        'member_users': member_users,
        'task_status_choices': Task.STATUS_CHOICES,
        'task_priority_choices': Task.PRIORITY_CHOICES,
        'today': timezone.now().date(),
        'can_delete': project.owner == request.user or task.created_by == request.user,
        'task_labels': task_labels,
        'available_labels': available_labels,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not _has_project_access(request.user, task.project):
        return HttpResponseForbidden()

    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        valid_statuses = [s for s, _ in Task.STATUS_CHOICES]
        if new_status in valid_statuses:
            task.status = new_status
            task.save(update_fields=['status', 'updated_at'])

    return redirect('tasks:task_detail', pk=pk)


@login_required
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not _has_project_access(request.user, task.project):
        return HttpResponseForbidden()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            assignee_id = request.POST.get('assignee') or None
            assignee = User.objects.filter(pk=assignee_id).first() if assignee_id else None
            task.title = title
            task.description = request.POST.get('description', '').strip()
            task.priority = request.POST.get('priority', task.priority)
            task.due_date = request.POST.get('due_date') or None
            task.assignee = assignee
            task.save(update_fields=['title', 'description', 'priority', 'due_date', 'assignee', 'updated_at'])

    return redirect('tasks:task_detail', pk=pk)


@login_required
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = task.project

    if not (project.owner == request.user or task.created_by == request.user):
        return HttpResponseForbidden()

    if request.method == 'POST':
        task.delete()
        return redirect('projects:project_detail', pk=project.pk)

    return redirect('tasks:task_detail', pk=pk)


@login_required
def create_label(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if not _has_project_access(request.user, project):
        return HttpResponseForbidden()

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#7A9E87').strip()
        if name:
            Label.objects.create(name=name, color=color, project=project)

    return redirect('projects:project_detail', pk=pk)


@login_required
def delete_label(request, pk):
    label = get_object_or_404(Label, pk=pk)
    project = label.project

    if project.owner != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        project_pk = project.pk
        label.delete()
        return redirect('projects:project_detail', pk=project_pk)

    return redirect('projects:project_detail', pk=project.pk)


@login_required
def toggle_task_label(request, pk, label_pk):
    task = get_object_or_404(Task, pk=pk)

    if not _has_project_access(request.user, task.project):
        return HttpResponseForbidden()

    if request.method == 'POST':
        label = get_object_or_404(Label, pk=label_pk, project=task.project)
        if task.labels.filter(pk=label.pk).exists():
            task.labels.remove(label)
        else:
            task.labels.add(label)

    return redirect('tasks:task_detail', pk=pk)
