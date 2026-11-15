
from toolbox.geometria import Parametryka, CCW
from toolbox.punkty import Punkt

# 1. Długość odcinka
odcinek = Parametryka(0, 0, 3, 4)
print("Długość:", odcinek.dlugosc())

# 2. Położenie punktu względem odcinka
wynik = odcinek.check_orientacja_punkt(2, 2)
print("Orientacja:", wynik)

# 3. Czy trzy punkty tworzą zakręt w lewo?
p = Punkt(0, 0)
q = Punkt(3, 0)
r = Punkt(3, 2)

print("Zakręt w lewo:", CCW(p, q, r))
