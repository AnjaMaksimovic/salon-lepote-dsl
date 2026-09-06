"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
import enum


class KategorijaUsluge(enum.Enum):
    FRIZURA = "FRIZURA"
    LASH_BROW = "LASH_BROW"
    MANIKIR_PEDIKIR = "MANIKIR_PEDIKIR"
    NEGA_LICA = "NEGA_LICA"
    DEPILACIJA = "DEPILACIJA"

class StatusTermina(enum.Enum):
    ODRZAN = "ODRZAN"
    OTKAZAN = "OTKAZAN"
    ZAKAZAN = "ZAKAZAN"

