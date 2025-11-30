# Code Green

> Plugin do PyCharm, który pomaga pisać kod przyjazny dla środowiska.

---

## Problem

Każde uruchomienie kodu to zużycie prądu. Prąd = emisja CO₂. W skali globalnej IT odpowiada za (4 - 10) % – tyle co lotnictwo. Programiści piszą kod, ale nie widzą jego wpływu na planetę.

Nieefektywny kod:
- zużywa więcej CPU
- działa dłużej 
- wymaga więcej energii
- generuje więcej CO₂

## Rozwiązanie

Plugin wbudowany w PyCharm, który:

1. Analizuje kod w czasie rzeczywistym – wykrywa nieefektywne wzorce

2. Mierzy rzeczywiste emisje – uruchamia kod i śledzi faktyczne zużycie energii oraz emisję CO₂

3. Pokazuje Eco Score – prosty wynik 0-100 z kolorowym wskaźnikiem

4. Podpowiada poprawki – podaje sugestię jak naprawić kod

---

## Integracja z AI (Junie)

Plugin został zaprojektowany z myślą o integracji z narzędziami AI, takimi jak Junie.

## Jak AI może to wykorzystać:

- Automatyczna refaktoryzacja – AI dostaje listę problemów z lokalizacją i sugestiami, może wygenerować poprawiony kod
- Priorytetyzacja – pole `co2_impact` pozwala AI skupić się na zmianach dających największy efekt
- Wyjaśnienia – AI może wytłumaczyć użytkownikowi dlaczego dany wzorzec jest nieefektywny
- Nauka – kontekst błędów pozwala AI uczyć się wzorców specyficznych dla danego projektu

Junie + Green Coding Assistant = automatyczna poprawa efektywności energetycznej kodu.


## Użyte technologie

### Python


[CodeCarbon](https://codecarbon.io/) | Śledzenie rzeczywistych emisji CO₂ podczas wykonywania kodu |
[eco-code-analyzer](https://pypi.org/project/eco-code-analyzer/) | Statyczna analiza kodu pod kątem efektywności energetycznej |

## Kotlin / IntelliJ Platform

Plugin zbudowany na 'IntelliJ Platform Plugin Template' – oficjalnym szablonie JetBrains do tworzenia pluginów.

- Annotator – podświetlanie problemów w edytorze w czasie rzeczywistym
- Tool Window – panel boczny z Eco Score
- Actions – komendy dostępne z menu kontekstowego i skrótów klawiszowych


## Instalacja

# Zainstaluj zależności Python
pip install codecarbon eco-code-analyzer

# Zbuduj plugin
cd green_code_V1.0
./gradlew buildPlugin

# Plugin znajdziesz w: build/distributions/
```



Projekt stworzony podczas BHL25 Hackathon przez MOAI w kategorii AI.


## Licencja

MIT
