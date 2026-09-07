import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "model"))

from salon_model import domain_model
from english import english
from besser.BUML.metamodel.structural import Class, Enumeration

print("=== CLASSES ===")
for t in domain_model.types:
    if isinstance(t, Class):
        print(f"\nClass: {english(t.name)}")
        for attr in t.attributes:
            type_name = getattr(attr.type, "name", attr.type)
            print(f"  - {english(attr.name)}: {english(str(type_name))}")

print("\n=== ENUMERATIONS ===")
for t in domain_model.types:
    if isinstance(t, Enumeration):
        print(f"\nEnum: {english(t.name)}")
        for lit in t.literals:
            print(f"  - {english(lit.name)}")

print("\n=== ASSOCIATIONS ===")
for assoc in domain_model.associations:
    print(f"\nAssociation: {english(assoc.name)}")
    for end in assoc.ends:
        type_name = getattr(end.type, "name", end.type)
        print(f"  - role '{english(end.name)}' -> {english(str(type_name))} (multiplicity {end.multiplicity.min}..{end.multiplicity.max})")

print("\n=== OCL CONSTRAINTS ===")
for c in domain_model.constraints:
    print(f"\n{english(c.name)} (context: {english(c.context.name)})")
    print(f"  {english(c.expression)}")