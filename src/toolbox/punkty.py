"""
Punkt na płaszczyźnie, dwie współrzędne i kolor.

Kolor trzymamy jako liczbę całkowitą: 0 to brak koloru 1 niebieski
2 czerwony 3 zielony a jak ktoś chce więcej to po prostu wpisuje
liczbę większą od 3.

Są jeszcze dwa punktów: nan i nieskończoność. Bierzemy je
z modułu math który jest w Pythonie.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import inf, isinf, isnan, nan

from .kolory import PodstawoweKolory


@dataclass(frozen=True)
class Punkt:
    """Punkt na płaszczyźnie z kolorem.

    Kolor nie jest sprawdzany więc można wpisać dowolną liczbę całkowitą.
    """

    x: float
    y: float
    c: int = int(PodstawoweKolory.NONE)

    def __post_init__(self) -> None:
        # Pola klasy frozen ustawiamy przez object.__setattr__
        object.__setattr__(self, "x", float(self.x))
        object.__setattr__(self, "y", float(self.y))

    @property
    def kolor(self) -> int:
        """To samo co c tylko tak nazywamy kolor w odcinku."""
        return self.c

    @property
    def wspolrzedne(self) -> tuple[float, float]:
        """Zwraca tylko (x, y), bez koloru."""
        return (self.x, self.y)

    @property
    def jest_nan(self) -> bool:
        """Czy to punkt nan."""
        return isnan(self.x) or isnan(self.y)

    @property
    def jest_nieskonczony(self) -> bool:
        """Czy to punkt nieskończoności."""
        return isinf(self.x) or isinf(self.y)

    @property
    def jest_specjalny(self) -> bool:
        """Czy to któryś z tych dwóch niefajnych punktów."""
        return self.jest_nan or self.jest_nieskonczony


def _specjalny(x: float, y: float, c: int = int(PodstawoweKolory.NONE)) -> Punkt:
    return Punkt(x=x, y=y, c=c)


# Punkty specjalne z modułu math, nie trzeba nic instalować.
PUNKT_ROZBIEGAJACY = _specjalny(nan, nan)
PUNKT_NIESKONCZONOSCI = _specjalny(-inf, inf)


def punkt(x: float, y: float, c: int = int(PodstawoweKolory.NONE)) -> Punkt:
    """Skrót żeby nie pisać Punkt(x=..., y=..., c=...) za każdym razem."""
    return Punkt(x=x, y=y, c=c)


__all__ = ["Punkt", "PUNKT_ROZBIEGAJACY", "PUNKT_NIESKONCZONOSCI", "punkt"]
