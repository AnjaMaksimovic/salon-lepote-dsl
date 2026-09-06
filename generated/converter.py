"""AUTO-GENERISANO - NE MENJATI RUČNO. Izmene radite u model/salon_model.py i ponovo pokrenite generate.py"""
from generated.dto import KlijentDTO, PaketDTO, RadnikDTO, TerminDTO, UslugaDTO
from generated.schema import KlijentOut, PaketOut, RadnikOut, TerminOut, UslugaOut

def klijent_to_dto(obj) -> KlijentDTO:
    """SQLAlchemy Klijent entitet -> KlijentDTO (bez ORM zavisnosti)."""
    return KlijentDTO(
        id=obj.id,
        email=obj.email,
        ime=obj.ime,
        telefon=obj.telefon,
    )


def klijent_dto_to_out(dto: KlijentDTO) -> KlijentOut:
    """KlijentDTO -> KlijentOut (Pydantic sema za API odgovor)."""
    return KlijentOut(**dto.__dict__)


def klijent_to_out(obj) -> KlijentOut:
    """SQLAlchemy Klijent entitet -> KlijentOut, direktno preko DTO-a."""
    return klijent_dto_to_out(klijent_to_dto(obj))

def paket_to_dto(obj) -> PaketDTO:
    """SQLAlchemy Paket entitet -> PaketDTO (bez ORM zavisnosti)."""
    return PaketDTO(
        id=obj.id,
        cena=obj.cena,
        naziv=obj.naziv,
    )


def paket_dto_to_out(dto: PaketDTO) -> PaketOut:
    """PaketDTO -> PaketOut (Pydantic sema za API odgovor)."""
    return PaketOut(**dto.__dict__)


def paket_to_out(obj) -> PaketOut:
    """SQLAlchemy Paket entitet -> PaketOut, direktno preko DTO-a."""
    return paket_dto_to_out(paket_to_dto(obj))

def radnik_to_dto(obj) -> RadnikDTO:
    """SQLAlchemy Radnik entitet -> RadnikDTO (bez ORM zavisnosti)."""
    return RadnikDTO(
        id=obj.id,
        ime=obj.ime,
        prezime=obj.prezime,
        radnoVremeDo=obj.radnoVremeDo,
        radnoVremeOd=obj.radnoVremeOd,
    )


def radnik_dto_to_out(dto: RadnikDTO) -> RadnikOut:
    """RadnikDTO -> RadnikOut (Pydantic sema za API odgovor)."""
    return RadnikOut(**dto.__dict__)


def radnik_to_out(obj) -> RadnikOut:
    """SQLAlchemy Radnik entitet -> RadnikOut, direktno preko DTO-a."""
    return radnik_dto_to_out(radnik_to_dto(obj))

def termin_to_dto(obj) -> TerminDTO:
    """SQLAlchemy Termin entitet -> TerminDTO (bez ORM zavisnosti)."""
    return TerminDTO(
        id=obj.id,
        datumVreme=obj.datumVreme,
        status=obj.status,
        trajanjeMin=obj.trajanjeMin,
        klijent_id=obj.klijent_id,
        radnik_id=obj.radnik_id,
    )


def termin_dto_to_out(dto: TerminDTO) -> TerminOut:
    """TerminDTO -> TerminOut (Pydantic sema za API odgovor)."""
    return TerminOut(**dto.__dict__)


def termin_to_out(obj) -> TerminOut:
    """SQLAlchemy Termin entitet -> TerminOut, direktno preko DTO-a."""
    return termin_dto_to_out(termin_to_dto(obj))

def usluga_to_dto(obj) -> UslugaDTO:
    """SQLAlchemy Usluga entitet -> UslugaDTO (bez ORM zavisnosti)."""
    return UslugaDTO(
        id=obj.id,
        cena=obj.cena,
        kategorija=obj.kategorija,
        naziv=obj.naziv,
        trajanjeMin=obj.trajanjeMin,
    )


def usluga_dto_to_out(dto: UslugaDTO) -> UslugaOut:
    """UslugaDTO -> UslugaOut (Pydantic sema za API odgovor)."""
    return UslugaOut(**dto.__dict__)


def usluga_to_out(obj) -> UslugaOut:
    """SQLAlchemy Usluga entitet -> UslugaOut, direktno preko DTO-a."""
    return usluga_dto_to_out(usluga_to_dto(obj))
