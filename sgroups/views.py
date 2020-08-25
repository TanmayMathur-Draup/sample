from .serializers import UserSerializer, GroupSerializer, PostSerializer, UserSerializer_custom, PermissionSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import MyUser, MyGroup, Post, Permissions
from rest_framework import viewsets
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django import forms


# from django.contrib.auth.models import User,Group
# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = MyGroup.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status=1)  # 1 are approved by admins
    serializer_class = PostSerializer


class UsersList(APIView):

    def get(self, request, name):
        group_passed = MyGroup.objects.filter(name=name)[0]
        queryset = group_passed.users.all()
        serializer = UserSerializer_custom(queryset, many=True)
        lst = ["group_" + name + ": "]
        lst.append("[")
        for en in list(serializer.data):
            s = str(en.values()).split('[')[1]
            s = s.split(']')[0]
            lst.append(s + ",")
        lst.append("]")
        string = ""
        for en in lst:
            string += en
        return Response(string)

    def post(self, request):
        pass


class AddMembers(APIView):

    def get(self, request, grp_name, name, role):
        group_passed = MyGroup.objects.filter(name=grp_name)[0]
        user_passed = MyUser.objects.filter(name=name)[0]
        group_passed.users.add(user_passed)
        permission_required = Permissions.objects.create(groups = group_passed, users = user_passed, role=role)
        group_passed.save()
        permission_required.save()
        return redirect('/')

    def post(self, request):
        pass


class ChangePermissions(APIView):

    def get(self, request, grp_name, name, role):
        group_passed = MyGroup.objects.filter(name = grp_name)[0]
        user_passed = MyUser.objects.filter(name = name)[0]
        user_requester = MyUser.objects.filter(email = request.user.username)[0]
        permissions_requester = (Permissions.objects.filter(users =user_requester, groups = group_passed)[0]).role
        if permissions_requester > 0:
            return redirect('/')
        permissions_requested = (Permissions.objects.filter(users = user_passed, groups = group_passed)[0])
        permissions_requested.role = role
        permissions_requested.save()

        return Response(
            "new role for"+
            name+
            "is"
            (permissions_requested).role)

    def post(self, request):
        pass


class GroupsList(APIView):

    def get(self, request, name):
        user_passed = MyUser.objects.filter(name=name)[0]
        queryset = user_passed.mygroup_set.all()
        serializer = GroupSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        pass


def index(request):
    return render(request, '/')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            name = str(username).split('@')[0]
            user = authenticate(username=username, password=password, name = name )
            new_user = MyUser.objects.create(user=user, email=username, number=0)
            new_user.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.htm', context)

class changename(APIView):

    def get(self, request, name):
        user = MyUser.objects.filter(email = request.user.username)[0]
        user.name = name
        user.save()
        return Response(UserSerializer(user).data)

    def post(self, request):
        pass

class group_add(APIView):

    def get(self, request, grp_name, admin_name):
        name = grp_name
        new_group = MyGroup.objects.create(name=grp_name)
        user = MyUser.objects.filter(name=admin_name)[0]
        new_group.users.add(user)
        new_group.save()
        permission_required = Permissions.objects.create(role=-1, groups=new_group, users=user)
        permission_required.save()
        return Response('created succesfully')

    def post(self, request):
        pass


class dataForm(forms.Form):
    content = forms.CharField(widget = forms.Textarea)
    grp_name = forms.CharField(max_length = 100)


class AddPost(APIView):

    def get(self, request, grp_name, content):
        user = MyUser.objects.filter(email = request.user.username)[0]
        group = MyGroup.objects.filter(name = grp_name)[0]
        permission = Permissions.objects.filter(users = user, groups = group)[0]

        if permission.role < 2:  #since no role>1 exists in Permissions, this checks out for all group members
            p = Post.objects.create(content = content, user = user, group =group)
            p.save()
            return Response(p.content +"id "+ p.id)

        return Response("You don't have access to this group")

    def post(self, request):
        pass

class CheckAll(APIView):

    def get(self, request, grp_name):

        queryset = []
        user = MyUser.objects.filter(email = request.user.username)[0]
        group = MyGroup.objects.filter(name = grp_name)[0]
        queryset = Post.objects.filter(group = group, status = 0)
        serializer = PostSerializer(queryset, many = True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):

        pass


class Moderate(APIView):

    def get(self, request, grp_name, postid):
        post = Post.objects.filter(postid = postid)[0]
        group = MyGroup.objects.filter(name = grp_name)[0]
        user = MyUser.objects.filter(email = request.user.username)[0]
        permission = Permissions.objects.filter(users = user, groups = group)[0].role
        if permission < 1:
            post.status = 1
            post.save()
            queryset = Post.objects.filter(group = group, status = 1)
            serializer = PostSerializer(queryset, many = True, context={'request': request})
            return Response(
                str(serializer.data) +
                "this is the new set of public posts")

        return Response('you can just check Posts and that will be it for you in this group')

    def post(self, request):
        pass


class Delete(APIView):


    def get(self, request, grp_name, postid):

        post = Post.objects.filter(postid = postid)[0]
        group = MyGroup.objects.filter(name = grp_name)[0]
        user = MyUser.objects.filter(email = request.user.username)[0]
        permission = Permissions.objects.filter(users = user, groups = group)[0].role

        if permission < 1:
            Post.objects.filter(postid=postid).delete()
            queryset = Post.objects.filter(group = group, status=1)
            serializer = PostSerializer(queryset, many = True, context={'request': request})
            return Response(
                str(serializer.data) +
                "this is the new set of public posts")

        return Response('you can just check/create/edit public Posts and that will be it for you in this group')

    def post(self, request):
        pass


class EditPost(APIView):


    def get(self, request, postid, new_content):

        post = Post.objects.filter(postid = postid)[0]

        if post.user.email != request.user.username:
            return Response('you are not the auhor of the said post')

        post.content = new_content
        post.save()

        return Response(PostSerializer(post,context={'request': request}).data)

    def post(self, request):

        pass

class BanMember(APIView):


    def get(self, request, grp_name, member_name):

        requester = MyUser.objects.filter(email = request.user.username)[0]
        group = MyGroup.objects.filter(name = grp_name)[0]
        member = MyUser.objects.filter(name = member_name)[0]
        permission = Permissions.objects.filter(groups = group, users = requester)[0]
        if permission.role<0:
            group.users.remove(member)
            group.save()
            Permissions.objects.filter(groups = group, users = member).delete()
        return Response(str(group.users.all()))

    def post(self, request):

        pass



