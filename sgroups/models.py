from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#status: 0,1 : private, public ; for both groups and posts

class MyUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(unique=True, max_length=500)
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=13)
    userid = models.AutoField(primary_key=True)

    class Meta:
        ordering = ['email']

    def __str__(self):
        return "user {} is {} ".format(self.name,self.userid)

class MyGroup(models.Model):
    name = models.CharField(max_length = 100)
    size = models.IntegerField(default=1)
    groupid = models.AutoField(primary_key = True)
    users = models.ManyToManyField(MyUser)
    status = models.IntegerField(default = 1)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "group {} is {}".format(self.name, self.groupid)


class Post(models.Model):
        content = models.TextField()
        createdon = models.DateTimeField(auto_now_add = True)
        user = models.ForeignKey(to = MyUser, on_delete = models.CASCADE)
        group = models.ForeignKey(to = MyGroup, on_delete = models.CASCADE)
        status = models.IntegerField(default=0)
        postid = models.AutoField(primary_key=True)

        class Meta:
            ordering = ['content','createdon']

        def __str__(self):
            return "Post {} is {}".format(self.content,self.postid)

class Permissions(models.Model):
    role = models.IntegerField()
    groups = models.ForeignKey(to = MyGroup, on_delete = models.CASCADE)
    users = models.ForeignKey(to = MyUser, on_delete = models.CASCADE)