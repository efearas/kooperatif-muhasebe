from django.contrib import admin
from .models import urun,uretici,Satis,SatisStokHareketleri,Birim,GiderTipi,VirmanVeDuzeltmeHesaplari,StokHareketiTipi,UrunKategorisi
# Register your models here.
admin.site.register(Birim)
admin.site.register(GiderTipi)
admin.site.register(Satis)
admin.site.register(VirmanVeDuzeltmeHesaplari)
admin.site.register(StokHareketiTipi)
admin.site.register(UrunKategorisi)