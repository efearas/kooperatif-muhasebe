# -*- coding: utf-8 -*-
from django.db import connection
import pdb
import datetime


def rapor_aylik_urun_satis():
	# son 6 aydaki urun bazinda satislar
	# son 6 ay oldugunu kabul edince kolon sayisi sabitleniyor.
	raporBaslangicTarihi = datetime.date(2017,6,1) 
	query = """
			SELECT  date_part('year', tarih) as yil, date_part('month', tarih) as ay,  urun_adi, sum(miktar),urun_id 
			FROM koopmuhasebe_satisstokhareketleri
			INNER JOIN koopmuhasebe_satis ON koopmuhasebe_satisstokhareketleri.satis_id = koopmuhasebe_satis.id
			INNER JOIN koopmuhasebe_urun ON koopmuhasebe_satisstokhareketleri.urun_id = koopmuhasebe_urun.id
            WHERE tarih > '{baslangicTarihi}'
            GROUP BY yil,ay, urun_adi,urun_id
            ORDER BY yil, ay ASC
			"""
	strBaslangicTarihi = raporBaslangicTarihi.strftime("%Y-%m-%d %H:%M")
	query = query.format(baslangicTarihi=strBaslangicTarihi)
	dicUrunAy = {}
	dicUrunler = {}
	dicAylar = {}
	listAylar = []

	with connection.cursor() as cursor:
		cursor.execute(query)		
		for row in cursor.fetchall():
			yilAy = str(int(row[0]) ) + '-' + str(int(row[1]))
			if not yilAy in dicAylar:
				dicAylar[yilAy]=0 #value onemli degil
				listAylar.append(yilAy)
			if not row[4] in dicUrunler:
				dicUrunler[row[4]] = row[2]

			urunAyStr = yilAy + '-' + str(row[4])
			dicUrunAy[urunAyStr] = row[3]

	# Header kismi
	header = []
	header.append("Ürün Adı")
	for t in listAylar:
		header.append(t)

	rows = []

	for urun in dicUrunler:
			row = []
			row.append(dicUrunler[urun])
			for t in listAylar:
				strAyUrun = t + '-' + str(urun)
				if strAyUrun in dicUrunAy:
					row.append( str(dicUrunAy[strAyUrun]) )
				else:
					row.append('-')
			rows.append(row)

	tuple = (rows,header)
	return tuple


def rapor_stok_durumu():
	query = """
			WITH
			UnionedTable AS(	
				select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
				UNION ALL
				select urun_id,miktar from koopmuhasebe_stokgirisi	
			),
			UnionedTableGrouped AS(	
				select urun_id,SUM(miktar) as miktar from UnionedTable
				GROUP BY urun_id	
			)

			SELECT  koopmuhasebe_urun.id ,koopmuhasebe_urun.urun_adi, UnionedTableGrouped.miktar,koopmuhasebe_urun.musteri_fiyati, (UnionedTableGrouped.miktar * koopmuhasebe_urun.musteri_fiyati) as urunToplamDegeri FROM UnionedTableGrouped
			INNER JOIN koopmuhasebe_urun
			ON UnionedTableGrouped.urun_id = koopmuhasebe_urun.id
			ORDER BY UnionedTableGrouped.miktar ASC
			"""
	yekun = 0
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0],row[1],row[2],row[3],row[4],])
			if row[4] != None:
				yekun = yekun + row[4]
	lastRow = (0,0,0,0,yekun)
	tuple = (rows,lastRow)
	return tuple


def rapor_kasa_hareketleri_listesi():
	query = """
			WITH

			UninionedKasaHareketleri AS(
				--Satis
				SELECT satis_id as ID,koopmuhasebe_satis.tarih as Tarih, sum(tutar) as Tutar, 'Satış' as HareketTipi FROM koopmuhasebe_satis
				INNER JOIN koopmuhasebe_satisstokhareketleri
				ON koopmuhasebe_satis.id = koopmuhasebe_satisstokhareketleri.satis_id
				GROUP BY satis_id,koopmuhasebe_satis.tarih
				UNION ALL
				-- Gider
				SELECT id as ID, tarih as Tarih, -(tutar) as Tutar, 'Gider' as HareketTipi  from koopmuhasebe_gider 
				WHERE odeme_araci=2
				UNION ALL
				--virman kasaya giris
				select id, tarih, tutar, 'Virman' from koopmuhasebe_virmanveduzeltme 
				WHERE giris_hesabi =2 
				UNION ALL
				--virman kasadan cikis
				select id, tarih, -(tutar), 'Virman' from koopmuhasebe_virmanveduzeltme 
				WHERE cikis_hesabi=2
				UNION ALL
				-- ureticiye odeme
				SELECT id, tarih, -(tutar), 'Üreticiye Ödeme' from koopmuhasebe_borcalacak 
				WHERE odeme_araci=2
				UNION ALL
				-- uye odeme tahsilat
				SELECT id,tarih,( odememi_tahsilatmi*tutar), 'Üye Ödeme/Tahsilat' from koopmuhasebe_kisiodemetahsilat 
				WHERE odeme_araci=2
			)

			SELECT * FROM UninionedKasaHareketleri
			ORDER BY Tarih DESC			
			"""
	rows = []
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = cursor.fetchall()		
	return rows

def rapor_banka_hareketleri_listesi():
	query = """
			WITH
			UninionedBankaHareketleri AS(
				-- Gider
				SELECT id as ID, tarih as Tarih, -(tutar) as Tutar, 'Gider' as HareketTipi  from koopmuhasebe_gider 
				WHERE odeme_araci=1
				UNION ALL
				--virman bankaya giris
				select id, tarih, tutar, 'Virman' from koopmuhasebe_virmanveduzeltme 
				WHERE giris_hesabi =1
				UNION ALL
				--virman bankadan cikis
				select id, tarih, -(tutar), 'Virman' from koopmuhasebe_virmanveduzeltme 
				WHERE cikis_hesabi=1
				UNION ALL
				-- ureticiye odeme
				SELECT id, tarih, -(tutar), 'Üreticiye Ödeme' from koopmuhasebe_borcalacak 
				WHERE odeme_araci=1
				UNION ALL
				-- uye odeme tahsilat
				SELECT id,tarih,( odememi_tahsilatmi*tutar), 'Üye Ödeme/Tahsilat' from koopmuhasebe_kisiodemetahsilat 
				WHERE odeme_araci=1 				
			)

			SELECT * FROM UninionedBankaHareketleri
			ORDER BY Tarih DESC
			"""
	rows = []
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = cursor.fetchall()		
	return rows


def rapor_kasa_durumu():
	query = """
			WITH
			
			UnionedKasaHareketleri AS(
			--satis
			select tutar from koopmuhasebe_satisstokhareketleri 
			UNION ALL
			--gider
			select sum(-tutar) from koopmuhasebe_gider where odeme_araci=2
			UNION ALL
			--virman kasaya giris
			select sum(tutar) from koopmuhasebe_virmanveduzeltme WHERE giris_hesabi =2 
			UNION ALL
			--virman kasadan cikis
			select sum(-tutar) from koopmuhasebe_virmanveduzeltme WHERE cikis_hesabi =2 
			UNION ALL
			-- ureticiye odeme
			select sum(borcmu_alacakmi*tutar) from koopmuhasebe_borcalacak where odeme_araci=2
			UNION ALL
			-- uye odeme tahsilat
			select sum(odememi_tahsilatmi*tutar) from koopmuhasebe_kisiodemetahsilat where odeme_araci=2

			)

			SELECT SUM(tutar) FROM UnionedKasaHareketleri
			"""
	yekun = 0
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = cursor.fetchall()
		yekun = rows[0][0]
	return yekun

def rapor_banka_durumu():
	query = """
			WITH
			UnionedBankaHareketleri AS(
			--gider
			select sum(-tutar) as tutar from koopmuhasebe_gider where odeme_araci=1
			UNION ALL
			--virman bankaya giris
			select sum(tutar) from koopmuhasebe_virmanveduzeltme WHERE giris_hesabi =1 
			UNION ALL
			--virman bankadan cikis
			select sum(-tutar) from koopmuhasebe_virmanveduzeltme WHERE cikis_hesabi =1 
			UNION ALL
			-- ureticiye odeme
			select sum(borcmu_alacakmi*tutar) from koopmuhasebe_borcalacak where odeme_araci=1
			UNION ALL
			-- uyelere odeme/tahsilat
			select sum(odememi_tahsilatmi*tutar) from koopmuhasebe_kisiodemetahsilat where odeme_araci=1
			)

			SELECT SUM(tutar) FROM UnionedBankaHareketleri
			"""
	yekun = 0
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = cursor.fetchall()
		yekun = rows[0][0]
	return yekun


def stokta_varolan_urunler():
	query = """
    			WITH
    			UnionedTable AS(	
    				select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
    				UNION ALL
    				select urun_id,miktar from koopmuhasebe_stokgirisi	
    			),
    			UnionedTableGrouped AS(	
    				select urun_id,SUM(miktar) as miktar from UnionedTable
    				GROUP BY urun_id	
    			)
    			SELECT  koopmuhasebe_urun.id ,koopmuhasebe_urun.urun_adi,uretici_adi 
                FROM UnionedTableGrouped                
    			INNER JOIN koopmuhasebe_urun ON UnionedTableGrouped.urun_id = koopmuhasebe_urun.id
                INNER JOIN koopmuhasebe_uretici ON koopmuhasebe_urun.uretici_id = koopmuhasebe_uretici.id
    			WHERE miktar > 0
    			ORDER BY koopmuhasebe_urun.urun_adi ASC
    			"""
	yekun = 0
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0], row[1], row[2], ])
	return rows

def urunler_ve_fiyatlari():
	query = """    			
			WITH 
				CTE AS 
				(
					SELECT urun_id, 
							zaman,
							fiyat,
							ROW_NUMBER() OVER (PARTITION BY urun_id ORDER BY zaman DESC)
					FROM koopmuhasebe_urun_fiyat
				)
			SELECT   koopmuhasebe_urun.id, koopmuhasebe_urun.urun_adi, koopmuhasebe_uretici.uretici_adi,  CTE.fiyat 
			FROM koopmuhasebe_urun
			INNER JOIN CTE ON CTE.urun_id = koopmuhasebe_urun.id
			INNER JOIN koopmuhasebe_uretici ON koopmuhasebe_urun.uretici_id = koopmuhasebe_uretici.id
			WHERE CTE.row_number =1
			"""
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0], row[1], row[2],row[3], ])
	return rows



def urunlerin_guncel_fiyatlari(_tarih):
	query = """
    			WITH 
					CTE AS 
					(
						SELECT urun_id, 
								zaman,
								fiyat,
								ROW_NUMBER() OVER (PARTITION BY urun_id ORDER BY zaman DESC)
						FROM koopmuhasebe_urun_fiyat
						WHERE ZAMAN < '{tarih}'
					)
					
				SELECT   koopmuhasebe_urun.id, CTE.fiyat from koopmuhasebe_urun
				INNER JOIN CTE 
				ON CTE.urun_id = koopmuhasebe_urun.id
				WHERE CTE.row_number =1
    		"""	
	query = query.format(tarih=_tarih)
	rows = []
	with connection.cursor() as cursor:
		cursor.execute(query)
		#rowz = cursor.fetchall()
		#a=1
		'''
		for row in cursor.fetchall():
			rows.append([ row[0], row[1],])
		'''
		columns = [col[0] for col in cursor.description]		
		return [
        	dict(zip(columns, row))
        	for row in cursor.fetchall()]		
		


def rapor_urun_satis_haftalik(urunID):
	query = """SELECT 
				date_part('year', tarih::date) as yearly,
				date_part('week', tarih::date) AS weekly,
				SUM(miktar)
			FROM koopmuhasebe_satis 
			INNER JOIN koopmuhasebe_satisstokhareketleri
			ON koopmuhasebe_satisstokhareketleri.satis_id = koopmuhasebe_satis.id 
			WHERE urun_id = {urunID}
			GROUP BY yearly, weekly 
			ORDER BY yearly, weekly;
			"""
	query = query.format(urunID=urunID)
	
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([ int(row[0]), int(row[1]),row[2],])
			#pdb.set_trace()			
	lastRow = (0,0,0,0)
	tuple = (rows,lastRow)
	return tuple
	
	
def stogu_azalan_urunler():
	query = """
	WITH
	UrunStokHareketleriUnion AS(	
		select urun_id,(miktar*-1) as miktar from koopmuhasebe_satisstokhareketleri
		UNION ALL
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


def rapor_uretici_borclari():
	query = """
	SELECT  uretici_adi,  SUM((tutar*borcmu_alacakmi)) as borc FROM koopmuhasebe_borcalacak
		INNER JOIN koopmuhasebe_uretici ON koopmuhasebe_uretici.id = koopmuhasebe_borcalacak.uretici_id
		GROUP BY uretici_adi
		ORDER BY uretici_adi ASC
	"""
	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = []
		for row in cursor.fetchall():
			rows.append([row[0], row[1], ])
	return rows