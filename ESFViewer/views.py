from django.shortcuts import render
from django.views import generic
from . import forms
# Create your views here.
class LandingPage(generic.TemplateView):
    template_name = 'esfviewer/index.html'

class FormView(generic.FormView):
    form_class = forms.UploadFinancialStatementForm
    template_name = 'esfviewer/upload_form.html'