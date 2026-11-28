"""
Otoczka wypukła zbioru punktów: trzy algorytmy.

Otoczka to najmniejszy wypukły wielokąt, który zawiera wszystkie punkty.
Wierzchołki otoczki to te punkty, które leżą "na brzegu" i są jego rogami.

Umowy, wspólne dla wszystkich trzech algorytmów:

* wynik to lista wierzchołków (Punkt) w kolejności ZGODNEJ z ruchem wskazówek
  zegara, czyli przy przejściu po brzegu cały zbiór jest po PRAWEJ stronie,
* lista zaczyna się od punktu położonego najbardziej na lewo (przy remisie
  najniżej), dzięki czemu wyniki różnych algorytmów można porównać wprost,
* punkty leżące na boku otoczki (współliniowe) NIE są wierzchołkami,
* powtórzone punkty (te same współrzędne) liczą się raz,
* dla 0, 1 i 2 różnych punktów, a także gdy wszystkie leżą na jednej prostej,
  wynik to odpowiednio [], [p], [skrajny1, skrajny2].

Algorytmy:

    otoczka_naiwna        O(n^3) w najgorszym razie; każda para punktów to
                          kandydat na bok, sprawdzamy czy reszta jest po prawej
    otoczka_przyrostowa   O(n^2) w najgorszym razie; sortujemy punkty po X
                          i dokładamy po jednym, poprawiając otoczkę
    otoczka_graham        O(n log n); sortowanie kątowe wokół najniższego
                          punktu i przejście ze stosem

Orientację punktów sprawdza zakret() z geometria.py (z tolerancją EPS).
"""
from __future__ import annotations

from functools import cmp_to_key
from typing import Callable, Iterable

from .geometria import SortLex, zakret
from .punkty import Punkt

Otoczka = list  # lista Punktow


# --- Wspólne drobiazgi ---------------------------------------------------

def _unikalne(punkty: Iterable[Punkt]) -> list[Punkt]:
    """Usuwa powtórzone punkty (po współrzędnych), zachowuje pierwszy z nich."""
    widziane = set()
    wynik = []
    for p in punkty:
        if p.wspolrzedne not in widziane:
            widziane.add(p.wspolrzedne)
            wynik.append(p)
    return wynik


def _na_prawo(p: Punkt, q: Punkt, r: Punkt) -> bool:
    """Czy punkt r leży ściśle po prawej od odcinka p -> q."""
    return zakret(p, q, r) < 0


def _na_odcinku(p: Punkt, q: Punkt, r: Punkt) -> bool:
    """Czy punkt r (współliniowy z p i q) leży między p a q, końce też."""
    return (min(p.x, q.x) <= r.x <= max(p.x, q.x)
            and min(p.y, q.y) <= r.y <= max(p.y, q.y))


def _od_najbardziej_lewego(wierzcholki: list[Punkt]) -> list[Punkt]:
    """Obraca listę tak, żeby zaczynała się od punktu najbardziej na lewo."""
    if not wierzcholki:
        return []
    start = SortLex(wierzcholki, "LD")[0]
    i = wierzcholki.index(start)
    return wierzcholki[i:] + wierzcholki[:i]


def _skrajne(punkty: list[Punkt]) -> list[Punkt]:
    """Wynik dla zbioru bez pola: [], [p] albo dwa skrajne punkty."""
    if len(punkty) <= 1:
        return list(punkty)
    posortowane = SortLex(punkty, "LD")
    return [posortowane[0], posortowane[-1]]


def _wspolliniowe(punkty: list[Punkt]) -> bool:
    """Czy wszystkie punkty leżą na jednej prostej."""
    if len(punkty) <= 2:
        return True
    a, b = punkty[0], punkty[1]
    return all(zakret(a, b, r) == 0 for r in punkty[2:])


# --- 1. Algorytm naiwny --------------------------------------------------

def otoczka_naiwna(punkty: Iterable[Punkt]) -> list[Punkt]:
    """Algorytm naiwny: sprawdza każdą parę punktów jako możliwy bok.

    Dla uporządkowanej pary (p, q) pytamy: czy WSZYSTKIE pozostałe punkty
    leżą po prawej od odcinka p -> q? Jeśli tak, p -> q jest bokiem otoczki.
    Punkt współliniowy z p i q nie psuje sprawy, o ile leży na odcinku p-q
    (wtedy to tylko punkt na boku). Dzięki temu bokiem jest zawsze najdłuższy
    odcinek i na liście wierzchołków nie ma punktów leżących na bokach.

    Na końcu boki układamy w jedną pętlę: koniec jednego to początek
    następnego.
    """
    p_all = _unikalne(punkty)
    if len(p_all) <= 2 or _wspolliniowe(p_all):
        return _skrajne(p_all)

    nastepny: dict[tuple[float, float], Punkt] = {}
    for p in p_all:
        for q in p_all:
            if p is q:
                continue
            czy_bok = True
            for r in p_all:
                if r is p or r is q:
                    continue
                z = zakret(p, q, r)
                if z < 0:
                    continue  # po prawej, dobrze
                if z == 0 and _na_odcinku(p, q, r):
                    continue  # leży na boku, dobrze
                czy_bok = False
                break
            if czy_bok:
                nastepny[p.wspolrzedne] = q

    # Składamy pętlę z boków: p -> nastepny[p] -> ...
    start = SortLex(list(p_all), "LD")[0]
    wynik = [start]
    aktualny = nastepny[start.wspolrzedne]
    while aktualny.wspolrzedne != start.wspolrzedne:
        wynik.append(aktualny)
        aktualny = nastepny[aktualny.wspolrzedne]
    return wynik


# --- 2. Algorytm przyrostowy ---------------------------------------------

def otoczka_przyrostowa(punkty: Iterable[Punkt]) -> list[Punkt]:
    """Algorytm przyrostowy: punkty po kolei od lewej do prawej.

    Punkty "rzucamy na oś X" i sortujemy (przy remisie od dołu), czyli nadajemy
    im numery 1, 2, 3, ... Zaczynamy od pierwszych dwóch i dokładamy kolejne.

    Kolejny punkt jest leksykograficznie największy z dotychczasowych, więc
    zawsze leży poza obecną otoczką i staje się jej wierzchołkiem. Wystarczy
    znaleźć boki, które go "widzą" (nowy punkt jest po ich LEWEJ, czyli
    z zewnątrz), usunąć wierzchołki leżące między nimi i wstawić nowy punkt.
    """
    p_all = SortLex(_unikalne(punkty), "LD")
    if len(p_all) <= 2 or _wspolliniowe(p_all):
        return _skrajne(p_all)

    # Start: trójkąt z pierwszych trzech punktów, które nie leżą na prostej.
    a, b = p_all[0], p_all[1]
    i = 2
    while zakret(a, b, p_all[i]) == 0:
        # Pierwsze punkty leżą na jednej prostej: zostają skrajne a, p_all[i-1+1]
        b = p_all[i]
        i += 1
    c = p_all[i]
    hull = [a, b, c] if _na_prawo(a, b, c) else [a, c, b]

    for p in p_all[i + 1:]:
        n = len(hull)
        # bok k to hull[k] -> hull[k+1]; "widoczny" gdy p jest po jego lewej
        widoczny = [zakret(hull[k], hull[(k + 1) % n], p) > 0 for k in range(n)]
        # początek serii widocznych boków: widoczny, a poprzedni nie
        k0 = next(k for k in range(n) if widoczny[k] and not widoczny[k - 1])
        k1 = k0
        while widoczny[(k1 + 1) % n]:
            k1 = (k1 + 1) % n
        # Usuwamy wierzchołki hull[k0+1] ... hull[k1], wstawiamy p
        nowa = [p]
        j = (k1 + 1) % n
        while True:
            nowa.append(hull[j])
            if j == k0:
                break
            j = (j + 1) % n
        # Sprzątanie: wierzchołek współliniowy z p i sąsiadem nie jest rogiem
        if len(nowa) >= 3 and zakret(nowa[-2], nowa[-1], p) == 0:
            nowa.pop()
        if len(nowa) >= 3 and zakret(p, nowa[1], nowa[2]) == 0:
            nowa.pop(1)
        hull = nowa

    return _od_najbardziej_lewego(hull)


# --- 3. Algorytm Grahama -------------------------------------------------

def otoczka_graham(punkty: Iterable[Punkt]) -> list[Punkt]:
    """Algorytm Grahama (przejście ze stosem po sortowaniu kątowym).

    1. Za punkt startowy bierzemy najniższy (przy remisie najbardziej lewy),
       na pewno jest wierzchołkiem otoczki.
    2. Pozostałe punkty sortujemy według kąta widzenia z punktu startowego
       (przy tym samym kącie bliższy pierwszy).
    3. Idziemy po kolei i trzymamy stos. Gdy nowy punkt nie daje skrętu
       w lewo względem dwóch ostatnich ze stosu, zdejmujemy ostatni punkt,
       bo wpadł do środka (albo leży na boku).
    Stos buduje otoczkę przeciwnie do zegara, na końcu ją odwracamy.
    """
    p_all = _unikalne(punkty)
    if len(p_all) <= 2 or _wspolliniowe(p_all):
        return _skrajne(p_all)

    start = SortLex(p_all, "DL")[0]
    reszta = [p for p in p_all if p is not start]

    def porownaj(p: Punkt, q: Punkt) -> int:
        z = zakret(start, p, q)
        if z > 0:        # q jest po lewej od start->p, czyli ma większy kąt
            return -1
        if z < 0:
            return 1
        # ten sam kąt: bliższy najpierw
        dp = (p.x - start.x) ** 2 + (p.y - start.y) ** 2
        dq = (q.x - start.x) ** 2 + (q.y - start.y) ** 2
        return -1 if dp < dq else (1 if dp > dq else 0)

    reszta.sort(key=cmp_to_key(porownaj))

    stos = [start]
    for p in reszta:
        while len(stos) >= 2 and zakret(stos[-2], stos[-1], p) <= 0:
            stos.pop()
        stos.append(p)

    stos.reverse()  # było przeciwnie do zegara, chcemy zgodnie
    return _od_najbardziej_lewego(stos)


ALGORYTMY: dict[str, Callable[[Iterable[Punkt]], list[Punkt]]] = {
    "naiwny": otoczka_naiwna,
    "przyrostowy": otoczka_przyrostowa,
    "graham": otoczka_graham,
}


__all__ = [
    "otoczka_naiwna", "otoczka_przyrostowa", "otoczka_graham", "ALGORYTMY",
]
