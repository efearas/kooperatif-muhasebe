from django.contrib import admin
from .models import urun,uretici,Satis,SatisStokHareketleri,Birim,GiderTipi
# Register your models here.
admin.site.register(Birim)
admin.site.register(GiderTipi)
admin.site.register(Satis)