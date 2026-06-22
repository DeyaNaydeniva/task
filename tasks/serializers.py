from rest_framework import serializers
from .models import Task, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'color', 'project']
        read_only_fields = ['id', 'project']


class TaskSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        queryset=Label.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='labels',
    )

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'due_date', 'project', 'assignee', 'created_by',
            'labels', 'label_ids', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'project', 'created_by', 'created_at', 'updated_at']
