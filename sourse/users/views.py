from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views import View
from users.forms import SignupForm
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from users.models import User
from users.token import account_activation_token


class RegisterView(View):
    def get(self, request):
        context = {
            'form': SignupForm,
            'referrals': User.objects.all()
        }
        return render(request, 'registration/registration.html', context)

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, 'Клиент создан')
            return redirect('acceptance')
        else:
            print(form.errors)
            context = {
                'form': SignupForm,
                'referrals': User.objects.all(),
                'errors': form.errors,
            }
        return render(request, 'registration/registration.html', context)

class RegisterWorkerView(View):

    def get(self, request):
        context = {
            'form': SignupForm,
            'referrals': User.objects.all()
        }
        return render(request, 'registration/registration_worker.html', context)

    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()

            return redirect('dashboard')
        else:
            print(form.errors)
            context = {
                'form': SignupForm,
                'referrals': User.objects.all(),
                'errors': form.errors,
            }

        return render(request, 'registration/registration_worker.html', context)


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, "registration/thank_you_for_activation.html")
    else:
        return HttpResponse('Activation link is invalid!')



