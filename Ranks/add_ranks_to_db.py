from Ranks.models import Rank  # zamień "game" na nazwę swojej aplikacji

levels = [
    ("Nowy Rekrut", 0),
    ("Obserwator Zdarzeń", 120),
    ("Stażysta Biura Śledczego", 300),
    ("Technik Kryminalny", 550),
    ("Młodszy Analityk", 850),
    ("Tropiciel Śladów", 1200),
    ("Śledczy Operacyjny", 1600),
    ("Agent Terenowy", 2100),
    ("Ekspert Dochodzeniowy", 2700),
    ("Starszy Detektyw", 3400),
    ("Specjalista Profilowania", 4200),
    ("Analityk Spraw Nierozwiązanych", 5100),
    ("Detektyw Wydziału Zabójstw", 6200),
    ("Koordynator Dochodzeń", 7400),
    ("Starszy Agent Wywiadu", 8700),
    ("Naczelny Śledczy", 10100),
    ("Strateg Operacyjny", 11600),
    ("Główny Kryminalistyk", 13200),
    ("Architekt Profilów Psychologicznych", 14900),
    ("Szef Jednostki Specjalnej", 16700),
    ("Dyrektor Operacyjny Spraw Kryminalnych", 18600),
    ("Elitarny Detektyw Federalny", 20600),
    ("Komisarz Dochodzeniowy", 22700),
    ("Inspektor Naczelny", 24900),
    ("Strateg Spraw Najwyższej Wagi", 27200),
    ("Analityk Kryminalny Klasy Alfa", 29600),
    ("Specjalista ds. Operacji Tajnych", 32100),
    ("Komendant Wydziału Śledczego", 34700),
    ("Elitarny Rozwiązywacz Spraw Niemożliwych", 37400),
    ("Legenda Kryminalistyki", 40000),
]

for name, exp in levels:
    Rank.objects.get_or_create(name=name, defaults={"required_exp": exp})

print("✅ Wszystkie poziomy zostały dodane.")
