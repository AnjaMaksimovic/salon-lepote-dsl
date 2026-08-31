####################
# STRUCTURAL MODEL #
####################

from besser.BUML.metamodel.structural import (
    Class, Property, Method, Parameter,
    BinaryAssociation, Generalization, DomainModel,
    Enumeration, EnumerationLiteral, Multiplicity,
    StringType, IntegerType, FloatType, BooleanType,
    TimeType, DateType, DateTimeType, TimeDeltaType,
    AnyType, Constraint, AssociationClass, Metadata, MethodImplementationType
)

# Enumerations
StatusTermina: Enumeration = Enumeration(
    name="StatusTermina",
    literals={
            EnumerationLiteral(name="ZAKAZAN"),
			EnumerationLiteral(name="ODRZAN"),
			EnumerationLiteral(name="OTKAZAN")
    }
)

KategorijaUsluge: Enumeration = Enumeration(
    name="KategorijaUsluge",
    literals={
            EnumerationLiteral(name="FRIZURA"),
			EnumerationLiteral(name="MANIKIR_PEDIKIR"),
			EnumerationLiteral(name="DEPILACIJA"),
			EnumerationLiteral(name="LASH_BROW"),
			EnumerationLiteral(name="NEGA_LICA")
    }
)

# Classes
Klijent = Class(name="Klijent")
Termin = Class(name="Termin")
Usluga = Class(name="Usluga")
Radnik = Class(name="Radnik")
Paket = Class(name="Paket")

# Klijent class attributes and methods
Klijent_ime: Property = Property(name="ime", type=StringType)
Klijent_email: Property = Property(name="email", type=StringType)
Klijent_telefon: Property = Property(name="telefon", type=StringType, visibility="private")
Klijent.attributes={Klijent_email, Klijent_ime, Klijent_telefon}

# Termin class attributes and methods
Termin_datumVreme: Property = Property(name="datumVreme", type=DateTimeType)
Termin_trajanjeMin: Property = Property(name="trajanjeMin", type=IntegerType)
Termin_status: Property = Property(name="status", type=StatusTermina)
Termin.attributes={Termin_datumVreme, Termin_status, Termin_trajanjeMin}

# Usluga class attributes and methods
Usluga_naziv: Property = Property(name="naziv", type=StringType)
Usluga_cena: Property = Property(name="cena", type=FloatType)
Usluga_trajanjeMin: Property = Property(name="trajanjeMin", type=IntegerType)
Usluga_kategorija: Property = Property(name="kategorija", type=KategorijaUsluge)
Usluga.attributes={Usluga_cena, Usluga_kategorija, Usluga_naziv, Usluga_trajanjeMin}

# Radnik class attributes and methods
Radnik_ime: Property = Property(name="ime", type=StringType)
Radnik_prezime: Property = Property(name="prezime", type=StringType)
Radnik_radnoVremeOd: Property = Property(name="radnoVremeOd", type=TimeType, visibility="private")
Radnik_radnoVremeDo: Property = Property(name="radnoVremeDo", type=TimeType, visibility="private")
Radnik.attributes={Radnik_ime, Radnik_prezime, Radnik_radnoVremeDo, Radnik_radnoVremeOd}

# Paket class attributes and methods
Paket_naziv: Property = Property(name="naziv", type=StringType)
Paket_cena: Property = Property(name="cena", type=FloatType)
Paket.attributes={Paket_cena, Paket_naziv}

# Relationships
Klijent_Termin: BinaryAssociation = BinaryAssociation(
    name="Klijent_Termin",
    ends={
        Property(name="klijent", type=Klijent, multiplicity=Multiplicity(1, 1)),
        Property(name="termin", type=Termin, multiplicity=Multiplicity(0, 9999))
    }
)
Radnik_Termin: BinaryAssociation = BinaryAssociation(
    name="Radnik_Termin",
    ends={
        Property(name="radnik", type=Radnik, multiplicity=Multiplicity(1, 1)),
        Property(name="termin", type=Termin, multiplicity=Multiplicity(0, 9999))
    }
)
Termin_Usluga: BinaryAssociation = BinaryAssociation(
    name="Termin_Usluga",
    ends={
        Property(name="termin", type=Termin, multiplicity=Multiplicity(1, 9999)),
        Property(name="usluga", type=Usluga, multiplicity=Multiplicity(0, 9999))
    }
)
Radnik_Usluga: BinaryAssociation = BinaryAssociation(
    name="Radnik_Usluga",
    ends={
        Property(name="radnik", type=Radnik, multiplicity=Multiplicity(0, 9999)),
        Property(name="usluga", type=Usluga, multiplicity=Multiplicity(0, 9999))
    }
)
Paket_Usluga: BinaryAssociation = BinaryAssociation(
    name="Paket_Usluga",
    ends={
        Property(name="paket", type=Paket, multiplicity=Multiplicity(1, 9999)),
        Property(name="usluga", type=Usluga, multiplicity=Multiplicity(0, 9999))
    }
)


# OCL Constraints
TrajanjeDovoljno: Constraint = Constraint(
    name="TrajanjeDovoljno",
    context=Termin,
    expression="context Termin inv TrajanjeDovoljno:   self.trajanjeMin >= self.usluga->collect(u | u.trajanjeMin)->sum()",
    language="OCL",
    description="Trajanje termina mora biti dovoljno da pokrije sve zakazane usluge."
)
UslugaKompatibilnaSaRadnikom: Constraint = Constraint(
    name="UslugaKompatibilnaSaRadnikom",
    context=Termin,
    expression="context Termin inv UslugaKompatibilnaSaRadnikom:   self.usluga->forAll(u | self.radnik.usluga->includes(u))",
    language="OCL",
    description="Usluge zakazane u terminu moraju biti u okviru specijalizacija dodeljenog radnika."
)
PaketJeftinijiOdPojedinacnih: Constraint = Constraint(
    name="PaketJeftinijiOdPojedinacnih",
    context=Paket,
    expression="context Paket inv PaketJeftinijiOdPojedinacnih:   self.cena < self.usluga->collect(u | u.cena)->sum()",
    language="OCL",
    description="Cena paketa mora biti niža od zbira cena pojedinačnih usluga koje sadrži."
)

# Domain Model
domain_model = DomainModel(
    name="Class_Diagram",
    types={Klijent, Termin, Usluga, Radnik, Paket, StatusTermina, KategorijaUsluge},
    associations={Klijent_Termin, Radnik_Termin, Termin_Usluga, Radnik_Usluga, Paket_Usluga},
    constraints={TrajanjeDovoljno, UslugaKompatibilnaSaRadnikom, PaketJeftinijiOdPojedinacnih},
    generalizations={},
    metadata=None
)


######################
# PROJECT DEFINITION #
######################

from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural.structural import Metadata

metadata = Metadata(description="Modern workspace project for UML, GUI and quantum modeling.")
project = Project(
    name="SalonLepoteDSL",
    models=[domain_model],
    owner="BESSER User",
    metadata=metadata
)
