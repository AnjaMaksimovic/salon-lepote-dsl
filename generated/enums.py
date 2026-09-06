"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
import enum


class KategorijaUsluge(enum.Enum):
    LASH_BROW = "LASH_BROW"
    MANIKIR_PEDIKIR = "MANIKIR_PEDIKIR"
    NEGA_LICA = "NEGA_LICA"
    DEPILACIJA = "DEPILACIJA"
    FRIZURA = "FRIZURA"

class StatusTermina(enum.Enum):
    ZAKAZAN = "ZAKAZAN"
    ODRZAN = "ODRZAN"
    OTKAZAN = "OTKAZAN"

