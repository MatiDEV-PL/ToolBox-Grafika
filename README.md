# ToolBox-Grafika

Biblioteka narzędzi geometrycznych w Pythonie: punkty, odcinki skierowane,
przecięcia i kontener obiektów.

## Testy

Testy leżą w folderze `testy/`. Uruchamiasz je z głównego katalogu projektu.

**Wszystkie testy:**

```powershell
.\.venv\Scripts\python.exe -m pytest
```

**Jeden plik:**

```powershell
.\.venv\Scripts\python.exe -m pytest testy/test_geometria.py
```

**Jeden test:**

```powershell
.\.venv\Scripts\python.exe -m pytest testy/test_geometria.py::test_dlugosc_odcinka
```

Wyniki wypisują się w terminalu — przy każdym teście widać, co zostało
policzone i z jakim wynikiem. Kolor i krótkie komunikaty błędów są już
ustawione w `pyproject.toml`, więc nie trzeba dopisywać flag.

## Wymagania

Python 3.9+ oraz `pytest`
