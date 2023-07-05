from django.contrib.auth.forms import UserCreationForm
from users.models import User


class SignupForm(UserCreationForm):
    # email = forms.EmailField(max_length=200, help_text='Required')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'user_type', 'referral', 'password1', 'password2')

