from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Project, ProjectMembership
from tasks.models import Task, Label

User = get_user_model()


@login_required
def dashboard(request):
    projects = Project.objects.filter(owner=request.user)
    return render(request, 'projects/dashboard.html', {'projects': projects})


@login_required
def create_project(request):
    if request.method != 'POST':
        return redirect('projects:dashboard')

    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()

    if name:
        Project.objects.create(name=name, description=description, owner=request.user)

    return redirect('projects:dashboard')


@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    is_owner = project.owner == request.user
    is_member = ProjectMembership.objects.filter(project=project, user=request.user).exists()

    if not is_owner and not is_member:
        return HttpResponseForbidden('You do not have access to this project.')

    tasks = Task.objects.filter(project=project).select_related('assignee')
    memberships = ProjectMembership.objects.filter(project=project).select_related('user')

    member_users = [project.owner] + [m.user for m in memberships if m.user != project.owner]

    labels = Label.objects.filter(project=project)

    context = {
        'project': project,
        'tasks': tasks,
        'memberships': memberships,
        'member_users': member_users,
        'task_status_choices': Task.STATUS_CHOICES,
        'task_priority_choices': Task.PRIORITY_CHOICES,
        'today': timezone.now().date(),
        'labels': labels,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def add_task(request, pk):
    project = get_object_or_404(Project, pk=pk)

    is_owner = project.owner == request.user
    is_member = ProjectMembership.objects.filter(project=project, user=request.user).exists()

    if not is_owner and not is_member:
        return HttpResponseForbidden()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        if title:
            assignee_id = request.POST.get('assignee') or None
            assignee = User.objects.filter(pk=assignee_id).first() if assignee_id else None
            due_date = request.POST.get('due_date') or None

            Task.objects.create(
                title=title,
                description=request.POST.get('description', '').strip(),
                status=request.POST.get('status', Task.TODO),
                priority=request.POST.get('priority', Task.MEDIUM),
                due_date=due_date,
                project=project,
                assignee=assignee,
                created_by=request.user,
            )

    return redirect('projects:project_detail', pk=pk)
