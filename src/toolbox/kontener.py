"""
Kontener na obiekty graficzne, trzyma punkty i odcinki w jednej liście.

Dzięki temu że wszystko jest w jednym miejscu dodawanie iteracja
filtr po kolorze i liczenie działają tak samo dla obu typów.
"""
from __future__ import annotations

from typing import Iterable, Iterator, Union

from .geometria import Obiekt
from .kolory import PodstawoweKolory
from .punkty import Punkt

Element = Union[Punkt, Obiekt]


class Kontener:
    """Zbiór punktów i odcinków.

    Niezależnie od tego co wrzucimy do środka dodawanie iteracja
    filtrowanie po kolorze i liczenie elementów działają tak samo.
    """

    def __init__(self, obiekty: Iterable[Element] | None = None):
        self._obiekty: list[Element] = list(obiekty) if obiekty else []

    def dodaj(self, obiekt: Element) -> Element:
        """Dodaje punkt albo odcinek i zwraca go z powrotem."""
        if not isinstance(obiekt, (Punkt, Obiekt)):
            raise TypeError(f"Kontener przyjmuje tylko Punkt lub Obiekt, nie {type(obiekt).__name__}")
        self._obiekty.append(obiekt)
        return obiekt

    def usun(self, obiekt: Element) -> None:
        """Usuwa obiekt, pierwszy taki jaki znajdzie."""
        self._obiekty.remove(obiekt)

    def wyslij(self) -> list[Element]:
        """Zwraca kopię listy z obiektami."""
        return list(self._obiekty)

    def wedlug_koloru(self, kolor: int) -> list[Element]:
        """Zwraca wszystko w podanym kolorze."""
        return [o for o in self._obiekty if o.kolor == kolor]

    def punkty(self) -> list[Punkt]:
        return [o for o in self._obiekty if isinstance(o, Punkt)]

    def odcinki(self) -> list[Obiekt]:
        return [o for o in self._obiekty if isinstance(o, Obiekt)]

    def specjalne(self) -> list[Punkt]:
        """Wszystkie punkty nan i nieskończoności jakie mamy.

        Sprawdzamy też końce odcinków bo one też są punktami i mogą
        popsuć wyniki obliczeń.
        """
        znalezione: list[Punkt] = []
        for element in self._obiekty:
            if isinstance(element, Punkt):
                if element.jest_specjalny:
                    znalezione.append(element)
            else:
                for koniec in (element.poczatek, element.koniec):
                    if koniec.jest_specjalny:
                        znalezione.append(koniec)
        return znalezione

    def __len__(self) -> int:
        return len(self._obiekty)

    def __iter__(self) -> Iterator[Element]:
        return iter(self._obiekty)

    def __repr__(self) -> str:
        return f"Kontener({len(self._obiekty)} obiektow)"


__all__ = ["Kontener", "Element"]
