from django.contrib.auth.models import User
from rest_framework import serializers
from ..models import UserProfile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    level = serializers.IntegerField(write_only=True, default=1)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'level']

    def create(self, validated_data):
        level = validated_data.pop('level', 1)
        user = User.objects.create_user(**validated_data)
        user.profile.level = level
        user.profile.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(source='profile.level', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'level']