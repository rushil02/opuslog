from allauth.account.forms import LoginForm, SignupForm
from captcha.fields import ReCaptchaField


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        captcha_flag = kwargs.pop('captcha_flag', True)
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        if captcha_flag:
            self.fields['captcha'] = ReCaptchaField()


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()
