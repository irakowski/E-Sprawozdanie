from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponse
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

    def form_valid(self, form):
        file_in_memory = form.cleaned_data     
        xml_text = forms.handle_upload(file_in_memory)
        data = parse_txt(xml_text)
        return render(self.request, 'esfviewer/output.html', 
                {"data": data, "desc" : description_dict, 'rzis':rzis, 'zmiany': zmiany, 'rachunek': rachunek})
