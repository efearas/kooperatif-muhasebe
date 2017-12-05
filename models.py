# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Birim(models.Model):
	birim_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.birim_adi

class GiderTipi(models.Model):
	gider_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.gider_adi

class StokHareketiTipi(models.Model):
	stok_hareket_tipi_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.stok_hareket_tipi_adi
		#return self.stok_hareket_tipi_adi.encode('utf-8')

class UrunKategorisi(models.Model):
	urun_kategori_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.urun_kategori_adi
		
###

class KDVKategorisi(models.Model):
	kategori_adi = models.CharField(max_length=200)
	kdv_orani = models.IntegerField()
	def __str__(self):
		return self.kategori_adi


class uretici(models.Model):
	uretici_adi = models.CharField(max_length=200)
	adres = models.CharField(max_length=500)
	banka_bilgileri = models.CharField(max_length=500)
	kullanici = models.ForeignKey(User)
	tarih = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.uretici_adi

class BorcAlacak(models.Model):
	BORC_ALACAK_CHOICES = (
		(1,'Alacak'),
		(-1, 'Borç'),
	)

	ODEME_ARACI_CHOICES = (
		(1, 'Banka'),
		(2, 'Nakit'),
	)

	uretici = models.ForeignKey(uretici)
	tarih = models.DateTimeField()
	tutar = models.DecimalField(null=True, max_digits=7, decimal_places=2)
	borcmu_alacakmi = models.IntegerField(null=True, choices=BORC_ALACAK_CHOICES,
        default=-1,)
	odeme_araci = models.IntegerField(null=True, choices=ODEME_ARACI_CHOICES, blank=True,)
	notlar = models.CharField(max_length=1500)
	kullanici = models.ForeignKey(User)
	dis_sistem_tipi = models.IntegerField(null=True) #stok girisi veya programin baska yerlerinden yapilan girislerde kullanilacak
	dis_sistem_id = models.IntegerField(null=True) #stok_girisi_id



class kisi(models.Model):
	kisi_adi = models.CharField(max_length=100) 	
	notlar = models.CharField(max_length=1500, null=True)
	def __str__(self):
		return self.kisi_adi

class KisiOdemeTahsilat(models.Model):
	ODEME_TAHSILAT_CHOICES = (
		(1,'Tahsilat'),
		(-1, 'Ödeme'),
	)

	ODEME_ARACI_CHOICES = (
		(1, 'Banka'),
		(2, 'Kasa'),
	)

	kisi = models.ForeignKey(kisi)
	tarih = models.DateTimeField()
	tutar = models.DecimalField(null=True, max_digits=7, decimal_places=2)
	odememi_tahsilatmi = models.IntegerField(null=True, choices=ODEME_TAHSILAT_CHOICES,
        default=1,)
	odeme_araci = models.IntegerField(null=True, choices=ODEME_ARACI_CHOICES, blank=True,)
	notlar = models.CharField(max_length=1500)
	kullanici = models.ForeignKey(User)

	




class urun(models.Model):
	urun_kategorisi = models.ForeignKey(UrunKategorisi)
	kdv_kategorisi = models.ForeignKey(KDVKategorisi, null=True)
	urun_adi = models.CharField(max_length=200)
	uretici = models.ForeignKey(uretici)
	uye_fiyati = models.DecimalField(null=True,  max_digits=7,decimal_places=2)
	musteri_fiyati = models.DecimalField(null=True,   max_digits=7,decimal_places=2)
	birim = models.ForeignKey(Birim, null=True)
	kdv_orani = models.IntegerField(null=True)	
	dayanisma_urunu = models.BooleanField()
	def __str__(self):
		return self.urun_adi

class urun_fiyat(models.Model):
	urun = models.ForeignKey(urun)
	zaman = models.DateTimeField()
	fiyat = models.DecimalField(max_digits=7, decimal_places=2)
	kullanici = models.ForeignKey(User)
		
class Gider(models.Model):
	ODEME_ARACI_CHOICES = (
		(1, 'Banka'),
		(2, 'Nakit'),
	)
	tarih  = models.DateTimeField()
	gider_tipi = models.ForeignKey(GiderTipi)
	tutar = models.DecimalField(null=True,  max_digits=7,decimal_places=2)
	notlar = models.CharField(max_length=500)
	odeme_araci = models.IntegerField(null=True, choices=ODEME_ARACI_CHOICES, blank=True,)

class StokGirisi(models.Model):
	stok_hareketi_tipi = models.ForeignKey(StokHareketiTipi)
	tarih = models.DateTimeField()
	urun = models.ForeignKey(urun)
	miktar = models.IntegerField()
	agirlik = models.DecimalField(null=True,  max_digits=5,decimal_places=2)
	notlar = models.CharField(max_length=500)
	
class Satis(models.Model):
	tarih = models.DateTimeField()
	kullanici = models.ForeignKey(User)
	def __str__(self):
		return str(self.tarih)

class SatisStokHareketleri(models.Model):
	satis = models.ForeignKey(Satis, on_delete=models.CASCADE)
	urun = models.ForeignKey(urun)
	miktar = models.IntegerField()
	tutar = models.DecimalField(null=True,   max_digits=7,decimal_places=2)	
	def __str__(self):
		return self.urun.urun_adi

class VirmanVeDuzeltmeHesaplari(models.Model):
	hesap_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.hesap_adi

HESAP_CHOICES = (
	(0, '---------'),
	(1, 'Banka'),
	(2, 'Kasa'),
)	


class VirmanVeDuzeltme(models.Model):
	tarih  = models.DateTimeField()
	cikis_hesabi = models.IntegerField(null=True, choices=HESAP_CHOICES,)
	giris_hesabi = models.IntegerField(null=True, choices=HESAP_CHOICES,)
	tutar = models.DecimalField(max_digits=7,decimal_places=2)	
	notlar = models.CharField(max_length=500)
	kullanici = models.ForeignKey(User, null=True)
