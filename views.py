	# -*- coding: utf-8 -*-

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404
#from .models import urun,uretici,Satis,SatisStokHareketleri,Gider,StokGirisi,VirmanVeDuzeltme,BorcAlacak,urun_fiyat
from .models import *
#from .forms import UreticiForm,UrunForm, SatisForm, SatisStokHareketleriForm, GiderForm, StokGirisiForm, VirmanForm, RaporTarihForm, BorcAlacakForm
from .forms import *
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
from django.http import JsonResponse
import  json
from django.db.models import Max, Min
from django.db import connection

from django.utils import timezone
from django.utils.timezone import get_current_timezone
from django.utils.timezone import localtime

from .functions import *
import os


def test(request):		
	dic = birim_fiyat_hesapla(7.50,25.50, 30, False)
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
def json_get_urun_zaman_fiyat(request,pk):
	results = urun_fiyat.objects.filter(urun=pk).values('zaman', 'fiyat','kullanici__username').order_by('-zaman')
	for row in results:
		#zaman = timezone.make_aware(row['zaman'] , timezone.get_current_timezone())
		row['zaman'] = localtime(row['zaman']).strftime("%Y-%m-%d %H:%M:%S")
	return JsonResponse({'results': list(results)})

@login_required
def json_get_urun_son_fiyat(request, yyyy,mo,dd,hh,mi):
	tarih =  datetime.datetime.strptime(yyyy + "-" + mo + "-" + dd + " " + hh + ":" + mi , "%Y-%m-%d %H:%M")
	dt_aware = timezone.make_aware(tarih, timezone.get_current_timezone())
	results = urunlerin_guncel_fiyatlari(dt_aware)
	return JsonResponse({'results': list(results)})

@login_required
def json_post_urun_zaman_fiyat(request):
	if request.method == 'POST':
		dic = json.loads(request.body.decode('utf-8'))
		#tarih = timezone.now()
		#tarih = timezone.make_aware(tarih, timezone.get_current_timezone())
		tarih = timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())
		urun_fiyat.objects.create(urun_id=dic['urun_id'], zaman = tarih, fiyat = dic['fiyat'], kullanici=request.user)
	return JsonResponse({'zaman': tarih.strftime("%Y-%m-%d %H:%M:%S"), 'fiyat' : "{:10.2f}".format(dic['fiyat']) , 'kullanici' : request.user.username })



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
def rapor_banka_hareketleri(request):
	headers = ['ID','Tarih','Tutar','Hareket Tipi', ]
	rows = rapor_banka_hareketleri_listesi()
	rows2 =[]
	for row in rows:				
		rows2.append([ GetEditAdresi(row[3]) ,row[0],row[1], row[2],row[3],])
	context = {
	'rows': rows2,
	'headers': headers,
	'title_of_list':'Banka Hareketleri',		
	}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)


@login_required
def rapor_kasa_hareketleri(request):
	headers = ['ID','Tarih','Tutar','Hareket Tipi', ]
	rows = rapor_kasa_hareketleri_listesi()
	rows2 =[]
	for row in rows:				
		rows2.append([ GetEditAdresi(row[3]) ,row[0],row[1], row[2],row[3],])
	context = {
	'rows': rows2,
	'headers': headers,
	'title_of_list':'Kasa Hareketleri',		
	}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

def GetEditAdresi(var):	
	dic = {"Virman" : "virman/edit/", 
	"Satış" : "satis_view/",
	"Gider" : "gider/edit/", 
	"Üreticiye Ödeme" : "borc_alacak/edit/", 
	"Üye Ödeme/Tahsilat": "kisi_odeme_tahsilat/edit/"}
	return dic[var]
	

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
def dashboard(request):
	kasa = rapor_kasa_durumu()
	banka = rapor_banka_durumu()
	context = {'kasa':kasa,
	'banka':banka,
	}
	return render(request, 'koopmuhasebe/main-body-dashboard.html',context)

@login_required
def virman_liste(request):
	virman_listesi = VirmanVeDuzeltme.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Çıkış Hesabı' ,'Giriş Hesabı', 'Tutar', 'Kullanıcı',]
	rows = []
	for p in virman_listesi:		
		rows.append([p.id,localtime(p.tarih).strftime("%Y-%m-%d %H:%M:%S"), GetHesapEnum(p.cikis_hesabi),GetHesapEnum(p.giris_hesabi),p.tutar, p.kullanici,])
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
	#borc_alacak_listesi = BorcAlacak.objects.all().order_by('-id')
	borc_alacak_listesi = borc_alacak_dosya_bilgisi_ile()
	headers = ['Kayıt No','Tarih','Üretici' ,'Tutar', 'Ödeme Aracı' ,'Borç/Alacak','Evrak']
	rows = []
	for p in borc_alacak_listesi:
		evrak_html = ""
		if p[6] != None:
			evrak_html = "<i class=\"fa fa-file-text-o fa-fw\"></i>"
		rows.append([p[0],localtime(p[1]).strftime("%Y-%m-%d %H:%M:%S"),p[2],p[3],GetOdemeAraciEnum(p[4]),GetBorcAlacakEnum(p[5]),evrak_html,])
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
				if 'myfile' in request.FILES:
					for f in request.FILES.getlist('myfile'):						
						dosya.SaveFile(f,"borc_alacak", borcAlacakObj.id)
				return redirect('/koopmuhasebe/borc_alacak_liste')
		else:
			form = BorcAlacakForm()

		return render(request, 'koopmuhasebe/domain/main-body-form-borc-alacak.html', {'form': form, })

def GetOdemeAraciEnum(var):
	if var == 1:
		return 'Banka'
	if var == 2:
		return 'Nakit'
def GetHesapEnum(var):
	if var == 1:
		return 'Banka'
	if var == 2:
		return 'Kasa'
def GetBorcAlacakEnum(var):
	if var == -1:
		return 'Ödeme'
	else:
		return 'Ürün Girişi'


@login_required
def borc_alacak_edit(request, pk):
	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	MEDIA_ROOT = os.path.join(BASE_DIR, 'koopmuhasebe/media')
	path = request.get_full_path()
	path2 =  request.build_absolute_uri() 
	borcAlacakObj = get_object_or_404(BorcAlacak, pk=pk)
	if request.method == "POST":
		form = BorcAlacakForm(request.POST, instance=borcAlacakObj)
		if form.is_valid():
			borcAlacakObj = form.save(commit=False)
			borcAlacakObj.kullanici = request.user
			form.save()			
			if 'myfile' in request.FILES:
				for f in request.FILES.getlist('myfile'):						
					dosya.SaveFile(f,"borc_alacak", borcAlacakObj.id)
			return redirect('/koopmuhasebe/borc_alacak_liste')
	else:
		form = BorcAlacakForm(instance=borcAlacakObj)
		file_rows = dosya.GetFileList("borc_alacak", borcAlacakObj.id)
	return render(request, 'koopmuhasebe/domain/main-body-form-borc-alacak.html', {'form': form,'file_rows': file_rows, })  

###STOK GİRİŞLERİ


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
		rows.append([p.id,localtime(p.tarih).strftime("%Y-%m-%d %H:%M:%S"),p.urun,p.miktar, p.stok_hareketi_tipi,])
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
	headers = ['Kayıt No','Tarih','Gider Tipi' ,'Tutar','Ödeme Aracı',]
	rows = []
	for p in gider_listesi:		
		rows.append([p.id,p.tarih,p.gider_tipi,p.tutar,GetOdemeAraciEnum(p.odeme_araci) ,])	
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
			#return satis_liste(request)
			return redirect('/koopmuhasebe/satis_liste')
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
		return render(request, 'koopmuhasebe/domain/satis_yeni_v2.html', context)
	else:
		return render(request, 'koopmuhasebe/domain/satis_edit_v2.html', context)


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
	satis_listesi = Satis.objects.all().order_by('-id').annotate(toplamTutar=Sum('satisstokhareketleri__tutar'))[:200]
	headers = ['Kayıt No','Tarih','Tutar','Kullanici',]
	rows = []
	for p in satis_listesi:		
		rows.append([p.id, localtime(p.tarih).strftime("%Y-%m-%d %H:%M:%S"),p.toplamTutar,p.kullanici,])	
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
	return render(request, 'koopmuhasebe/domain/main-body-form-urun_v2.html', {'form': form, 'pk':0})#js patlamasin diye pk'ya 0 geciyorum

@login_required
def urun_liste(request):
	urun_listesi = urun.objects.all()
	headers = ['Kayıt No','Ürün','Üretici','Fiyat']
	rows = urunler_ve_fiyatlari()	
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
	return render(request, 'koopmuhasebe/domain/main-body-form-urun_v2.html', {'form': form, 'pk':pk})


###Kisi
@login_required
@permission_required("koopmuhasebe.change_kisi")
def kisi_yeni(request): 		
	if request.method == "POST":
		form = KisiForm(request.POST)
		if form.is_valid():
			kisiObj = form.save(commit=False)			
			kisiObj.save()
			return redirect('/koopmuhasebe/kisi_liste')
	else:
		form = KisiForm()
	return render(request, 'koopmuhasebe/domain/main-body-form-kisi.html', {'form': form})

@login_required
@permission_required("koopmuhasebe.change_kisi")
def kisi_edit(request,pk):
	kisiObj = get_object_or_404(kisi, pk=pk)
	if request.method == "POST":
		form = KisiForm(request.POST,instance=kisiObj)
		if form.is_valid():
			kisiObj = form.save(commit=False)			
			form.save()
			return redirect('/koopmuhasebe/kisi_liste')
	else:
		form = KisiForm(instance=kisiObj)
	return render(request, 'koopmuhasebe/domain/main-body-form-kisi.html', {'form': form})


def kisi_liste(request):
	kisi_listesi = kisi.objects.all()
	headers = ['Kayıt No','Kişi Adı','Notlar']
	rows = []
	for p in kisi_listesi:		
		rows.append([p.id,p.kisi_adi,p.notlar[0:20]+'...' ])	
	context = {'rows': rows, 'headers': headers,
	'form_adresi':'kisi_yeni',
	'title_of_list':'Kişiler',
	'edit_adresi':'koopmuhasebe/kisi/edit/',	
	'yeni_buton_adi':'Yeni Kişi'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

#kisi_odeme_tahsilat

@login_required
def kisi_odeme_tahsilat_liste(request):
	kisi_odeme_tahsilat_listesi = KisiOdemeTahsilat.objects.all().order_by('-id')
	headers = ['Kayıt No','Tarih','Kişi' ,'Tutar', 'Ödeme Aracı' ,'Ödeme/Tahsilat',]
	rows = []
	for p in kisi_odeme_tahsilat_listesi:
		rows.append([p.id,p.tarih,p.kisi,p.tutar, GetOdemeAraciEnum(p.odeme_araci) , GetOdemeTahsilatEnum(p.odememi_tahsilatmi),])
	context = {'rows': rows, 'headers': headers,
	'title_of_list':'Ödeme Tahsilat Hareketleri',
	'form_adresi':'kisi_odeme_tahsilat_yeni',
	'edit_adresi':'kisi_odeme_tahsilat/edit/',
	'yeni_buton_adi':'Yeni Ödeme/Tahsilat Girişi'}
	return render(request, 'koopmuhasebe/main-body-liste.html',context)

def GetOdemeTahsilatEnum(var):
	#if var == 1:
	return 'Tahsilat' if var ==1 else 'Ödeme'
	#else:
	#	return 'Ödeme'

@login_required
def kisi_odeme_tahsilat_yeni(request):
		if request.method == "POST":
			form = KisiOdemeTahsilatForm(request.POST)
			if form.is_valid():
				kisiOdemeTahsilatObj = form.save(commit=False)
				kisiOdemeTahsilatObj.kullanici = request.user
				kisiOdemeTahsilatObj.save()
				return redirect('/koopmuhasebe/kisi_odeme_tahsilat_liste')
		else:
			form = KisiOdemeTahsilatForm()

		return render(request, 'koopmuhasebe/domain/main-body-form-kisi-odeme-tahsilat.html', {'form': form, })

@login_required
def kisi_odeme_tahsilat_edit(request, pk):
	kisiOdemeTahsilatObj = get_object_or_404(KisiOdemeTahsilat, pk=pk)
	if request.method == "POST":
		form = KisiOdemeTahsilatForm(request.POST, instance=kisiOdemeTahsilatObj)
		if form.is_valid():
			kisiOdemeTahsilatObj = form.save(commit=False)
			kisiOdemeTahsilatObj.kullanici = request.user
			form.save()
			return redirect('/koopmuhasebe/kisi_odeme_tahsilat_liste')
	else:
		form = KisiOdemeTahsilatForm(instance=kisiOdemeTahsilatObj)

	return render(request, 'koopmuhasebe/domain/main-body-form-kisi-odeme-tahsilat.html', {'form': form, })  

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


