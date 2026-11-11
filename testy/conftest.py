import os
import sys


def pytest_configure(config):
    # Przełączamy strumienie na UTF-8, zanim testy zaczną cokolwiek drukować.
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            try:
                strumien.reconfigure(encoding="utf-8")
            except (AttributeError, ValueError):
                pass
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
