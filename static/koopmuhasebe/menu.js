function LoadMenu()
{
    //alert('asdsa');
    
	$("#side-menu").append("<li><a href='satis_liste.html'><i class='fa fa-money fa-fw'></i> Satışlar</a></li>");
    $("#side-menu").append("<li><a href='urun_girisi_liste.html'><i class='fa fa-sign-in fa-fw'></i> Ürün Girişleri</a></li>");
	$("#side-menu").append("<li><a href='kasa_gider_liste.html'><i class='fa fa-minus fa-fw'></i> Kasa Giderleri</a></li>");
	$("#side-menu").append("<li><a href='kasa_banka_virman_liste.html'><i class='fa fa-exchange fa-fw'></i> Kasa Banka Virman İşlemleri</a></li>");
	
	$("#side-menu").append("<li><a href='stok_duzeltme_liste.html'><i class='fa fa-check fa-fw'></i> Stok Düzeltme İşlemleri</a></li>");
	$("#side-menu").append("<li><a href='kasa_duzeltme_liste.html'><i class='fa fa-check-square fa-fw'></i> Kasa Düzeltme İşlemleri</a></li>");
	
    //$("#side-menu").append("<li><a href='siparisler.html'><i class='fa fa-envelope fa-fw'></i> Siparişler</a></li>");
	//$("#side-menu").append("<li><i></i> </li>");
	
	
	$("#side-menu").append("<li>");
		//$("#side-menu").append("<a href='#'><i class='fa fa-wrench fa-fw'></i> UI Elements </a>");
		$("#side-menu").append("<ul class='nav nav-second-level'>");
			$("#side-menu").append("<li><a href='urunler.html'><i class='fa fa-tree fa-fw'></i> Ürünler</a></li>");
			$("#side-menu").append("<li><a href='ureticiler.html'><i class='fa fa-users fa-fw'></i> Üreticiler</a></li>");
			$("#side-menu").append("<li><a href='gider_liste.html'><i class='fa fa-envelope fa-fw'></i> Gider Tipleri</a></li>");
			$("#side-menu").append("<li><a href='fiyat_tipi_liste.html'><i class='fa fa-bullseye fa-fw'></i> Fiyat Tipleri</a></li>");
		$("#side-menu").append("</ul>");
    $("#side-menu").append("</li>");
    
    return;
}

LoadMenu();