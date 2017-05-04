from django.conf.urls import url
from django.conf.urls import include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),			
	url(r'liste_uretici', views.liste_uretici, name='liste_uretici'),
	url(r'form_uretici_yeni', views.form_uretici_yeni, name='form_uretici_yeni'),	
	url(r'uretici/edit/(?P<pk>\d+)$', views.form_uretici_edit, name='uretici_edit'),
	
	url(r'urun_liste', views.urun_liste, name='urun_liste'),
	url(r'urun_yeni', views.urun_yeni, name='urun_yeni'),
	url(r'urun/edit/(?P<pk>\d+)$', views.urun_edit, name='urun_edit'),	
	
	url(r'satis_view/(?P<pk>\d+)$', views.satis_view, name='satis'),
	url(r'satis_view/', views.satis_view, name='satis'),
	url(r'satis_liste', views.satis_liste, name='satis_liste'),
	
	url(r'gider_liste', views.gider_liste, name='gider_liste'),
	url(r'gider_yeni', views.gider_yeni, name='gider_yeni'),
	url(r'gider/edit/(?P<pk>\d+)$', views.gider_edit, name='gider_edit'),	
	
	url(r'stok_girisi_liste', views.stok_girisi_liste, name='stok_girisi_liste'),
	url(r'stok_girisi_yeni', views.stok_girisi_yeni, name='stok_girisi_yeni'),
	url(r'stok_girisi/edit/(?P<pk>\d+)$', views.stok_girisi_edit, name='stok_girisi_edit'),	
	
	url('^', include('django.contrib.auth.urls')),	
	url(r'login/$', auth_views.LoginView.as_view(template_name='koopmuhasebe/login.html')),	
]