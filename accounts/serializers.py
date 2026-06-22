from django.contrib.auth.models import User
from rest_framework import serializers


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1)
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']
