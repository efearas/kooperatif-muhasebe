from django import forms
#from .models import uretici,urun,Satis, SatisStokHareketleri,Gider, StokGirisi, VirmanVeDuzeltme, VirmanVeDuzeltmeHesaplari, BorcAlacak
from .models import *
from django.forms.models import inlineformset_factory
#import datetime
from datetime import datetime, date, timedelta
from django.forms import extras
#from django.contrib.admin.widgets import AdminDateWidget
#from django.forms.fields import DateField
from django.forms import ModelChoiceField

class UrunUreticiModelChoiceField(ModelChoiceField):
	def label_from_instance(self, obj):		
		return (obj.urun_adi + ' :: '+ obj.uretici.uretici_adi)

class UrunForm(forms.ModelForm):

    class Meta:
        model = urun
        fields = ('urun_adi', 'uretici','birim', 'kdv_kategorisi','dayanisma_urunu','urun_kategorisi')

class GiderForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)	
	notlar = forms.CharField( widget=forms.Textarea )
	class Meta:
		model = Gider
		fields = ('tarih', 'gider_tipi','tutar','notlar','odeme_araci')

class StokGirisiForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)		
	notlar = forms.CharField( widget=forms.Textarea, required=False )
	urun = forms.ModelChoiceField(queryset=urun.objects.order_by('urun_adi'), required=True)	
	agirlik = forms.DecimalField(required=False)
	class Meta:
		model = StokGirisi
		fields = ('tarih', 'urun','miktar','notlar','agirlik','stok_hareketi_tipi')


		
class UreticiForm(forms.ModelForm):	
    class Meta:
        model = uretici
        fields = ('uretici_adi', 'adres', 'banka_bilgileri')

class KisiForm(forms.ModelForm):	
    class Meta:
        model = kisi
        fields = ('kisi_adi', 'notlar',)


class SatisForm(forms.ModelForm):	
	tarih = forms.DateTimeField(initial=datetime.now)	
	class Meta:
		model = Satis		
		exclude = {'kullanici'}

class BorcAlacakForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)
	class Meta:
		model = BorcAlacak
		exclude= {'kullanici','dis_sistem_tipi','dis_sistem_id','borcmu_alacakmi'}

class KisiOdemeTahsilatForm(forms.ModelForm):
	tarih = forms.DateTimeField(initial=datetime.now)
	class Meta:
		model = KisiOdemeTahsilat
		exclude= {'kullanici',}
		
		
class VirmanForm(forms.ModelForm):	
	tarih = forms.DateTimeField(initial=datetime.now)
	giris_hesabi = forms.ChoiceField(choices= HESAP_CHOICES)
	cikis_hesabi = forms.ChoiceField(choices= HESAP_CHOICES)
	class Meta:
		model = VirmanVeDuzeltme				
		exclude = {'kullanici'}

class SatisStokHareketleriForm(forms.ModelForm):
	urun = UrunUreticiModelChoiceField(queryset=urun.objects.order_by('urun_adi'), required=True)	
	#urun = forms.ModelChoiceField(queryset=urun.objects.order_by('urun_adi'), required=True)	
	#tutar = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'})
	class Meta:
		model = SatisStokHareketleri		
		exclude = {}

class RaporTarihForm(forms.Form):
	baslangicTarihi = forms.DateField(initial=datetime.today)
	bitisTarihi = forms.DateField(initial=datetime.today)
	
	
		
