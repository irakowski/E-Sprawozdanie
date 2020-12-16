from django.shortcuts import render, redirect
from django.contrib import messages

from django.urls import reverse_lazy, reverse
from django.views import generic
from django.http import HttpResponse, HttpResponseRedirect
from . import forms
import xml.etree.ElementTree as ET
import xmlschema
from .xml_parse import parse_txt
from .desc import description_dict, rzis, zmiany, rachunek


class LandingPage(generic.TemplateView):
    template_name = 'esfviewer/index.html'


class UploadView(generic.TemplateView):
    template_name = 'esfviewer/upload_form.html'
    extra_context = {'form': forms.UploadFinancialStatementForm }


class ReportView(generic.FormView):
    form_class = forms.UploadFinancialStatementForm
    template_name = 'esfviewer/output.html'

    
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        messages.add_message(self.request, messages.ERROR, form.errors['file'])
        return HttpResponseRedirect(reverse('esfviewer:upload'))
    
    def form_valid(self, form):
        file_in_memory = form.cleaned_data
        #print(file_in_memory)  
        xml_text = forms.handle_upload(file_in_memory)
        data = parse_txt(xml_text)
        return render(self.request, 'esfviewer/output.html', 
                {"data": data, "desc" : description_dict, 'rzis':rzis, 'zmiany': zmiany, 'rachunek': rachunek})
    
    