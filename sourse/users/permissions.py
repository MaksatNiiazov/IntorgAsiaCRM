from django.contrib.auth.mixins import UserPassesTestMixin

from users.models import UserType


class WorkerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == UserType.WORKER


class ClientRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == UserType.CLIENT
    

class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == UserType.MANAGER


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.user_type == UserType.ADMIN
