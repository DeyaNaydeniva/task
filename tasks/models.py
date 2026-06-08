from django.db import models
from django.conf import settings
from projects.models import Project


class Label(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#7A9E87')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='labels')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    STATUS_CHOICES = [
        (TODO, 'To do'),
        (IN_PROGRESS, 'In progress'),
        (DONE, 'Done'),
    ]

    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TODO)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default=MEDIUM)
    due_date = models.DateField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_tasks',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks',
    )
    labels = models.ManyToManyField(Label, blank=True, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
