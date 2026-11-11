# ToolBox-Grafika

Biblioteka narzędzi geometrycznych w Pythonie: punkty, odcinki skierowane,
przecięcia i kontener obiektów.

## Wymagania

Python 3.9+ oraz `pytest` (opcjonalnie `numpy`, patrz `[project.optional-dependencies]`
w `pyproject.toml`).

## Instalacja środowiska

**Windows (PowerShell):**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

**Linux / macOS (bash, zsh):**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
```

Jeśli masz zainstalowane [`uv`](https://docs.astral.sh/uv/), oba kroki robi jedna
komenda — sama utworzy `.venv` i doinstaluje zależności testowe:

```bash
uv run --extra test pytest
```

## Testy

Testy leżą w folderze `testy/`. Uruchamiasz je z głównego katalogu projektu.
Ścieżka do interpretera zależy od systemu — na Windowsie jest
`.venv\Scripts\python.exe`, na Linuksie i macOS `.venv/bin/python`.

### Windows (PowerShell)

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

### Linux

**Wszystkie testy:**

```bash
.venv/bin/python -m pytest
```

**Jeden plik:**

```bash
.venv/bin/python -m pytest testy/test_geometria.py
```

**Jeden test:**

```bash
.venv/bin/python -m pytest testy/test_geometria.py::test_dlugosc_odcinka
```

**Skrót przez `uv`** (nie wymaga aktywacji środowiska):

```bash
uv run pytest
uv run pytest testy/test_geometria.py::test_dlugosc_odcinka
```

Wyniki wypisują się w terminalu — przy każdym teście widać, co zostało
policzone i z jakim wynikiem. Kolor i krótkie komunikaty błędów są już
ustawione w `pyproject.toml`, więc nie trzeba dopisywać flag.
