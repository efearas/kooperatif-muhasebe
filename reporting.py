from django.db import connection



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
