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
	
	url(r'virman_liste', views.virman_liste, name='virman_liste'),
	url(r'virman_yeni', views.virman_yeni, name='virman_yeni'),
	url(r'virman/edit/(?P<pk>\d+)$', views.virman_edit, name='virman_edit'),	

	url(r'borc_alacak_liste', views.borc_alacak_liste, name='borc_alacak_liste'),
	url(r'borc_alacak_yeni', views.borc_alacak_yeni, name='borc_alacak_yeni'),
	url(r'borc_alacak/edit/(?P<pk>\d+)$', views.borc_alacak_edit, name='borc_alacak_edit'),

	url(r'rapor_stok', views.rapor_stok, name='rapor_stok'),
	url(r'rapor_ciro', views.rapor_ciro, name='rapor_ciro'),
	url(r'rapor_satis_aylik', views.rapor_satis_aylik, name='rapor_satis_aylik'),
	url(r'rapor_uretici_borc', views.rapor_uretici_borc, name='rapor_uretici_borc'),
	url(r'rapor_satis_haftalik/(?P<pk>\d+)$', views.rapor_satis_haftalik, name='rapor_satis_haftalik'),

	url(r'json_get_urun_zaman_fiyat/(?P<pk>\d+)$', views.json_get_urun_zaman_fiyat, name='json_get_urun_zaman_fiyat'),
	url(r'json_post_urun_zaman_fiyat', views.json_post_urun_zaman_fiyat, name='json_post_urun_zaman_fiyat'),
	url(r'json_get_urun_son_fiyat/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)$', views.json_get_urun_son_fiyat, name='json_get_urun_son_fiyat'),

	url(r'dashboard', views.dashboard, name='dashboard'),	



	url(r'test', views.test, name='test'),
	
	url('^', include('django.contrib.auth.urls')),	
	url(r'login/$', auth_views.LoginView.as_view(template_name='koopmuhasebe/login.html')),	
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),

]