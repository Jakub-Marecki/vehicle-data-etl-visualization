# ETL Pipeline z API do Teradata i wizualizacja w Power BI

## Spis treści 

1. [Opis projektu](#opis-projektu)
2. [Struktura repozytorium](#struktura-repozytorium)
3. [Wymagania i instalacja](#wymagania-i-instalacja)
4. [Proces ETL](#proces-etl)

   * [1. Ekstrakcja (API)](#1-ekstrakcja-api)
   * [2. Transformacja danych](#2-transformacja-danych)
   * [3. Ładowanie do Teradata](#3-ładowanie-do-teradata)
   * [4. Zapytania SQL – analiza danych](#4-zapytania-sql--analiza-danych)
5. [Wizualizacja w Power BI](#wizualizacja-w-power-bi)

---

## Opis projektu

Celem projektu jest zbudowanie end-to-endowego procesu ETL:

1. **Ekstrakcja**: pobieranie miesięcznych danych rejestracji pojazdów z publicznego API CEPiK.
2. **Transformacja**: spłaszczenie i czyszczenie danych (JSON → CSV) przy użyciu biblioteki pandas.
3. **Ładowanie**: załadowanie przetworzonych danych do hurtowni Teradata przy użyciu narzędzia MLOAD.
4. **Wizualizacja**: stworzenie raportu w Power BI do analizy trendów rejestracji.

## Struktura repozytorium

```plaintext
├── README.md                     # Niniejszy plik
├── Pobieranie-danych.py          # Skrypt Python do ekstrakcji danych z API
├── data_vehicle_v3_cleaned.csv   # Wynikowy plik CSV po transformacji
├── pojazdy_fixed.mld             # Definicje pól i mapowania formatu MLD
├── sql-vehicle.sql               # Skrypt SQL do tworzenia tabel i analizy danych
└── Raport-vehicle-powerbi.pbix   # Plik Power BI z wizualizacją
```

## Wymagania i instalacja

Aby uruchomić projekt, wystarczy:

* Python 3.8+
* Biblioteki (`requests`, `pandas`, `python-dateutil`) zdefiniowane w `requirements.txt`
* Skonfigurowany plik `teradata_config.json` z danymi połączenia do Teradata
* (Opcjonalnie) Power BI Desktop lub dostęp do CSV `data_vehicle_v3_cleaned.csv`

Instalacja środowiska:

```bash
python -m venv venv       # utworzenie wirtualnego środowiska
source venv/bin/activate  # aktywacja (Linux/macOS)
# venv\Scripts\activate # aktywacja (Windows)
pip install -r requirements.txt
```

## Proces ETL

### 1. Ekstrakcja (API)

W pliku `Pobieranie-danych.py` znajdują się:

* **SSLContextAdapter**: adapter HTTPS z niestandardowym poziomem zabezpieczeń.
* **fetch\_monthly**: pobieranie danych rejestracji pojazdów z API CEPiK dla wybranego województwa i miesiąca.
* **main**: iteracja przez wszystkie województwa i miesiące, zbieranie rekordów oraz spłaszczanie struktury JSON.

Parametry:

* `year` – rok danych (domyślnie 2019).
* Zakres od pierwszego do ostatniego dnia każdego miesiąca.

Efekt: surowy plik CSV zapisany w katalogu wyjściowym.

### 2. Transformacja danych

* `pandas.json_normalize` – spłaszczenie zagnieżdżonego JSON do formatu tabelarycznego.
* Czyszczenie: usuwanie duplikatów, uzupełnianie braków (imputacja wartości domyślnych).
* Finalny plik: `data_vehicle_v3_cleaned.csv`.

### 3. Ładowanie do Teradata

Do ładowania danych używane jest narzędzie **MLOAD** i plik definicji **`pojazdy_fixed.mld`** (Map Load Definition):

```bash
mload < ścieżka/do/pojazdy_fixed.mld
```

Plik MLD zawiera mapowanie kolumn, typy danych oraz instrukcje ładowania, co zapewnia spójność i automatyzację.

### 4. Zapytania SQL – analiza danych

W pliku `sql-vehicle.sql` znajdują się przykładowe zapytania:

* Tworzenie tabeli docelowej z odpowiednimi typami kolumn (`CREATE TABLE`).
* Ładowanie danych z tymczasowej tabeli.
* Analiza z użyciem funkcji okna (OVER):

  * Obliczanie 12-miesięcznej średniej ruchomej rejestracji,
  * Ranking miesięcy w ramach województw (RANK() OVER (PARTITION BY wojewodztwo ORDER BY liczba DESC)),
  * Cumulative Sum – SUM(liczba) OVER (PARTITION BY marka ORDER BY data ROWS UNBOUNDED PRECEDING).

Dodatkowo przykłady agregacji i filtrowania pozwalają na szybkie wyciąganie wniosków.

## Wizualizacja w Power BI

* Źródło danych: tabela SQL eksportowana do `dane_pojazdy_output.csv` lub bezpośrednie połączenie do Teradata.
* Raport zawiera:

  * Trend miesięcznych rejestracji w wykresie liniowym,
  * Porównanie nowych vs. zarejestrowanych pojazdów w wykresie słupkowym,
  * Podział liczby rejestracji wg marki i modelu (tabela i wykres kołowy).
* Interaktywne filtry: miesiąc, marka, województwo itp.

---
