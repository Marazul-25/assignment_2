from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from events.forms import StyledFormMixin
from django.contrib.auth.forms import AuthenticationForm


class Registerform(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name',
                  'password1','password2','email']


    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        for fieldname in ['username','password1','password2']:
            self.fields[fieldname].help_text = None

class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)