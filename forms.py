from django import forms
from .models import uretici,urun,Satis, SatisStokHareketleri,Gider, StokGirisi, VirmanVeDuzeltme, VirmanVeDuzeltmeHesaplari
from django.forms.models import inlineformset_factory
#import datetime
from datetime import datetime, date, timedelta
from django.forms import extras
#from django.contrib.admin.widgets import AdminDateWidget
#from django.forms.fields import DateField

class UrunForm(forms.ModelForm):	
    class Meta:
        model = urun
        fields = ('urun_adi', 'uretici','musteri_fiyati','birim')

class GiderForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)	
	notlar = forms.CharField( widget=forms.Textarea )
	class Meta:
		model = Gider
		fields = ('tarih', 'gider_tipi','tutar','notlar')

class StokGirisiForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)		
	notlar = forms.CharField( widget=forms.Textarea )
	class Meta:
		model = StokGirisi
		fields = ('tarih', 'urun','miktar','notlar')


		
class UreticiForm(forms.ModelForm):	
    class Meta:
        model = uretici
        fields = ('uretici_adi', 'adres', 'banka_bilgileri')

class SatisForm(forms.ModelForm):	
	tarih = forms.DateTimeField(initial=datetime.now)	
	class Meta:
		model = Satis		
		exclude = {}

		
		
class VirmanForm(forms.ModelForm):	
	tarih = forms.DateTimeField(initial=datetime.now)	
	cikis_hesabi = forms.ModelChoiceField(queryset=VirmanVeDuzeltmeHesaplari.objects.all(),required=False)
	giris_hesabi = forms.ModelChoiceField(queryset=VirmanVeDuzeltmeHesaplari.objects.all(),required=False)
	class Meta:
		model = VirmanVeDuzeltme				
		exclude = {'kullanici'}

class SatisStokHareketleriForm(forms.ModelForm):
	urun = forms.ModelChoiceField(queryset=urun.objects.order_by('urun_adi'), required=True)	
	tutar = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'})
)
	class Meta:
		model = SatisStokHareketleri		
		exclude = {}

class RaporTarihForm(forms.Form):
	baslangicTarihi = forms.DateField(widget=extras.SelectDateWidget,initial=datetime.today)
	bitisTarihi = forms.DateField(widget=extras.SelectDateWidget,initial=datetime.today)
	
	
		
