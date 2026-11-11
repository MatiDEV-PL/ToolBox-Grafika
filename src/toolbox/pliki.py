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

Strona w sekcji [side]: 1 = punkt po lewej od odcinka p->q, -1 = po prawej,
0 = współliniowo.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from math import isinf, isnan
from pathlib import Path
from typing import Callable, Hashable, Iterable, TypeVar, Union

from .geometria import Obiekt, Orientacja
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

    if d == 0:
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


def strona_punktu(odcinek: Obiekt, punkt: Punkt) -> int:
    """1 gdy punkt jest po lewej od odcinka, -1 po prawej, 0 gdy współliniowy."""
    o = odcinek.jako_parametryka.check_orientacja_punkt(punkt.x, punkt.y)
    return {Orientacja.WSPOLLINIOWE: 0, Orientacja.PRZECIWNIE: 1, Orientacja.ZGODNIE: -1}[o]


def oblicz_przeciecia(odcinki: Iterable[Obiekt]) -> list[Przeciecie]:
    """Przecięcia wszystkich par odcinków (naiwnie, każdy z każdym)."""
    lista = list(odcinki)
    wynik = []
    for i in range(len(lista)):
        for j in range(i + 1, len(lista)):
            wynik.append(Przeciecie(lista[i], lista[j], punkt_przeciecia(lista[i], lista[j])))
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
            dane.przeciecia.append(Przeciecie(a, b, Punkt(v[10], v[11])))
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
        for pr in dane.przeciecia:
            a, b = pr.a, pr.b
            w.append(
                _wiersz_odcinka(a) + " " + str(int(a.kolor)).rjust(3) + "  "
                + _wiersz_odcinka(b) + " " + str(int(b.kolor)).rjust(3) + "  "
                + _wiersz(pr.punkt.x, pr.punkt.y)
            )
        w.append("")

    for wielokat in dane.wielokaty:
        w.append(f"[polygon {wielokat.kolor}]")
        w += [_wiersz(p.x, p.y) for p in wielokat.punkty]
        w.append("")

    if dane.strony:
        w.append("[side]")
        w.append("# odcinek (px py qx qy)  punkt (x y)  strona: 1 lewa, -1 prawa, 0 współliniowo")
        for s in dane.strony:
            w.append(_wiersz_odcinka(s.odcinek) + "  " + _wiersz(s.punkt.x, s.punkt.y)
                     + " " + str(s.strona).rjust(3))
        w.append("")

    return "\n".join(w)


def zapisz(sciezka: Union[str, Path], dane: Dane) -> None:
    """Zapisuje dane do pliku."""
    Path(sciezka).write_text(do_tekstu(dane), encoding="utf-8")


__all__ = [
    "BladPliku", "Przeciecie", "Strona", "Wielokat", "Dane",
    "punkt_przeciecia", "strona_punktu", "oblicz_przeciecia",
    "z_tekstu", "wczytaj", "do_tekstu", "zapisz",
]
