from django.db import connection
import pdb



def rapor_stok_durumu():
	query = """WITH
			UnionedTable AS(	
				select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
				UNION
				select urun_id,miktar from koopmuhasebe_stokgirisi	
			),
			UnionedTableGrouped AS(	
				select urun_id,SUM(miktar) as miktar from UnionedTable
				GROUP BY urun_id	
			)

			SELECT  koopmuhasebe_urun.urun_adi, UnionedTableGrouped.miktar FROM UnionedTableGrouped
			INNER JOIN koopmuhasebe_urun
			ON UnionedTableGrouped.urun_id = koopmuhasebe_urun.id
			ORDER BY UnionedTableGrouped.miktar ASC
			"""
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0],row[1],])				
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