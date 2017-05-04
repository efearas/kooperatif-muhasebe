from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class uretici(models.Model):
	uretici_adi = models.CharField(max_length=200)
	adres = models.CharField(max_length=500)
	banka_bilgileri = models.CharField(max_length=500)
	kullanici = models.ForeignKey(User)
	tarih = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.uretici_adi

class Birim(models.Model):
	birim_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.birim_adi

class GiderTipi(models.Model):
	gider_adi = models.CharField(max_length=50)
	def __str__(self):
		return self.gider_adi
		
class Gider(models.Model):
	tarih  = models.DateTimeField()
	gider_tipi = models.ForeignKey(GiderTipi)
	tutar = models.DecimalField(null=True,  max_digits=7,decimal_places=2)
	notlar = models.CharField(max_length=500)


class urun(models.Model):
	urun_adi = models.CharField(max_length=200)
	uretici = models.ForeignKey(uretici)
	uye_fiyati = models.DecimalField(null=True,  max_digits=7,decimal_places=2)
	musteri_fiyati = models.DecimalField(null=True,   max_digits=7,decimal_places=2)
	birim = models.ForeignKey(Birim, null=True)
	def __str__(self):
		return self.urun_adi

class StokGirisi(models.Model):
	tarih = models.DateTimeField()
	urun = models.ForeignKey(urun)
	miktar = models.IntegerField()
	notlar = models.CharField(max_length=500)


class Satis(models.Model):
	tarih = models.DateTimeField()
	def __str__(self):
		return self.tarih

class SatisStokHareketleri(models.Model):
	satis = models.ForeignKey(Satis, on_delete=models.CASCADE)
	urun = models.ForeignKey(urun)
	miktar = models.IntegerField()
	tutar = models.DecimalField(null=True,   max_digits=7,decimal_places=2)	
	def __str__(self):
		return self.urun


	