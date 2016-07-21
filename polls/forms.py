from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u'用户名',
        error_messages={'required': '请输入用户名'},
        widget=forms.TextInput(
            attrs={
                'placeholder': u'用户名',
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u'密码',
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u'密码',
            }
        ),
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u'用户名和密码为必填项')
        else:
            cleaned_data = super(LoginForm, self).clean()


class SignupForm(forms.Form):
    username = forms.CharField(
        required=True,
        label=u'用户名',
        error_messages={'required': '请输入用户名'},
        widget=forms.TextInput(
            attrs={
                'placeholder': u'用户名',
            }
        ),
    )
    password = forms.CharField(
        required=True,
        label=u'密码',
        error_messages={'required': u'请输入密码'},
        widget=forms.PasswordInput(
            attrs={
                'placeholder': u'密码',
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label=u'邮箱',
        error_messages={'required': u'请输入邮箱'},
        widget=forms.EmailInput(
            attrs={
                'placeholder': u'hahu@hahu.com'
            }
        )
    )

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u'用户名、密码和邮箱为必填项')
        else:
            cleaned_data = super(SignupForm, self).clean()
