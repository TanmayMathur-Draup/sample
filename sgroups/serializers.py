from rest_framework import serializers
from .models import MyUser, MyGroup, Post, Permissions


# Create your serializers here

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ('name', 'email',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyGroup
        fields = ('name', 'users', 'size',)


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ('user', 'group', 'content', 'postid', 'createdon',)


class UserSerializer_custom(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MyUser
        fields = ('name',)


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permissions
        fields = ('users', 'groups', 'role')

