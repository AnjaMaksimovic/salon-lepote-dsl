"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
import enum


class KategorijaUsluge(enum.Enum):
    LASH_BROW = "LASH_BROW"
    FRIZURA = "FRIZURA"
    MANIKIR_PEDIKIR = "MANIKIR_PEDIKIR"
    NEGA_LICA = "NEGA_LICA"
    DEPILACIJA = "DEPILACIJA"

class StatusTermina(enum.Enum):
    ODRZAN = "ODRZAN"
    ZAKAZAN = "ZAKAZAN"
    OTKAZAN = "OTKAZAN"

