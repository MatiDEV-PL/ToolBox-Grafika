# Algorytm - przecięcie odcinków&#xA0;

> [!NOTE]
> ## Wstawiamy 2 odcinki:&#xA0;
>
> a = Obiekt.z_wspolrzednych(), b = Obiekt.z...
>
> Jest klasy obiekt, przechowuje punkt początkowy, końcowy i kolor.
>
> A.poczatek.x, a.poczatek.y, a.koniec.x, a.koniec.y
>
> a.jako_parametryka zmienia odcinek na postać parametryczna - punkt początkowy i wektor kierunkowy

---

> [!NOTE]
> ## Get_orientacja()
>
> Sprawdza położenie punktu względem odcinka
>
> *(geometria.py `19`)*
>
> Wykorzystuje się wyznacznik związany z iloczynem wektorowym.
>
> - `-1` - po lewej
> - `1` - po prawej
> - `0` - współliniowy

---

> [!NOTE]
> ## na_odcinku()&#xA0;
>
> Sprawdza czy punkt należy do odcinka
>
> (`geometria.py`, linia `119`)
>
> Funkcja najpierw sprawdza wspolliniowosc, potem sprawdza, czy współrzędne punktu są pomiędzy końcami odcinka (oddzielnie x i y)

---

> [!NOTE]
> ## tuli_z()
>
> Sprawdza czy odcinki się przecinają (`geometria.py`, linia `129`)
>
> - Sprawdza czy współrzędne są poprawne (bez punkt specjalny - nan, inf) `137`
> - Sprawdza położenie końców względem drugiego odcinka (wszystkich punktów) `140`
> - Sprawdza przecięcie (rzeka, droga to co było) `147`
> - Jak końce albo odcinki się pokrywają `151`

---

> [!NOTE]
> ## punkt_przeciecia()
>
> Oblicza współrzędne punktu przecięcia (`pliki.py`, linia `90`)
>
> - Jeśli się nie przecinają to punkt rozbiegający (nań, nań) `92`
> - Zamienia odcinki na postać parametryczna (punkt pacz. I wektor) `95`
> - Oblicza wyznacznik `112` jeśli wyznacznik =/=0 to nie są rownolegle, jeśli tak to są rownolegle lub współliniowe
> - Jeśli są współliniowe to szukamy końców odcinków, które leżą na drugim odcinku
>
>   - Jeśli znaleźliśmy dokładnie jeden punkt `107`, to zwracamy ten punkt
>   - Jeśli jest więcej punktów `110` zwraca -inf; inf
>
> - Jeśli wyznacznik jest równy 0 lub blisko 0 (`99`), to obliczamy t - układ równań na przecięcie dwóch prostych `112`.
> - get_punkt(t) oblicza współrzędne (`geometria.py`, linia `107`)

---

> [!NOTE]
> ## czesc_wspolna()&#xA0;
>
> Zwraca nam część wspólną pokrywających się odcinków (`pliki.py`, linia `117`)
>
> - Sprawdza czy jest punkt przecięcia z tuli_z() `124`
> - Parametryzuje odcinki `127`
> - Sprawdza czy odcinki są współliniowe (poprzez wyznacznik wektorowy) `128`
> - Szuka końców, które leżą na drugim odcinku `132`
> - Jeżeli znajduje mniej niż 2 punkty, to odcinki się nie nakładają, mogą się dotykać jednym końcem `137`
> - Porządkuje punkty i zwraca końcowe `140`
