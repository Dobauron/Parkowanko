# app_name/validators.py

from rest_framework.exceptions import ValidationError
from ..models import Review


def validate_choice(value, choices, field_name="value", allow_null=False):
    """
    Uniwersalny validator dla pól opartych o Django TextChoices.
    """
    if allow_null and value in (None, ""):
        return value

    valid_choices = [choice[0] for choice in choices]

    if value not in valid_choices:
        raise ValidationError(
            {field_name: f"Niepoprawna wartość. Dozwolone opcje: {valid_choices}"}
        )

    return value


def validate_property(value):
    return validate_choice(
        value=value,
        choices=Review.Property.choices,
        field_name="property",
        allow_null=False,
    )


def validate_occupancy(value):
    return validate_choice(
        value=value,
        choices=Review.Occupancy.choices,
        field_name="occupancy",
        allow_null=True,
    )
