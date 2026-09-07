"""English code names mapped from the unchanged source domain model."""
import re

NAMES = {
    "Klijent": "Client", "Radnik": "Worker", "Usluga": "Service", "Paket": "Package", "Termin": "Appointment",
    "klijent": "client", "radnik": "worker", "usluga": "service", "paket": "package", "termin": "appointment",
    "StatusTermina": "AppointmentStatus", "KategorijaUsluge": "ServiceCategory",
    "ime": "name", "prezime": "surname", "naziv": "name", "telefon": "phone", "cena": "price",
    "radnoVremeOd": "workingHoursFrom", "radnoVremeDo": "workingHoursTo",
    "trajanjeMin": "durationMinutes", "datumVreme": "dateTime", "kategorija": "category",
    "FRIZURA": "HAIRCUT", "LASH_BROW": "LASH_BROW", "MANIKIR_PEDIKIR": "MANICURE_PEDICURE",
    "NEGA_LICA": "FACIAL_CARE", "DEPILACIJA": "HAIR_REMOVAL",
    "ODRZAN": "COMPLETED", "OTKAZAN": "CANCELLED", "ZAKAZAN": "SCHEDULED",
    "TrajanjeDovoljno": "SufficientDuration", "UslugaKompatibilnaSaRadnikom": "WorkerServiceCompatibility",
    "PaketJeftinijiOdPojedinacnih": "PackageDiscount", "validiraj": "validate",
    "povezani": "related", "zbir": "total", "drugi_objekat": "related_object", "dozvoljeni_ids": "allowed_ids",
    "primer": "sample",
}
_PATTERN = re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(k) for k in sorted(NAMES, key=len, reverse=True)) + r")(?![A-Za-z0-9])")


def english(value):
    return _PATTERN.sub(lambda match: NAMES[match.group()], value)


def translate_context(value):
    if isinstance(value, dict):
        return {english(key): translate_context(item) for key, item in value.items()}
    if isinstance(value, list):
        return [translate_context(item) for item in value]
    if isinstance(value, str):
        return english(value)
    return value


CONSTRAINT_DESCRIPTIONS = {
    "TrajanjeDovoljno": "The appointment must be long enough to cover all selected services.",
    "UslugaKompatibilnaSaRadnikom": "The selected worker must be qualified to perform every selected service.",
    "PaketJeftinijiOdPojedinacnih": "The package price must be lower than the total price of its services.",
}
