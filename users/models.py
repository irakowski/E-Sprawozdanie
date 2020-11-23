from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from esprawozdanie import settings
from django.template.defaultfilters import slugify
import re
from .managers import CustomUserManager


class AppUser(AbstractBaseUser,PermissionsMixin):
    """
    Custom User Model. 
    Required fields: Email
    """
    first_name = models.CharField(_('First Name'), max_length=150, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=150, blank=True)
    email = models.EmailField(_('Email address'), max_length=250, unique=True,
        error_messages={
            'unique':_('User with such email already exists.')
        })
    is_staff = models.BooleanField(_('Staff Status'), default=False, help_text=
        _('Designates whether user can log in into admin site'))
    is_active = models.BooleanField(_('Active'), default=True, help_text=
        _('Designates whether user should be treated as active.'
          'Unselect instead of deleting account.'))
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
      
    def get_full_name(self):
        """Return user's full name separated by space"""
        return f'{self.first_name} {self.last_name}'

    def short_name(self):
        """Short name for the user"""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send email to the user"""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

