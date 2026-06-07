from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Project


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
