from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm, SetPasswordForm, AddEmailForm, \
    ResetPasswordForm, ResetPasswordKeyForm
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


class CustomChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()


class CustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super(CustomAddEmailForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super(CustomResetPasswordKeyForm, self).__init__(*args, **kwargs)
        self.fields['captcha'] = ReCaptchaField()
