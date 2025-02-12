from rest_framework.exceptions import ValidationError
from ..models import ParkingPointReport

def validate_reason(value):
    """
    Waliduje, czy podana wartość `reason` znajduje się w dozwolonych opcjach.
    """
    valid_choices = [choice[0] for choice in ParkingPointReport.ReportReason.choices]
    if value not in valid_choices:
        raise ValidationError({"error":f"Niepoprawny powód zgłoszenia. Dostępne opcje: {valid_choices}"})
    return value
