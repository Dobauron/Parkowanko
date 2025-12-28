from rest_framework.exceptions import ValidationError
from better_profanity import profanity
from rest_framework.exceptions import ValidationError
from ..models import Review
from functools import wraps
from rest_framework import serializers


# ---------------- Choice validator (uniwersalny) ---------------- #


def choice_validator(choices, field_name="value", allow_null=False):
    valid_choices = [choice[0] for choice in choices]

    def decorator(func):
        @wraps(func)
        def wrapper(value):
            if allow_null and value in (None, ""):
                return value

            if value not in valid_choices:
                raise ValidationError(
                    {field_name: f"Niepoprawna wartość. Dozwolone: {valid_choices}"}
                )

            return func(value)

        return wrapper

    return decorator


@choice_validator(
    choices=Review.Attributes.choices, field_name="property", allow_null=False
)
def validate_attributes(value):
    return value


@choice_validator(
    choices=Review.Occupancy.choices, field_name="occupancy", allow_null=True
)
def validate_occupancy(value):
    return value


# ---------------- Walidator przekleństw ---------------- #

# Ładujemy własne polskie przekleństwa (default angielskie nie wystarczą)
POLISH_BAD_WORDS = [
    "kurwa",
    "chuj",
    "pizda",
    "jebac",
    "jebać",
    "skurwiel",
    "kutas",
    "pierdol",
    "spierdalaj",
    "debil",
    "idiota",
]

profanity.load_censor_words(POLISH_BAD_WORDS)


def validate_no_profanity(value):
    """
    Waliduje czy string nie zawiera przekleństw.
    """
    if value and profanity.contains_profanity(value):
        raise ValidationError("Opis zawiera niedozwolone słowa.")

    return value


# ---------------- Dekorator 2: unikalność recenzji ---------------- #


def validate_unique_review(func):
    """
    Walidator sprawdzający, czy użytkownik nie dodał już recenzji dla danego parking point.
    """

    @wraps(func)
    def wrapper(self, attrs):
        # Spróbuj pobrać parking_point z kontekstu (domyślna metoda w DRF przy read_only)
        parking_point = self.context.get("parking_point")

        if parking_point is None:
            # Jeśli nie ma w kontekście, sprawdź w attrs (np. w testach lub niestandardowych przypadkach)
            parking_point = attrs.get("parking_point")

        if parking_point is None:
            raise serializers.ValidationError(
                {"parking_point": "Nie można znaleźć obiektu parking_point."}
            )

        user = self.context["request"].user

        if self.instance is None:  # tylko przy tworzeniu nowej recenzji
            exists = Review.objects.filter(
                user=user, parking_point=parking_point
            ).exists()
            if exists:
                raise serializers.ValidationError(
                    {
                        "detail": "Możesz dodać tylko jedną recenzję dla tego parking point."
                    }
                )

        return func(self, attrs)

    return wrapper
