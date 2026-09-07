"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
import enum


class KategorijaUsluge(enum.Enum):
    FRIZURA = "FRIZURA"
    DEPILACIJA = "DEPILACIJA"
    MANIKIR_PEDIKIR = "MANIKIR_PEDIKIR"
    LASH_BROW = "LASH_BROW"
    NEGA_LICA = "NEGA_LICA"

class StatusTermina(enum.Enum):
    ODRZAN = "ODRZAN"
    OTKAZAN = "OTKAZAN"
    ZAKAZAN = "ZAKAZAN"

