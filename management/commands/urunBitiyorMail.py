from django.core.management.base import BaseCommand, CommandError
from django.core.mail import send_mail
from koopmuhasebe.reporting import stogu_azalan_urunler

class Command(BaseCommand):
	def handle(self, *args, **options):
		rows = stogu_azalan_urunler()		
		stoguAzalanUrunler = ""
		for row in rows:
			stoguAzalanUrunler = stoguAzalanUrunler + str(row[0]) + "\n"
			#self.stdout.write(row, ending='')
		
		giris_mesaji = "Asagidaki urunlerin stogu azaldi:\n"
		if stoguAzalanUrunler != "":
			self.stdout.write(stoguAzalanUrunler, ending='')
			send_mail('Stogu azalan urunler vaaaar', giris_mesaji + stoguAzalanUrunler, 'muhasebe@kadikoykoop.org', ['arasefe@gmail.com'], fail_silently=False)
		