import xml.etree.ElementTree as ET
import xmlschema
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.views import generic
from . import forms
from .xml_parse import parse_txt
from . import element_mappings
from esprawozdanie.settings import STATIC_ROOT

class LandingPage(generic.TemplateView):
    """Basic landing page providing link to file upload"""
    template_name = 'esfviewer/index.html'


class UploadView(generic.TemplateView):
    """View displaying form for file upload"""
    template_name = 'esfviewer/upload_form.html'
    extra_context = {'form': forms.UploadFinancialStatementForm }


class ReportView(generic.FormView):
    """View handling form submittion"""
    form_class = forms.UploadFinancialStatementForm
    template_name = 'esfviewer/output.html'
    
    def form_invalid(self, form):
        """If the form is invalid, redirect to Upload View with Error."""
        messages.add_message(self.request, messages.ERROR, form.errors['file'])
        return HttpResponseRedirect(reverse('esfviewer:upload'))
    
    def form_valid(self, form):
        """If the form is valid, parse file content and display on the page"""
        file_in_memory = form.cleaned_data 
        xml_text = forms.handle_upload(file_in_memory)
        data = parse_txt(xml_text)
        return render(self.request, 'esfviewer/output.html', {'data': data})

def my_500_view(request):
    context = {}
    response = render(request, "esfviewer/errors/500.html", context=context)
    response.status_code = 500
    return response
    