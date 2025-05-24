from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Task, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar']

class UserSerializer(serializers.ModelSerializer):
    avatar = UserProfileSerializer(required=False)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username',  'email', 'first_name', 'last_name', 'password', 'avatar']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        if hasattr(instance, 'profile'):
            ret['avatar'] = self.context['request'].build_absolute_uri(instance.profile.avatar.url) if instance.profile.avatar else None
        else:
            ret['avatar'] = None
            
        return ret

    def create(self, validated_data):
        request = self.context.get('request')
        avatar_file = request.FILES.get('avatar') if request else None
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        if avatar_file:
            UserProfile.objects.create(user=user, avatar=avatar_file)
        else:
            UserProfile.objects.create(user=user)
            
        return user
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        avatar_file = request.FILES.get('avatar') if request else None
        password = validated_data.pop('password')
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Update profile if provided
        if avatar_file:
            setattr(instance.profile, 'avatar', avatar_file)
            instance.profile.save()
            
        return instance

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'project', 'assigned_to']
        read_only_fields = ['created_at', 'updated_at']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.assigned_to:
            ret['assigned_to'] = instance.assigned_to.username
        if instance.project:
            ret['project'] = instance.project.name
        return ret


class ProjectSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'tasks']
        read_only_fields = ['created_at', 'updated_at']