	# -*- coding: utf-8 -*-

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import urun,uretici,Satis,SatisStokHareketleri,Gider,StokGirisi,VirmanVeDuzeltme,BorcAlacak
from .forms import UreticiForm,UrunForm, SatisForm, SatisStokHareketleriForm, GiderForm, StokGirisiForm, VirmanForm, RaporTarihForm, BorcAlacakForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.forms.models import inlineformset_factory
from django.db.models import Sum
from django.contrib.auth.decorators import permission_required
from .reporting import *
import pdb
import datetime as dt     
from django.contrib.auth.models import User
from django.core.mail import send_mail
from .util import  *


def test(request):
	#email = EmailMessage('Subject 2', 'Body 123', to=['arasefe@gmail.com'])
	send_mail('Subject here', 'Here is the message.', 'muhasebe@kadikoykoop.org', ['arasefe@gmail.com'], fail_silently=False)
	#email.send()
	return render(request, 'koopmuhasebe/test.html')

###RAPORLAR
#test2

@login_required
def rapor_stok(request):	
	headers = ['Ürün ID','Ürün','Stokta Kalan Miktar','Birim Fiyat', 'Toplam Değer']
	tuple = rapor_stok_durumu()	
	context = {
	'rows': tuple[0],
	'headers': headers,
	'title_of_list':'Stok Durumu',
	'yekun' : tuple[1],	
	'edit_adresi':'rapor_satis_haftalik/',
	}
	return render(request, 'koopmuhasebe/main-body-rapor.html',context)

@login_required
def rapor_satis_aylik(request):
	tuple = rapor_aylik_urun_satis()
	#headers = []
	#for h in tuple[1]:
	#	headers.append(h)
	context = {
		'rows': tuple[0],
		'headers': tuple[1],
		'title_of_list': 'Aylık Ürün Satış Miktarı',
	}


	return render(request, 'koopmuhasebe/main-body-rapor.html',context)

@login_required
def rapor_uretici_borc(request):
	headers = ['Üretici', 'Borç', ]
	rows = rapor_uretici_borclari()
	context = {
		'rows': rows,
		'headers': headers,
		'title_of_list': 'Üreticilere Borçlarımız',
	}


	return render(request, 'koopmuhasebe/main-body-rapor.html',context)



@login_required
def rapor_satis_haftalik(request,pk):
	headers = ['Yıl','Hafta','Miktar', ]
	tuple = rapor_urun_satis_haftalik(pk)	
	context = {
	'rows': tuple[0],
	'headers': headers,
	'title_of_list':'Haftalık Satış Miktarı',
	'yekun' : tuple[1],	
	}
	return render(request, 'koopmuhasebe/main-body-rapor.html',context)

@login_required
def rapor_ciro(request):
	
	rows=''
	form = RaporTarihForm()
	#pdb.set_trace()
	if request.method == "POST":
			form = RaporTarihForm(request.POST)
			if form.is_valid():
				cd = form.cleaned_data #a = cd.get('a')
				baslangicTarihi = cd.get('baslangicTarihi')
				bitisTarihi = cd.get('bitisTarihi')
				#pdb.set_trace()
				rows = rapor_ciro_durumu(baslangicTarihi, bitisTarihi)	
								
	else:
		rows = rapor_ciro_durumu(dt.datetime.today().strftime("%Y-%m-%d"), dt.datetime.today().strftime("%Y-%m-%d"))	
	#rows = rapor_stok_durumu()	
	headers = ['Tarih','Ciro',]	
	context = {'rows': rows, 
	'headers': headers,
	'title_of_list':'Ciro',		
	'action':'rapor_ciro',
	'form': form,
	}
	return render(request, 'koopmuhasebe/main-body-rapor-tarihli.html',context)
	


###Virman Ve Düzeltme
@login_required
def virman_yeni(request):
	if request.method == "POST":
		form = VirmanForm(request.POST)
		if form.is_valid():
			virmanObj = form.save(commit=False)
			virmanObj.kullanici = request.user			
			virmanObj.save()
			return redirect('/koopmuhasebe/virman_liste')
	else:
		form = VirmanForm()
	
	
	return render(request, 'koopmuhasebe/domain/main-body-form-virman.html', {'form': form,})

@login_required
def virman_liste(request):
	virman_listesi = VirmanVeDuzeltme.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Çıkış Hesabı' ,'Giriş Hesabı', 'Tutar', 'Kullanıcı',]
	rows = []
	for p in virman_listesi:		
		rows.append([p.id,p.tarih,p.cikis_hesabi,p.giris_hesabi,p.tutar, p.kullanici,])
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Virman ve Düzeltmeler',
	'form_adresi':'virman_yeni',
	'edit_adresi':'virman/edit/',	
	'yeni_buton_adi':'Yeni Virman veya Düzeltme Girişi'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

@login_required
def virman_edit(request,pk):
	virmanObj = get_object_or_404(VirmanVeDuzeltme, pk=pk)
	if request.method == "POST":
		form = VirmanForm(request.POST,instance=virmanObj)
		if form.is_valid():
			virmanObj = form.save(commit=False)			
			virmanObj.kullanici = request.user			
			form.save()
			return redirect('/koopmuhasebe/virman_liste',pk=virmanObj.pk)
	else:
		form = VirmanForm(instance=virmanObj)
	
	
	return render(request, 'koopmuhasebe/domain/main-body-form-virman.html', {'form': form,})

#BORC ALACAK
@login_required
def borc_alacak_liste(request):
	borc_alacak_listesi = BorcAlacak.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Üretici' ,'Tutar', 'Ödeme Aracı' ,'Borç/Alacak',]
	rows = []
	for p in borc_alacak_listesi:
		rows.append([p.id,p.tarih,p.uretici,p.tutar, GetOdemeAraciEnum(p.odeme_araci) , GetBorcAlacakEnum(p.borcmu_alacakmi),])
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Borç Alacak Hareketleri',
	'form_adresi':'borc_alacak_yeni',
	'edit_adresi':'borc_alacak/edit/',
	'yeni_buton_adi':'Yeni Ödeme Girişi'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

@login_required
def borc_alacak_yeni(request):
		if request.method == "POST":
			form = BorcAlacakForm(request.POST)
			if form.is_valid():
				borcAlacakObj = form.save(commit=False)
				borcAlacakObj.kullanici = request.user
				borcAlacakObj.save()
				return redirect('/koopmuhasebe/borc_alacak_liste')
		else:
			form = BorcAlacakForm()

		return render(request, 'koopmuhasebe/domain/main-body-form-borc-alacak.html', {'form': form, })

def GetOdemeAraciEnum(var):
	if var == 1:
		return 'Banka'
	if var == 2:
		return 'Nakit'

def GetBorcAlacakEnum(var):
	if var == -1:
		return 'Ödeme'
	else:
		return 'Tahsilat'


@login_required
def borc_alacak_edit(request, pk):
	borcAlacakObj = get_object_or_404(BorcAlacak, pk=pk)
	if request.method == "POST":
		form = BorcAlacakForm(request.POST, instance=borcAlacakObj)
		if form.is_valid():
			borcAlacakObj = form.save(commit=False)
			borcAlacakObj.kullanici = request.user
			form.save()
			return redirect('/koopmuhasebe/borc_alacak_liste')
	else:
		form = BorcAlacakForm(instance=borcAlacakObj)

	return render(request, 'koopmuhasebe/domain/main-body-form-borc-alacak.html', {'form': form, })  ###STOK GİRİŞLERİ


#STOK GİRİŞİ
@login_required
def stok_girisi_yeni(request):
#dukkana mal geldi stok girisi yapiyoruz 		
	if request.method == "POST":
		form = StokGirisiForm(request.POST)
		if form.is_valid():
			stokGirisObj = form.save(commit=False)			
			stokGirisObj.save()
			otomatikNot = str(stokGirisObj.miktar) +' adet ' +stokGirisObj.urun.urun_adi
			urunObj = urun.objects.get(pk=stokGirisObj.urun.id)
			tutar = request.POST['tutar']
			if stokGirisObj.stok_hareketi_tipi_id == 1: # demek ki stok girisi imiş, duzeltme ve fireyi kapsamiyor
				borcAlacak = BorcAlacak.objects.create(uretici=urunObj.uretici, tarih = stokGirisObj.tarih, tutar = tutar, borcmu_alacakmi = 1, notlar =  otomatikNot ,kullanici= request.user, dis_sistem_tipi=1, dis_sistem_id = stokGirisObj.id)
			return redirect('/koopmuhasebe/stok_girisi_liste')
	else:
		form = StokGirisiForm()
	
	s = UrunFiyatVeBirimleriniGetir()	
	return render(request, 'koopmuhasebe/domain/main-body-form-stok_girisi.html', {'form': form, 'urun_fiyat' : s,})

@login_required
def stok_girisi_liste(request):
	stok_girisleri_listesi = StokGirisi.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Ürün' ,'Miktar', 'Stok Hareketi Tipi',]
	rows = []
	for p in stok_girisleri_listesi:		
		rows.append([p.id,p.tarih,p.urun,p.miktar, p.stok_hareketi_tipi,])
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Stok Girişleri',
	'form_adresi':'stok_girisi_yeni',
	'edit_adresi':'stok_girisi/edit/',	
	'yeni_buton_adi':'Yeni Stok Girişi'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

@login_required
def stok_girisi_edit(request,pk):
	stokGirisiObj = get_object_or_404(StokGirisi, pk=pk)
	#borcAlacakObj = BorcAlacak.objects.get(dis_sistem_id=pk, dis_sistem_tipi=1)
	borcAlacakObj = get_or_none(BorcAlacak, dis_sistem_id=pk, dis_sistem_tipi=1)
	tutar = 0
	if request.method == "POST":
		form = StokGirisiForm(request.POST,instance=stokGirisiObj)
		if form.is_valid():
			stokGirisObj = form.save(commit=False)
			form.save()
			tutar = request.POST['tutar']
			if stokGirisObj.stok_hareketi_tipi_id == 1:  # demek ki stok girisi imiş, duzeltme ve fireyi kapsamiyor
				if borcAlacakObj != None:
					borcAlacakObj.tutar = tutar
					borcAlacakObj.save()
				else:
					otomatikNot = str(stokGirisObj.miktar) + ' adet ' + stokGirisObj.urun.urun_adi
					urunObj = urun.objects.get(pk=stokGirisObj.urun.id)
					tutar = request.POST['tutar']
					borcAlacak = BorcAlacak.objects.create(uretici=urunObj.uretici, tarih=stokGirisObj.tarih, tutar=tutar,
														   borcmu_alacakmi=1, notlar=otomatikNot, kullanici=request.user,
														   dis_sistem_tipi=1, dis_sistem_id=stokGirisObj.id)
			return redirect('/koopmuhasebe/stok_girisi_liste',pk=stokGirisiObj.pk)
	else:
		form = StokGirisiForm(instance=stokGirisiObj)
		if borcAlacakObj != None:
			tutar = borcAlacakObj.tutar
	s = UrunFiyatVeBirimleriniGetir()
	return render(request, 'koopmuhasebe/domain/main-body-form-stok_girisi.html', {'form': form, 'urun_fiyat' : s, 'tutar' : tutar, })
	
	

###GİDERLER
@login_required
def gider_yeni(request): 		
	if request.method == "POST":
		form = GiderForm(request.POST)
		if form.is_valid():
			giderObj = form.save(commit=False)			
			giderObj.save()
			return redirect('/koopmuhasebe/gider_liste')
	else:
		form = GiderForm()		
	return render(request, 'koopmuhasebe/domain/main-body-form-gider.html', {'form': form})

@login_required
def gider_edit(request,pk):
	giderObj = get_object_or_404(Gider, pk=pk)
	if request.method == "POST":
		form = GiderForm(request.POST,instance=giderObj)
		if form.is_valid():
			giderObjObj = form.save(commit=False)			
			form.save()
			return redirect('/koopmuhasebe/gider_liste',pk=giderObj.pk)
	else:
		form = GiderForm(instance=giderObj)
	return render(request, 'koopmuhasebe/domain/main-body-form-gider.html', {'form': form})

@login_required	
def gider_liste(request):
	gider_listesi = Gider.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Gider Tipi' ,'Tutar',]
	rows = []
	for p in gider_listesi:		
		rows.append([p.id,p.tarih,p.gider_tipi,p.tutar,])	
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Giderler',
	'form_adresi':'gider_yeni',
	'edit_adresi':'gider/edit/',	
	'yeni_buton_adi':'Yeni Gider'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)
	


###SATIŞ
@login_required
def satis_view(request, pk = None):	
	
	if pk == None:
		satis = Satis()		
	else:
		satis = Satis.objects.get(id = pk)		
	
	satisStokHareketleriFormSet = inlineformset_factory(Satis, SatisStokHareketleri, form=SatisStokHareketleriForm, fields=('urun','miktar','tutar'), extra = 6)	
	
	if request.method == "POST":		
		satisForm = SatisForm(request.POST, instance = satis)		
		satisHareketleri = satisStokHareketleriFormSet(request.POST, instance = satis)		
		if satisForm.is_valid() and satisHareketleri.is_valid():			
			satis = satisForm.save(commit=False)
			satis.kullanici = request.user
			satis.save()			
			objeler2 = satisHareketleri.save(commit=False)			
			for obje in objeler2:
				if(obje.tutar != 0):
					obje.save()
				else:
					obje.delete()
			#objeler2.save()
			return satis_liste(request)
	else:
		if pk != None:
			satisForm = SatisForm(instance=satis)
			satisHareketleri = satisStokHareketleriFormSet(instance=satis)
		else:
			satisForm = SatisForm()
			satisHareketleri = satisStokHareketleriFormSet()
	
	
	s = UrunFiyatVeBirimleriniGetir()
	urunler = stokta_varolan_urunler()
	context = {'form1': satisForm,
	'form2': satisHareketleri,
	'urun_fiyat' : s,
	'urunler' : urunler,
	}

	if pk == None:
		return render(request, 'koopmuhasebe/domain/satis_yeni.html', context)
	else:
		return render(request, 'koopmuhasebe/domain/satis_edit.html', context)


def UrunFiyatVeBirimleriniGetir():
	urun_fiyatlari = urun.objects.all()
	s=""
	for urun_fiyat in urun_fiyatlari:
		#s = s + "'" + str(urun_fiyat.id) + "'," + "'" + str(urun_fiyat.musteri_fiyati) + "'," + "'" + str(urun_fiyat.birim) + "'," + "'" + str(urun_fiyat.kdv_orani) + "',"
		s = s + "'" + str(urun_fiyat.id) + "'," + "'" + str(urun_fiyat.musteri_fiyati) + "'," + "'" + str(
			urun_fiyat.birim) + "'," + "'" + str(urun_fiyat.kdv_kategorisi) + "',"
	return s	

	
@login_required
def satis_liste(request):
	a=User.get_all_permissions(request.user)
	satis_listesi = Satis.objects.all().order_by('-id').annotate(toplamTutar=Sum('satisstokhareketleri__tutar'))
	headers = ['Kayıt No','Tarih','Tutar','Kullanici',]
	rows = []
	for p in satis_listesi:		
		rows.append([p.id,p.tarih,p.toplamTutar,p.kullanici,])	
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Satışlar',
	'form_adresi':'satis_view',
	'edit_adresi':'satis_view/',	
	'yeni_buton_adi':'Yeni Satış'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

		

###ÜRÜN

@login_required
@permission_required("koopmuhasebe.change_urun")
def urun_yeni(request): 		
	if request.method == "POST":
		form = UrunForm(request.POST)
		if form.is_valid():
			urunObj = form.save(commit=False)
			#ureticiObj.kullanici = request.user
			urunObj.save()
			return redirect('/koopmuhasebe/urun_liste')
	else:
		form = UrunForm()		
	return render(request, 'koopmuhasebe/domain/main-body-form-urun.html', {'form': form})

@login_required
def urun_liste(request):
	urun_listesi = urun.objects.all()
	headers = ['Kayıt No','Ürün','Üretici','Üye Fiyatı','Müşteri Fiyatı']
	rows = []
	for p in urun_listesi:		
		rows.append([p.id,p.urun_adi,p.uretici,p.uye_fiyati,p.musteri_fiyati])	
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Ürünler',
	'form_adresi':'urun_yeni',
	'edit_adresi':'koopmuhasebe/urun/edit/',	
	'yeni_buton_adi':'Yeni Ürün'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

@login_required
@permission_required("koopmuhasebe.change_urun")
def urun_edit(request,pk):
	#a = User.get_all_permissions(request.user)
	urunObj = get_object_or_404(urun, pk=pk)
	if request.method == "POST":
		form = UrunForm(request.POST,instance=urunObj)
		if form.is_valid():
			urunObj = form.save(commit=False)			
			form.save()
			return redirect('/koopmuhasebe/urun_liste',pk=urunObj.pk)
	else:
		form = UrunForm(instance=urunObj)
	return render(request, 'koopmuhasebe/domain/main-body-form-urun.html', {'form': form})



###ÜRETİCİ
@login_required
@permission_required("koopmuhasebe.change_uretici")
def form_uretici_yeni(request): 		
	if request.method == "POST":
		form = UreticiForm(request.POST)
		if form.is_valid():
			ureticiObj = form.save(commit=False)
			ureticiObj.kullanici = request.user
			ureticiObj.save()
			return redirect('/koopmuhasebe/liste_uretici')
	else:
		form = UreticiForm()
	return render(request, 'koopmuhasebe/domain/main-body-form-uretici.html', {'form': form})

@login_required
@permission_required("koopmuhasebe.change_uretici")
def form_uretici_edit(request,pk):
	ureticiObj = get_object_or_404(uretici, pk=pk)
	if request.method == "POST":
		form = UreticiForm(request.POST,instance=ureticiObj)
		if form.is_valid():
			ureticiObj = form.save(commit=False)
			ureticiObj.kullanici = request.user
			ureticiObj.tarih = datetime.datetime.now()
			form.save()
			return redirect('/koopmuhasebe/liste_uretici')
	else:
		form = UreticiForm(instance=ureticiObj)
	return render(request, 'koopmuhasebe/domain/main-body-form-uretici.html', {'form': form})

@login_required
def liste_uretici(request):
	uretici_listesi = uretici.objects.all()
	headers = ['Kayıt No','Üretici Adı','Adres']
	rows = []
	for p in uretici_listesi:		
		rows.append([p.id,p.uretici_adi,p.adres])	
	context = {'rows': rows, 'headers': headers,
	'form_adresi':'form_uretici_yeni',
	'title_of_list':'Üreticiler',
	'edit_adresi':'koopmuhasebe/uretici/edit/',	
	'yeni_buton_adi':'Yeni Uretici'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)
	
@login_required
def index(request):
	return redirect('/koopmuhasebe/satis_liste')


