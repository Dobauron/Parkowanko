from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from parking_point.models import ParkingPoint

class Command(BaseCommand):
    help = 'Trwale usuwa punkty parkingowe, które zostały oznaczone do usunięcia ponad 30 dni temu.'

    def handle(self, *args, **options):
        # Obliczamy datę graniczną (30 dni temu)
        cutoff_date = timezone.now() - timedelta(days=30)

        # Znajdujemy punkty do usunięcia
        # Muszą mieć ustawioną datę i musi być ona starsza niż data graniczna
        points_to_delete = ParkingPoint.objects.filter(
            marked_for_deletion_at__isnull=False,
            marked_for_deletion_at__lt=cutoff_date
        )

        count = points_to_delete.count()

        if count > 0:
            self.stdout.write(f'Znaleziono {count} punktów parkingowych do trwałego usunięcia...')
            points_to_delete.delete()
            self.stdout.write(self.style.SUCCESS(f'Pomyślnie usunięto {count} punktów.'))
        else:
            self.stdout.write(self.style.SUCCESS('Nie znaleziono żadnych punktów do usunięcia.'))
