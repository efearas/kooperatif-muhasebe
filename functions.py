import math

def birim_fiyat_hesapla(alis_fiyati_kdv_dahil, kargo_bedeli, adet_kg, vergi_mukellefi_uretici):
    urun_birim_maliyeti = alis_fiyati_kdv_dahil + (kargo_bedeli/adet_kg)
    amortisman = 0.01    
    dukkan_giderleri = 0.15
    kooperatif_calismalari = 0.01
    toplumsal_dayanisma_fonu = 0.01        
    gider_pusulasi_icin_eklenecek_oran = 0 if vergi_mukellefi_uretici else 0.05    
    urune_eklenecek_oranlar_toplami =  amortisman + dukkan_giderleri + kooperatif_calismalari + toplumsal_dayanisma_fonu + gider_pusulasi_icin_eklenecek_oran
    tahmini_birim_satis_fiyati = urun_birim_maliyeti* (1 +urune_eklenecek_oranlar_toplami)
    ortaklara_satis_fiyati = math.ceil(tahmini_birim_satis_fiyati)
    
    gelir_vergisi_orani_stopaj = urune_eklenecek_oranlar_toplami * 1.2
    paketleme_masrafi = 0.01
    perakende_satis_fiyati = math.ceil(urun_birim_maliyeti * (1 + gelir_vergisi_orani_stopaj+paketleme_masrafi))
    
    return {'ortaklara_satis_fiyati':ortaklara_satis_fiyati, 'perakende_satis_fiyati' : perakende_satis_fiyati}

