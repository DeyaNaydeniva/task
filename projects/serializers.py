from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Project, ProjectMembership


class ProjectSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class MembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ['id', 'user', 'user_id', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']

    def get_user(self, obj):
        return {
            'id': obj.user.pk,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }

    def validate_user_id(self, value):
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError('User not found.')
        return value


class MembershipRolePatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMembership
        fields = ['role']
