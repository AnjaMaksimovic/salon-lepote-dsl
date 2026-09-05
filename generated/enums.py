"""AUTO-GENERISANO - NE MENJATI RUcNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
import enum


class KategorijaUsluge(enum.Enum):
    DEPILACIJA = "DEPILACIJA"
    NEGA_LICA = "NEGA_LICA"
    FRIZURA = "FRIZURA"
    LASH_BROW = "LASH_BROW"
    MANIKIR_PEDIKIR = "MANIKIR_PEDIKIR"

class StatusTermina(enum.Enum):
    ZAKAZAN = "ZAKAZAN"
    OTKAZAN = "OTKAZAN"
    ODRZAN = "ODRZAN"

