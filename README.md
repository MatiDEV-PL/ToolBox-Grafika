# ToolBox-Grafika

Biblioteka narzędzi geometrycznych w Pythonie: punkty, odcinki skierowane,
orientacja punktów, przecięcia, sortowanie leksykograficzne, kontener obiektów
oraz zapis i odczyt danych z pliku.

Biblioteka nie ma żadnych zależności zewnętrznych — wystarczy Python 3.9+.

## Uruchomienie testów

Testy leżą w folderze `testy/` i uruchamia się je z głównego katalogu projektu.

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

Przy każdym teście widać, co zostało policzone i z jakim wynikiem. Kolor
i krótkie komunikaty błędów są ustawione w `pyproject.toml`, więc nie trzeba
dopisywać flag. Polskie znaki w konsoli obsługuje `testy/conftest.py`.

## Import

Kod leży w `src/toolbox`. W tym projekcie katalog `src` jest dopisany do
ścieżki przez plik `.pth` w venv, więc działa po prostu:

```python
import toolbox
from toolbox import Punkt, Obiekt, Kontener, Dane, ZapiszDane
```

## Punkty

Punkt to para współrzędnych i kolor (liczba całkowita: 0 brak, 1 niebieski,
2 czerwony, 3 zielony, powyżej 3 — kolory użytkownika).

```python
from toolbox import Punkt, punkt, PUNKT_ROZBIEGAJACY, PUNKT_NIESKONCZONOSCI

p = Punkt(1.5, -2, 2)
p.wspolrzedne   # (1.5, -2.0)
p.kolor         # 2

punkt(0, 0)     # Punkt(x=0.0, y=0.0, c=0)
```

Punkty specjalne:

| Stała | Wartość |
|---|---|
| `PUNKT_ROZBIEGAJACY` | `(nan, nan, 0)` — brak punktu |
| `PUNKT_NIESKONCZONOSCI` | `(-inf, inf, 0)` — odcinki nachodzą na siebie |

Sprawdzenie: `p.jest_nan`, `p.jest_nieskonczony`, `p.jest_specjalny`.

## Odcinki skierowane

Odcinek (`Obiekt`) to początek, koniec i kolor. Kolejność punktów ma znaczenie.

```python
from toolbox import Obiekt

a = Obiekt.z_wspolrzednych(0, 0, 3, 4, kolor=1)
a.dlugosc()                      # 5.0
a.poczatek, a.koniec             # Punkty

b = Obiekt.z_wspolrzednych(3, 4, 6, 8)
a.tuli_z(b)                      # True - stykają się końcami
a.na_odcinku(Punkt(1.5, 2))      # True
a.jako_parametryka.dlugosc()     # to samo, w zapisie punkt + wektor
```

`tuli_z` obsługuje trzy przypadki: przecięcie w środku, dotknięcie końcami
i nachodzenie odcinków współliniowych.

## Orientacja punktu względem odcinka

Wartości: **−1 lewa strona, 0 współliniowo, 1 prawa**.
Kierunek prostej jest zgodny z kierunkiem odcinka.

```python
from toolbox import get_orientacja, strona_punktu, CCW, zakret

get_orientacja(0, 0, 10, 0, 5, 5)    # -1  (punkt nad odcinkiem = lewa)
get_orientacja(0, 0, 10, 0, 5, -5)   #  1  (punkt pod = prawa)
get_orientacja(0, 0, 10, 0, 5, 0)    #  0  (współliniowo)

odcinek = Obiekt.z_wspolrzednych(-1, 0, 1, 0)
strona_punktu(odcinek, Punkt(0, 1))  # -1
```

Zakręt trzech punktów:

```python
CCW(Punkt(0, 0), Punkt(10, 0), Punkt(5, 5))    # True  - zakręt w lewo
CCW(Punkt(0, 0), Punkt(10, 0), Punkt(5, -5))   # False - zakręt w prawo
zakret(Punkt(0, 0), Punkt(10, 0), Punkt(5, -5))  # -1 (1 lewo, -1 prawo, 0 prosto)
```

Do porównań zmiennoprzecinkowych służy stała `EPS = 1e-9` — bez niej punkt
matematycznie leżący na prostej wypada jako „po jednej ze stron".

## Sortowanie leksykograficzne

`SortLex(punkty, ord)` — `ord` to dwie litery. Pierwsza to oś i kierunek
główny, druga poboczny:

* `L` — od lewej, `R` — od prawej (oś X)
* `D` — od dołu, `U` — od góry (oś Y)

```python
from toolbox import SortLex, Punkt

p = [Punkt(2, 1), Punkt(1, 5), Punkt(1, -2)]

SortLex(p, "LD")   # [(1, -2), (1, 5), (2, 1)]  od lewej, potem od dołu
SortLex(p, "LU")   # [(1, 5), (1, -2), (2, 1)]  od lewej, potem od góry
SortLex(p, "UL")   # [(1, 5), (2, 1), (1, -2)]  od góry, potem od lewej
```

Dostępne są `LD`, `LU`, `RD`, `RU`, `DL`, `DR`, `UL`, `UR`. Inna wartość
zgłasza `ValueError`.

## Kontener

Zbiera punkty i odcinki w jednej liście, z jednakowym interfejsem.

```python
from toolbox import Kontener, Punkt, Obiekt

k = Kontener()
k.dodaj(Punkt(0, 0, 1))
k.dodaj(Obiekt.z_wspolrzednych(0, 0, 5, 0, kolor=2))

len(k)                 # 2
k.punkty()             # [Punkt(...)]
k.odcinki()            # [Obiekt(...)]
k.wedlug_koloru(1)     # obiekty w kolorze 1
k.specjalne()          # punkty nan i nieskończoności (też końce odcinków)
list(k)                # iteracja
```

## Przecięcia

```python
from toolbox import punkt_przeciecia, czesc_wspolna, oblicz_przeciecia

a = Obiekt.z_wspolrzednych(0, 0, 10, 0)
b = Obiekt.z_wspolrzednych(5, -5, 5, 5)

punkt_przeciecia(a, b).wspolrzedne   # (5.0, 0.0)
oblicz_przeciecia([a, b])            # wszystkie pary (naiwnie, każdy z każdym)
czesc_wspolna(a, b)                  # None, bo się nie nakładają
```

Wynik `punkt_przeciecia`:

| Sytuacja | Wynik |
|---|---|
| jeden punkt wspólny | zwykły punkt |
| brak przecięcia | `PUNKT_ROZBIEGAJACY` (nan, nan) |
| nachodzenie na siebie | `PUNKT_NIESKONCZONOSCI` (-inf, inf) |

## Zapis i odczyt plików

Plik jest tekstowy i dzieli się na sekcje: `[info]`, `[points c]`,
`[segments c]`, `[polygon c]`, `[intersections]`, `[side]`. Linie zaczynające
się od `#` to komentarze.

Podstawowe funkcje:

```python
from toolbox import InfoDanych, WczytajDane, ZapiszDane, wypisz_info, wypisz_dane

InfoDanych("dane.txt")     # [('info', ['Moj zestaw']), ('points 0', []), ...]
WczytajDane("dane.txt")    # Dane
ZapiszDane("kopia.txt", dane)               # zapisuje wszystko
ZapiszDane("tylko.txt", dane, ["points"])   # zapisuje wybrane sekcje

wypisz_info("dane.txt")    # wypisuje sekcje i komentarze na konsolę
wypisz_dane(dane)          # wypisuje liczbę punktów, odcinków itd.
```

`InfoDanych` zwraca **listę par**, nie słownik — bo ta sama sekcja może
wystąpić kilka razy (np. `[info]` na początku i na końcu pliku). Puste linie
na końcu sekcji są obcinane.

Zapis całego zestawu danych:

```python
from toolbox import Dane, Punkt, Obiekt, Strona, oblicz_przeciecia, ZapiszDane

dane = Dane(info=["Moj zestaw"])
dane.kontener.dodaj(Punkt(0, 0, 0))
dane.kontener.dodaj(Obiekt.z_wspolrzednych(0, 0, 10, 0, kolor=1))
dane.przeciecia = oblicz_przeciecia(dane.kontener.odcinki())
dane.strony.append(Strona(Obiekt.z_wspolrzednych(-1, 0, 1, 0), Punkt(0, 1), -1))

ZapiszDane("dane.txt", dane)
```

Plik wygląda tak:

```
[info]
# Moj zestaw

[points 0]
      0.0       0.0

[segments 1]
      0.0       0.0      10.0       0.0

[side]
# odcinek (px py qx qy)  punkt (x y)  strona: -1 lewa, 1 prawa, 0 współliniowo
     -1.0       0.0       1.0       0.0        0.0       1.0  -1
```

Niżej poziomu plików są jeszcze `zapisz`, `wczytaj`, `do_tekstu` i `z_tekstu`
— `zapisz`/`wczytaj` działają tak samo jak `ZapiszDane`/`WczytajDane`,
a `do_tekstu`/`z_tekstu` operują na tekście, bez pliku.

### Zasady sekcji [intersections]

Wiersz ma 12 liczb: odcinek 1 (4 współrzędne), kolor 1, odcinek 2
(4 współrzędne), kolor 2, punkt przecięcia.

* `nan nan` — brak przecięcia
* `-inf inf` — odcinki nachodzą na siebie; zaraz po tym wierszu idzie
  dodatkowy wiersz z częścią wspólną w miejsce obu odcinków i `nan nan`
  na końcu

### Zasady sekcji [side]

7 liczb: odcinek (4 współrzędne), punkt (2 współrzędne), strona
(-1 lewa, 1 prawa, 0 współliniowo).

## Struktura projektu

```
src/toolbox/
    punkty.py      Punkt i punkty specjalne
    kolory.py      PodstawoweKolory
    geometria.py   Obiekt, Parametryka, Orientacja, CCW, SortLex
    kontener.py    Kontener
    pliki.py       format pliku i operacje I/O
    _version.py    wersja pakietu
testy/             testy pytest
```

## Wymagania

Python 3.9+ oraz `pytest` do testów. Biblioteka nie wymaga żadnych paczek.
