from user import models
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = '添加超级管理员等基础用户信息'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument("password", type=str)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']

        try:
            user = models.User.objects.get(username=username)
        except Exception as e:
            user = models.User(username=username, password=password)
            user.save()
        try:
            role = models.Role.objects.get(name="超级管理员")
        except Exception as e:
            role = models.Role(name="超级管理员")
            role.save()

        try:
            group = models.Group.objects.get(name="超级部门")
        except Exception as e:
            group = models.Group(name="超级部门")
            group.save()
        for v in models.Permission.permission_choices.values():
            try:
                permission = models.Permission.objects.get(name=v[0], codename=v[1])
            except Exception as e:
                permission = models.Permission(name=v[0], codename=v[1])
                permission.save()
            role.permissions.add(permission)
            group.permissions.add(permission)

        role.save()
        group.save()

        user.role.add(role)
        user.groups.add(group)

        user.save()
        self.stdout.write(self.style.SUCCESS('基础信息创建成功'))
