#!/bin/bash

# Instalacja Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Dodanie Poetry do PATH
export PATH="$HOME/.local/bin:$PATH"

# Konfiguracja Poetry, aby nie tworzył własnych środowisk wirtualnych
poetry config virtualenvs.create false

# Instalacja zależności
poetry install --no-root
