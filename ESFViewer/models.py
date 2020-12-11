from django.db import models
from django.utils.translation import gettext_lazy as _

class FileUploads(models.Model):
    file = models.FileField(upload_to='uploads/')


class Report(models.Model):
    
    class CalculationMethod(models.TextChoices):
        COMPARISON = 'COMP', _('Porównawcza')
        CALCULATION = 'CALC', ('Kalkulacyjny')

    wariant_sprawozdania = models.CharField(
        max_length=4, 
        choices=CalculationMethod.choices,
        default=CalculationMethod.COMPARISON
    )

    podmiot_sprawozdania = models.CharField(max_length=128)
    numer_identyfikacyjny = models.CharField(max_length=20)
    marza_operacyjna = models.FloatField()
    marza_zysku_brutto = models.FloatField()
    rentownosc_aktywow = models.FloatField()
    rentownosc_kapitalu_wlasnego = models.FloatField()
