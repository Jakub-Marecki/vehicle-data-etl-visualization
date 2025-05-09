# ETL Pipeline z API do Teradata i wizualizacja w Power BI

## Spis treści 

1. [Opis projektu](#opis-projektu)
2. [Struktura repozytorium](#struktura-repozytorium)
3. [Wymagania](#wymagania)
4. [Instalacja i konfiguracja](#instalacja-i-konfiguracja)
5. [Proces ETL](#proces-etl)

   * [1. Ekstrakcja (API)](#1-ekstrakcja-api)
   * [2. Transformacja danych](#2-transformacja-danych)
   * [3. Ładowanie do Teradata](#3-ładowanie-do-teradata)
6. [Wizualizacja w Power BI](#wizualizacja-w-power-bi)
7. [Uruchomienie](#uruchomienie)
8. [Kontrybucje](#kontrybucje)
9. [Licencja](#licencja)

---

## Opis projektu

Celem projektu jest zbudowanie end-to-endowego procesu ETL:

1. **Ekstrakcja**: pobieranie miesięcznych danych rejestracji pojazdów z publicznego API CEPiK.
2. **Transformacja**: spłaszczanie i czyszczenie danych (JSON → CSV) przy użyciu biblioteki pandas oraz zastosowanie definicji kolumn z pliku MLD.
3. **Ładowanie**: załadowanie przetworzonych danych do hurtowni Teradata.
4. **Wizualizacja**: stworzenie raportu w Power BI do analizy trendów rejestracji.

## Struktura repozytorium

```plaintext
├── README.md                     # Niniejszy plik
├── Pobieranie-danych.py          # Skrypt Python do ekstrakcji danych z API
├── data_vehicle_v3_cleaned.csv   # Wynikowy plik CSV po transformacji
├── pojazdy_fixed.mld             # Definicje pól i mapowania formatu MLD
├── sql-vehicle.sql               # Skrypt SQL do stworzenia tabeli i załadowania danych w Teradata
└── Raport-vehicle-powerbi.pbix   # Plik Power BI z wizualizacją
```

## Wymagania

* Python 3.8+
* Biblioteki Python:

  * `requests`
  * `pandas`
  * `python-dateutil`
* Plik MLD (`pojazdy_fixed.mld`) z definicjami i mapowaniem kolumn
* Dostęp do instancji Teradata (poświadczenia, host, port)
* Power BI Desktop (wersja 2.XX lub wyższa)

## Instalacja i konfiguracja

1. Sklonuj repozytorium:

   ```bash
   git clone https://github.com/twoje-konto/etl-teradata-powerbi.git
   cd etl-teradata-powerbi
   ```
2. Utwórz i aktywuj wirtualne środowisko:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```
3. Zainstaluj zależności:

   ```bash
   pip install -r requirements.txt
   ```
4. Skonfiguruj połączenie do Teradata:

   * Utwórz plik `teradata_config.json` obok skryptów:

     ```json
     {
       "host": "<adres_host>",
       "username": "<użytkownik>",
       "password": "<hasło>",
       "database": "<schemat>"
     }
     ```

## Proces ETL

### 1. Ekstrakcja (API)

W pliku `Pobieranie-danych.py` znajduje się klasa i funkcje:

* **SSLContextAdapter**: adapter HTTPS z niestandardowym poziomem zabezpieczeń.
* **fetch\_monthly**: pobiera dane dla pojedynczego województwa i miesiąca.
* **main**: iteruje przez wszystkie województwa i miesiące zdefiniowane w tablicy `WOJEWODZTWA`, zbiera rekordy, a następnie spłaszcza strukturę JSON.

Parametry:

* Rok docelowy: definiowany w zmiennej `year` (domyślnie 2019).
* Zakres dat: od pierwszego do ostatniego dnia każdego miesiąca.

Wynik: surowy plik CSV zapisany w katalogu wyjściowym (`OUT_DIR`).

### 2. Transformacja danych

* Użycie `pandas.json_normalize` do przekształcenia zagnieżdżonego JSON w płaską tabelę.
* Wczytanie pliku `pojazdy_fixed.mld` w celu pobrania definicji kolumn i mapowania wartości.
* Czyszczenie danych (usuwanie duplikatów, uzupełnianie braków) odbywa się w kodzie.
* Finalny CSV: `data_vehicle_v3_cleaned.csv`.

### 3. Ładowanie do Teradata

Skrypt SQL (`sql-vehicle.sql`) zawiera:

1. Definicję tabeli docelowej (`CREATE TABLE …`).
2. Instrukcję `LOAD` lub `INSERT` z wykorzystaniem BTEQ/TPump.

Przykładowe polecenie w terminalu:

```bash
bteq < sql-vehicle.sql
```

Upewnij się, że w pliku `teradata_config.json` ustawiono prawidłowe parametry połączenia, a w skrypcie SQL odwołujesz się do zmiennych środowiskowych.

## Wizualizacja w Power BI

* Otwórz plik `Raport-vehicle-powerbi.pbix` w Power BI Desktop.
* Źródło danych: połączenie do hurtowni Teradata lub plik CSV `data_vehicle_v3_cleaned.csv`.
* Raport zawiera:

  * Trend miesięcznych rejestracji.
  * Porównanie liczb nowych i zarejestrowanych pojazdów.
  * Podział wg marki i modelu.

Możesz filtrować dane po miesiącu, marce, województwie itp.

## Uruchomienie

1. Wyeksportuj dane:

   ```bash
   python Pobieranie-danych.py
   ```
2. Załaduj do Teradata:

   ```bash
   bteq < sql-vehicle.sql
   ```
3. Otwórz Power BI, odśwież dane i eksploruj raport.

## Kontrybucje

Wszelkie uwagi, poprawki i propozycje usprawnień mile widziane. Proszę otwierać issues oraz pull requesty.

## Licencja

Projekt udostępniony na licencji MIT. Zobacz plik `LICENSE`.
