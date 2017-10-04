from django.db import connection
import pdb



def rapor_stok_durumu():
	query = """WITH
			UnionedTable AS(	
				select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
				UNION ALL
				select urun_id,miktar from koopmuhasebe_stokgirisi	
			),
			UnionedTableGrouped AS(	
				select urun_id,SUM(miktar) as miktar from UnionedTable
				GROUP BY urun_id	
			)

			SELECT  koopmuhasebe_urun.urun_adi, UnionedTableGrouped.miktar,koopmuhasebe_urun.musteri_fiyati, (UnionedTableGrouped.miktar * koopmuhasebe_urun.musteri_fiyati) as urunToplamDegeri FROM UnionedTableGrouped
			INNER JOIN koopmuhasebe_urun
			ON UnionedTableGrouped.urun_id = koopmuhasebe_urun.id
			ORDER BY UnionedTableGrouped.miktar ASC
			"""
	yekun = 0
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0],row[1],row[2],row[3],])
			yekun = yekun + row[3]
	lastRow = (0,0,0,yekun)
	tuple = (rows,lastRow)
	return tuple
	
	
def stogu_azalan_urunler():
	query = """
	WITH
	UrunStokHareketleriUnion AS(	
		select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
		UNION
		select urun_id,miktar from koopmuhasebe_stokgirisi	
	),
	UrunBazindaStokDurumu AS(	
		select urun_id,SUM(miktar) as miktar from UrunStokHareketleriUnion
		GROUP BY urun_id	
	),
	Son1SaatIcindeSatilanUrunler AS(
		select urun_id,urun_adi from koopmuhasebe_satis
		INNER JOIN koopmuhasebe_satisstokhareketleri ON koopmuhasebe_satis.id = koopmuhasebe_satisstokhareketleri.satis_id
		INNER JOIN koopmuhasebe_urun ON koopmuhasebe_satisstokhareketleri.urun_id = koopmuhasebe_urun.id
		WHERE tarih >= NOW() - '1 month'::INTERVAL
	)

	SELECT  Son1SaatIcindeSatilanUrunler.urun_adi FROM Son1SaatIcindeSatilanUrunler
	INNER JOIN UrunBazindaStokDurumu
	ON UrunBazindaStokDurumu.urun_id = Son1SaatIcindeSatilanUrunler.urun_id
	WHERE miktar < 5
	GROUP BY Son1SaatIcindeSatilanUrunler.urun_adi
	"""
	
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0],])				
	return rows


def rapor_ciro_durumu(baslangicTarihi, bitisTarihi):
	baslangicTarihi = str(baslangicTarihi) + ' 00:00:00'
	bitisTarihi = str(bitisTarihi) + ' 23:59:59'	
	query = """
	WITH
		IntersectTable AS(	
			select koopmuhasebe_satis.tarih, koopmuhasebe_satisstokhareketleri.tutar 
			FROM koopmuhasebe_satis	
			INNER JOIN koopmuhasebe_satisstokhareketleri
			ON koopmuhasebe_satis.id = koopmuhasebe_satisstokhareketleri.satis_id	
			WHERE tarih BETWEEN '{baslangic}' AND '{bitis}'
		)
	
	SELECT  date(tarih),sum(tutar) FROM IntersectTable
	GROUP BY date(tarih)
	ORDER BY date(tarih) ASC
			"""
	query = query.format(baslangic=baslangicTarihi,bitis=bitisTarihi)	
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0],row[1],])				
	return rows