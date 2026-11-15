"""
Zapis i odczyt plików tekstowych z danymi geometrycznymi.

Plik składa się z sekcji. Każda zaczyna się od nagłówka w nawiasach
kwadratowych, a pod nim idą wiersze z liczbami. Linie zaczynające się od
# to komentarze, puste linie są pomijane.

    [info]                 tylko komentarze (opis zestawu, statystyki)
    [points c]             wiersz: x y                      (c = kolor punktów)
    [segments c]           wiersz: px py qx qy              (c = kolor odcinków)
    [intersections]        wiersz: odcinek1(px py qx qy c)  odcinek2(px py qx qy c)  x y
    [polygon c]            wiersz: x y                      (kolejne wierzchołki)
    [side]                 wiersz: px py qx qy  x y  strona (strona: -1, 0, 1)

Punkt przecięcia w sekcji [intersections]:
    zwykłe współrzędne -> odcinki mają jeden punkt wspólny
    nan nan            -> brak przecięcia          (PUNKT_ROZBIEGAJACY)
    -inf inf           -> odcinki nachodzą na siebie (PUNKT_NIESKONCZONOSCI)

Gdy odcinki nachodzą na siebie (punkt -inf inf), zaraz po tej linii idzie
dodatkowa linia z częścią wspólną w miejsce obu odcinków i nan nan na końcu:

    odcinek1  kolor1  odcinek2  kolor2  nan nan

gdzie oba "odcinki" to ta sama część wspólna, każdy w kolumnach swojego
odcinka. Czyli razem 12 liczb, tak samo jak w zwykłej linii.

Strona w sekcji [side]: -1 = punkt po lewej od odcinka p->q, 1 = po prawej,
0 = współliniowo.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from math import isinf, isnan, nan
from pathlib import Path
from typing import Callable, Hashable, Iterable, TypeVar, Union

from .geometria import EPS, Obiekt
from .kontener import Kontener
from .punkty import PUNKT_NIESKONCZONOSCI, PUNKT_ROZBIEGAJACY, Punkt

T = TypeVar("T")


class BladPliku(ValueError):
    """Plik z danymi ma zły format."""


# --- Struktury na dane z pliku -------------------------------------------

@dataclass
class Przeciecie:
    """Wynik przecięcia dwóch odcinków (jedna linia sekcji [intersections])."""
    a: Obiekt
    b: Obiekt
    punkt: Punkt  # zwykły punkt, PUNKT_ROZBIEGAJACY (brak) albo PUNKT_NIESKONCZONOSCI (nakładanie)
    # Gdy odcinki nachodzą na siebie, tu trafia część wspólna jako para końców.
    # W pliku jest to dodatkowa linia zaraz po tej z -inf inf.
    wspolna: tuple[Punkt, Punkt] | None = None


@dataclass
class Strona:
    """Po której stronie odcinka leży punkt (jedna linia sekcji [side])."""
    odcinek: Obiekt
    punkt: Punkt
    strona: int  # -1, 0 albo 1


@dataclass
class Wielokat:
    """Lista wierzchołków z kolorem (sekcja [polygon c])."""
    punkty: list[Punkt] = field(default_factory=list)
    kolor: int = 0


@dataclass
class Dane:
    """Wszystko co może być w pliku."""
    info: list[str] = field(default_factory=list)
    kontener: Kontener = field(default_factory=Kontener)
    przeciecia: list[Przeciecie] = field(default_factory=list)
    wielokaty: list[Wielokat] = field(default_factory=list)
    strony: list[Strona] = field(default_factory=list)


# --- Obliczenia potrzebne do wypełnienia sekcji --------------------------

def punkt_przeciecia(a: Obiekt, b: Obiekt) -> Punkt:
    """Punkt wspólny dwóch odcinków, w konwencji z pliku (patrz górę modułu)."""
    if not a.tuli_z(b):
        return PUNKT_ROZBIEGAJACY

    p, r = a.jako_parametryka, b.jako_parametryka
    d = p.dx * r.dy - p.dy * r.dx

    # Zamiast d == 0 używamy tolerancji, bo float bywa niedokładny
    if abs(d) <= EPS:
        # Odcinki leżą na jednej prostej. Wspólne punkty to te końce, które
        # leżą na drugim odcinku. Jeden taki punkt = dotknięcie końcami.
        kandydaci = {
            q.wspolrzedne for q in (a.poczatek, a.koniec) if b.na_odcinku(q)
        } | {
            q.wspolrzedne for q in (b.poczatek, b.koniec) if a.na_odcinku(q)
        }
        if len(kandydaci) == 1:
            x, y = next(iter(kandydaci))
            return Punkt(x, y)
        return PUNKT_NIESKONCZONOSCI

    t = ((r.x0 - p.x0) * r.dy - (r.y0 - p.y0) * r.dx) / d
    x, y = p.get_punkt(t)
    return Punkt(x, y)


def czesc_wspolna(a: Obiekt, b: Obiekt) -> tuple[Punkt, Punkt] | None:
    """Wspólna część dwóch odcinków jako para końców (albo None).

    Ma sens tylko dla odcinków nachodzących na siebie, czyli takich, które
    leżą na jednej prostej i pokrywają się na pewnym odcinku. Dotknięcie
    końcami daje jeden punkt, więc zwracamy None - to nie jest nakładanie.
    """
    if not a.tuli_z(b):
        return None

    p, r = a.jako_parametryka, b.jako_parametryka
    if abs(p.dx * r.dy - p.dy * r.dx) > EPS:
        return None  # nie są współliniowe

    kandydaci: list[Punkt] = []
    for q in (a.poczatek, a.koniec, b.poczatek, b.koniec):
        na_drugim = b.na_odcinku(q) if q in (a.poczatek, a.koniec) else a.na_odcinku(q)
        if na_drugim and q.wspolrzedne not in [k.wspolrzedne for k in kandydaci]:
            kandydaci.append(q)

    if len(kandydaci) < 2:
        return None  # tylko dotknięcie końcami, nie nakładanie

    kandydaci.sort(key=lambda q: (q.x, q.y))
    return (kandydaci[0], kandydaci[-1])


def strona_punktu(odcinek: Obiekt, punkt: Punkt) -> int:
    """-1 gdy punkt jest po lewej od odcinka, 1 po prawej, 0 gdy współliniowy."""
    o = odcinek.jako_parametryka.check_orientacja_punkt(punkt.x, punkt.y)
    # Orientacja ma już właściwe wartości (-1/0/1), więc tylko rzutujemy na int
    return int(o)


def oblicz_przeciecia(odcinki: Iterable[Obiekt]) -> list[Przeciecie]:
    """Przecięcia wszystkich par odcinków (naiwnie, każdy z każdym)."""
    lista = list(odcinki)
    wynik = []
    for i in range(len(lista)):
        for j in range(i + 1, len(lista)):
            a, b = lista[i], lista[j]
            punkt = punkt_przeciecia(a, b)
            # Przy nakładaniu dorzucamy jeszcze część wspólną
            wspolna = czesc_wspolna(a, b) if punkt.jest_nieskonczony else None
            wynik.append(Przeciecie(a, b, punkt, wspolna))
    return wynik


# --- Odczyt --------------------------------------------------------------

_NAGLOWEK = re.compile(r"^\[\s*(\w+)(?:\s+(-?\d+))?\s*\]$")
_SEKCJE = {"info", "points", "segments", "intersections", "polygon", "side"}


def _odcinek_z_liczb(v: list[float], kolor: int) -> Obiekt:
    return Obiekt.z_wspolrzednych(v[0], v[1], v[2], v[3], kolor=kolor)


def z_tekstu(tekst: str) -> Dane:
    """Czyta dane z tekstu w formacie opisanym na górze modułu."""
    dane = Dane()
    sekcja: str | None = None
    kolor = 0

    for nr, surowa in enumerate(tekst.splitlines(), start=1):
        linia = surowa.strip()
        if not linia:
            continue

        if linia.startswith("#"):
            if sekcja == "info":
                dane.info.append(linia[1:].strip())
            continue

        if linia.startswith("["):
            m = _NAGLOWEK.match(linia)
            if not m or m.group(1).lower() not in _SEKCJE:
                raise BladPliku(f"linia {nr}: nieznany nagłówek sekcji: {linia!r}")
            sekcja = m.group(1).lower()
            kolor = int(m.group(2) or 0)
            if sekcja == "polygon":
                dane.wielokaty.append(Wielokat(kolor=kolor))
            continue

        if sekcja is None:
            raise BladPliku(f"linia {nr}: dane przed pierwszym nagłówkiem sekcji")
        if sekcja == "info":
            raise BladPliku(f"linia {nr}: sekcja [info] może zawierać tylko komentarze (#)")

        try:
            v = [float(s) for s in linia.split()]  # float() rozumie też nan, inf, -inf
        except ValueError:
            raise BladPliku(f"linia {nr}: nie umiem zamienić na liczby: {linia!r}") from None

        oczekiwane = {"points": 2, "segments": 4, "intersections": 12, "polygon": 2, "side": 7}[sekcja]
        if len(v) != oczekiwane:
            raise BladPliku(
                f"linia {nr}: sekcja [{sekcja}] wymaga {oczekiwane} liczb, jest {len(v)}"
            )

        if sekcja == "points":
            dane.kontener.dodaj(Punkt(v[0], v[1], kolor))
        elif sekcja == "segments":
            dane.kontener.dodaj(_odcinek_z_liczb(v, kolor))
        elif sekcja == "polygon":
            dane.wielokaty[-1].punkty.append(Punkt(v[0], v[1], kolor))
        elif sekcja == "intersections":
            a = _odcinek_z_liczb(v[0:4], int(v[4]))
            b = _odcinek_z_liczb(v[5:9], int(v[9]))
            punkt = Punkt(v[10], v[11])
            # Linia zaraz po nakładaniu (punkt -inf inf) i zakończona nan nan
            # to linia z częścią wspólną, a nie kolejna para odcinków.
            poprzednie = dane.przeciecia[-1] if dane.przeciecia else None
            if (poprzednie is not None and poprzednie.punkt.jest_nieskonczony
                    and poprzednie.wspolna is None and punkt.jest_nan):
                poprzednie.wspolna = (a.poczatek, a.koniec)
            else:
                dane.przeciecia.append(Przeciecie(a, b, punkt))
        elif sekcja == "side":
            if v[6] not in (-1, 0, 1):
                raise BladPliku(f"linia {nr}: strona musi być -1, 0 albo 1, jest {v[6]}")
            dane.strony.append(Strona(_odcinek_z_liczb(v[0:4], 0), Punkt(v[4], v[5]), int(v[6])))

    return dane


def wczytaj(sciezka: Union[str, Path]) -> Dane:
    """Czyta dane z pliku."""
    return z_tekstu(Path(sciezka).read_text(encoding="utf-8"))


# --- Zapis ---------------------------------------------------------------

def _liczba(v: float) -> str:
    if isnan(v):
        return "nan"
    if isinf(v):
        return "inf" if v > 0 else "-inf"
    return repr(round(v, 6))


def _wiersz(*liczby: float) -> str:
    return " ".join(_liczba(v).rjust(9) for v in liczby)


def _grupuj(elementy: Iterable[T], klucz: Callable[[T], Hashable]) -> dict:
    grupy: dict = {}
    for e in elementy:
        grupy.setdefault(klucz(e), []).append(e)
    return grupy


def _wiersz_odcinka(o: Obiekt) -> str:
    return _wiersz(o.poczatek.x, o.poczatek.y, o.koniec.x, o.koniec.y)


def do_tekstu(dane: Dane) -> str:
    """Zamienia dane na tekst w formacie opisanym na górze modułu."""
    w: list[str] = []

    if dane.info:
        w.append("[info]")
        w += [f"# {linia}" if linia else "#" for linia in dane.info]
        w.append("")

    for kolor, pts in _grupuj(dane.kontener.punkty(), lambda p: p.c).items():
        w.append(f"[points {kolor}]")
        w += [_wiersz(p.x, p.y) for p in pts]
        w.append("")

    for kolor, odc in _grupuj(dane.kontener.odcinki(), lambda o: o.kolor).items():
        w.append(f"[segments {kolor}]")
        w += [_wiersz_odcinka(o) for o in odc]
        w.append("")

    if dane.przeciecia:
        w.append("[intersections]")
        w.append("# odcinek 1 (px py qx qy c)  odcinek 2 (px py qx qy c)  punkt przecięcia (x y)")
        w.append("# nan nan = brak przecięcia, -inf inf = odcinki nachodzą na siebie")
        w.append("# po nakładaniu dodatkowa linia: część wspólna w miejsce obu odcinków i nan nan")
        for pr in dane.przeciecia:
            a, b = pr.a, pr.b
            w.append(
                _wiersz_odcinka(a) + " " + str(int(a.kolor)).rjust(3) + "  "
                + _wiersz_odcinka(b) + " " + str(int(b.kolor)).rjust(3) + "  "
                + _wiersz(pr.punkt.x, pr.punkt.y)
            )
            # Przy nakładaniu dopisujemy część wspólną w kolumnach obu odcinków
            if pr.punkt.jest_nieskonczony:
                czesc = pr.wspolna or czesc_wspolna(a, b)
                if czesc is not None and czesc[0].wspolrzedne != czesc[1].wspolrzedne:
                    pocz, kon = czesc
                    wiersz_czesci = _wiersz_odcinka(Obiekt(pocz, kon))
                    w.append(
                        wiersz_czesci + " " + str(int(a.kolor)).rjust(3) + "  "
                        + wiersz_czesci + " " + str(int(b.kolor)).rjust(3) + "  "
                        + _wiersz(nan, nan)
                    )
        w.append("")

    for wielokat in dane.wielokaty:
        w.append(f"[polygon {wielokat.kolor}]")
        w += [_wiersz(p.x, p.y) for p in wielokat.punkty]
        w.append("")

    if dane.strony:
        w.append("[side]")
        w.append("# odcinek (px py qx qy)  punkt (x y)  strona: -1 lewa, 1 prawa, 0 współliniowo")
        for s in dane.strony:
            w.append(_wiersz_odcinka(s.odcinek) + "  " + _wiersz(s.punkt.x, s.punkt.y)
                     + " " + str(s.strona).rjust(3))
        w.append("")

    return "\n".join(w)


def zapisz(sciezka: Union[str, Path], dane: Dane) -> None:
    """Zapisuje dane do pliku."""
    Path(sciezka).write_text(do_tekstu(dane), encoding="utf-8")


# --- Odczyt nazw sekcji i wygodne I/O ----------------------------------------

def InfoDanych(sciezka: Union[str, Path]) -> list[tuple[str, list[str]]]:
    """Zwraca nazwy sekcji z pliku razem z ich komentarzami.

    Wynik to lista par (nazwa sekcji, lista komentarzy) w kolejności
    występowania w pliku. Lista, a nie słownik, bo ta sama sekcja może
    wystąpić kilka razy - np. [info], a potem znowu [info] na końcu.

    Nazwa sekcji jest zachowana tak, jak w pliku, czyli razem z numerem
    koloru (np. "points 0"). Komentarze są bez znaku # na początku,
    a puste linie na końcu sekcji są obcinane.
    """
    tekst = Path(sciezka).read_text(encoding="utf-8")

    sekcje: list[tuple[str, list[str]]] = []
    for surowa in tekst.splitlines():
        linia = surowa.strip()
        if not linia:
            continue
        if linia.startswith("["):
            if not _NAGLOWEK.match(linia):
                raise BladPliku(f"zły nagłówek sekcji: {linia!r}")
            sekcje.append((linia[1:-1].strip(), []))
            continue
        if linia.startswith("#") and sekcje:
            sekcje[-1][1].append(linia[1:].strip())

    # "bez końcowych pustych lini"
    wynik = []
    for nazwa, komentarze in sekcje:
        while komentarze and not komentarze[-1]:
            komentarze.pop()
        wynik.append((nazwa, komentarze))
    return wynik


def WczytajDane(sciezka: Union[str, Path]) -> Dane:
    """Wczytuje zawartość pliku do struktur danych.

    To ta sama operacja co wczytaj(), tylko pod inną nazwą.
    """
    return wczytaj(sciezka)


_SEKCJE_DO_ZAPISU = {"info", "points", "segments", "intersections", "polygon", "side"}


def _wybierz_sekcje(dane: Dane, sekcje: Iterable[str]) -> Dane:
    """Zwraca kopię danych zawierającą tylko wybrane sekcje."""
    wybrane = {str(s).strip().lower() for s in sekcje}
    nieznane = wybrane - _SEKCJE_DO_ZAPISU
    if nieznane:
        raise ValueError(
            f"nieznane sekcje: {', '.join(sorted(nieznane))}; "
            f"dostępne: {', '.join(sorted(_SEKCJE_DO_ZAPISU))}"
        )

    wynik = Dane()
    if "info" in wybrane:
        wynik.info = list(dane.info)
    if "points" in wybrane:
        for punkt in dane.kontener.punkty():
            wynik.kontener.dodaj(punkt)
    if "segments" in wybrane:
        for odcinek in dane.kontener.odcinki():
            wynik.kontener.dodaj(odcinek)
    if "intersections" in wybrane:
        wynik.przeciecia = list(dane.przeciecia)
    if "polygon" in wybrane:
        wynik.wielokaty = list(dane.wielokaty)
    if "side" in wybrane:
        wynik.strony = list(dane.strony)
    return wynik


def ZapiszDane(
    sciezka: Union[str, Path],
    dane: Dane,
    sekcje: Iterable[str] | None = None,
) -> None:
    """Zapisuje wybrane dane do pliku.

    Bez argumentu sekcje zapisuje wszystko. Z listą nazw sekcji zapisuje
    tylko te, np. ZapiszDane("x.txt", dane, ["points", "segments"]).
    """
    if sekcje is not None:
        dane = _wybierz_sekcje(dane, sekcje)
    zapisz(sciezka, dane)


def wypisz_info(sciezka: Union[str, Path]) -> None:
    """Wypisuje na konsolę nazwy sekcji i ich komentarze."""
    for nazwa, komentarze in InfoDanych(sciezka):
        print(f"[{nazwa}]")
        for linia in komentarze:
            print(f"  {linia}")


def wypisz_dane(dane: Dane) -> None:
    """Wypisuje na konsolę krótkie podsumowanie wczytanych danych."""
    print(f"punkty: {len(dane.kontener.punkty())}")
    print(f"odcinki: {len(dane.kontener.odcinki())}")
    print(f"przeciecia: {len(dane.przeciecia)}")
    print(f"wielokaty: {len(dane.wielokaty)}")
    print(f"strony: {len(dane.strony)}")
    if dane.info:
        print("info:")
        for linia in dane.info:
            print(f"  {linia}")


__all__ = [
    "BladPliku", "Przeciecie", "Strona", "Wielokat", "Dane",
    "punkt_przeciecia", "czesc_wspolna", "strona_punktu", "oblicz_przeciecia",
    "z_tekstu", "wczytaj", "do_tekstu", "zapisz",
    "InfoDanych", "WczytajDane", "ZapiszDane", "wypisz_info", "wypisz_dane",
]
