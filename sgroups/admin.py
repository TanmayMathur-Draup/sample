from django.contrib import admin
from .models import MyUser,MyGroup,Post, Permissions
# Register your models here.
admin.site.register(MyUser)
admin.site.register(Post)
admin.site.register(MyGroup)
admin.site.register(Permissions)