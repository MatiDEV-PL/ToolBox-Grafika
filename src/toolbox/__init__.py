# Te importy definiują, co jest "widoczne" dla osoby używającej Twojej biblioteki
from .kolory import PodstawoweKolory
from .geometria import Orientacja, get_orientacja, Parametryka

__version__ = "0.1.0"
__all__ = ["PodstawoweKolory", "Orientacja", "get_orientacja", "Parametryka"]