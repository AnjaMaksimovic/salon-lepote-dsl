import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "model"))

from salon_model import domain_model
from besser.BUML.metamodel.structural import Class, Enumeration

print("=== KLASE ===")
for t in domain_model.types:
    if isinstance(t, Class):
        print(f"\nKlasa: {t.name}")
        for attr in t.attributes:
            type_name = getattr(attr.type, "name", attr.type)
            print(f"  - {attr.name}: {type_name}")

print("\n=== ENUMERACIJE ===")
for t in domain_model.types:
    if isinstance(t, Enumeration):
        print(f"\nEnum: {t.name}")
        for lit in t.literals:
            print(f"  - {lit.name}")

print("\n=== ASOCIJACIJE ===")
for assoc in domain_model.associations:
    print(f"\nAsocijacija: {assoc.name}")
    for end in assoc.ends:
        type_name = getattr(end.type, "name", end.type)
        print(f"  - rola '{end.name}' -> {type_name} (multiplicity {end.multiplicity.min}..{end.multiplicity.max})")

print("\n=== OCL OGRANICENJA ===")
for c in domain_model.constraints:
    print(f"\n{c.name} (context: {c.context.name})")
    print(f"  {c.expression}")