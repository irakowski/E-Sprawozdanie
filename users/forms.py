#from django import forms
#from django.core.exceptions import ValidationError
#from django.utils.translation import gettext_lazy as _
#
#from .models import AppUser
#
#
#class AppUserCreationForm(forms.ModelForm):
#    """
#    A form for creating users. Includes email + repeated passwords
#    Does not include first_name and last_name fields
#    """
#    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput(attrs=
#                {'placeholder': 'Password'}))
#    password2 = forms.CharField(label=_('Confirm Password'), widget=forms.PasswordInput(attrs=
#                {'placeholder': 'Confirm Password'}))
#    
#    class Meta:
#        model = CustomUser
#        widgets = {
#            'email': forms.TextInput(attrs={'placeholder': 'Email'})
#        }
#        fields = ('email',)
#
#    def clean_password2(self):
#        #confirm both passwords match 
#        password1 = self.cleaned_data.get('password1')
#        password2 = self.cleaned_data.get('password2')
#        if password1 and password2 and password1 != password2:
#            raise ValidationError('Passwords don\'t match')
#        return password2
#    
#    def save(self, commit=True):
#        #save hashed password
#        user = super().save(commit=False)
#        user.set_password(self.cleaned_data['password1'])
#        if commit:
#            user.save()
#        return user