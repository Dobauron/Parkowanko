from rest_framework.exceptions import ValidationError
from better_profanity import profanity
from rest_framework.exceptions import ValidationError
from ..models import Review
from functools import wraps


# ---------------- Choice validator (uniwersalny) ---------------- #

def choice_validator(choices, field_name="value", allow_null=False):
    valid_choices = [choice[0] for choice in choices]

    def decorator(func):
        @wraps(func)
        def wrapper(value):
            if allow_null and value in (None, ""):
                return value

            if value not in valid_choices:
                raise ValidationError({
                    field_name: f"Niepoprawna wartość. Dozwolone: {valid_choices}"
                })

            return func(value)
        return wrapper
    return decorator


@choice_validator(
    choices=Review.Attribiutes.choices,
    field_name="property",
    allow_null=False
)
def validate_attribiutes(value):
    return value


@choice_validator(
    choices=Review.Occupancy.choices,
    field_name="occupancy",
    allow_null=True
)
def validate_occupancy(value):
    return value



# ---------------- Walidator przekleństw ---------------- #

# Ładujemy własne polskie przekleństwa (default angielskie nie wystarczą)
POLISH_BAD_WORDS = [
    "kurwa", "chuj", "pizda", "jebac", "jebać", "skurwiel",
    "kutas", "pierdol", "spierdalaj", "debil", "idiota",
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
    @wraps(func)
    def wrapper(self, attrs):
        user = self.context["request"].user
        parking_point = attrs.get("parking_point")
        if self.instance is None:
            if Review.objects.filter(user=user, parking_point=parking_point).exists():
                raise ValidationError({
                    "detail": "Możesz dodać tylko jedną recenzję dla tego parking point."
                })
        return func(self, attrs)
    return wrapper