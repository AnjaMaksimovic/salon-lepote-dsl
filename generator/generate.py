"""
Glavni generator skript. Cita model/salon_model.py (B-UML model) i za svaku klasu,
enumeraciju i OCL ograničenje generise odgovarajući Python kod koristeći Jinja2 template-e
iz generator/templates/.

Pokretanje:  python3 generator/generate.py
"""
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from model.salon_model import domain_model
from besser.BUML.metamodel.structural import Class, Enumeration
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "generated")
FRONTEND_DIR = os.path.join(OUTPUT_DIR, "frontend")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)

# ---------------------------------------------------------------------------
# Mapiranje B-UML tipova
# ---------------------------------------------------------------------------
SQL_TYPE_MAP = {
    "str": "String(100)",
    "int": "Integer",
    "float": "Float",
    "bool": "Boolean",
    "date": "Date",
    "datetime": "DateTime",
    "time": "Time",
}
PY_TYPE_MAP = {
    "str": "str",
    "int": "int",
    "float": "float",
    "bool": "bool",
    "date": "date",
    "datetime": "datetime",
    "time": "time",
}
SAMPLE_VALUE_MAP = {
    "str": "primer",
    "int": 1,
    "float": 1.0,
    "bool": True,
    "date": "2026-09-10",
    "datetime": "2026-09-10T10:00:00",
    "time": "10:00:00",
}

all_classes = [t for t in domain_model.types if isinstance(t, Class)]
all_enums = [t for t in domain_model.types if isinstance(t, Enumeration)]
enum_names_by_type = {e.name: e for e in all_enums}
enum_names = [e.name for e in all_enums]

def resolve_type(buml_type, attr_name):
    """Vraća (sql_type, py_type, sample_value) za dati B-UML tip atributa."""
    type_name = getattr(buml_type, "name", None)
    if type_name in enum_names_by_type:
        prvi_literal = next(iter(enum_names_by_type[type_name].literals)).name
        return f"SAEnum({type_name})", type_name, prvi_literal
    sql = SQL_TYPE_MAP.get(type_name, "String(100)")
    py = PY_TYPE_MAP.get(type_name, "str")
    sample = SAMPLE_VALUE_MAP.get(type_name, "primer")
    return sql, py, sample

MANY = 9999  # BESSER export koristi 9999 kao "unbounded"

class_by_name = {c.name: c for c in all_classes}
fk_fields_by_class = {c.name: [] for c in all_classes}          # 1:N -> FK kolone
relationships_by_class = {c.name: [] for c in all_classes}       # SQLAlchemy relationship() pozivi
m2m_associations = []                                             # za association table
m2m_create_fields_by_class = {c.name: [] for c in all_classes}   # role imena za *_ids polja u Create schemi
m2m_role_to_class = {}                                            # role -> ciljna klasa (za validaciju/repo)

for assoc in domain_model.associations:
    ends = sorted(assoc.ends, key=lambda e: e.name)  # determinizam - uvek isti redosled
    e1, e2 = ends[0], ends[1]
    is_many_to_many = e1.multiplicity.max >= MANY and e2.multiplicity.max >= MANY

    if is_many_to_many:
        class_a, role_a = e2.type.name, e1.name
        class_b, role_b = e1.type.name, e2.name
        table_name = f"{class_a.lower()}_{class_b.lower()}"
        m2m_associations.append({
            "table_name": table_name,
            "class_a": class_a, "table_a": class_a.lower(), "role_a": role_a,
            "class_b": class_b, "table_b": class_b.lower(), "role_b": role_b,
            "attr_on_a": role_a,
            "attr_on_b": role_b,
        })
        m2m_create_fields_by_class[class_a].append(role_a)
        m2m_role_to_class[role_a] = e1.type.name
        m2m_create_fields_by_class[class_b].append(role_b)
        m2m_role_to_class[role_b] = e2.type.name
    else:
        if e1.multiplicity.max <= 1:
            one_end, many_end = e1, e2
        else:
            one_end, many_end = e2, e1

        one_class, many_class = one_end.type.name, many_end.type.name
        fk_column = f"{one_end.name}_id"

        fk_fields_by_class[many_class].append({
            "column_name": fk_column,
            "ref_table": one_class.lower(),
        })
        relationships_by_class[one_class].append({
            "attr_name": many_end.name,
            "target_class": many_class,
            "back_populates": one_end.name,
        })
        relationships_by_class[many_class].append({
            "attr_name": one_end.name,
            "target_class": one_class,
            "back_populates": many_end.name,
        })

def build_class_context(cls):
    attrs = []
    for a in cls.attributes:
        sql_type, py_type, sample = resolve_type(a.type, a.name)
        attrs.append({"name": a.name, "sql_type": sql_type, "py_type": py_type, "sample": sample})
    temporal_attrs = [a for a in attrs if a["py_type"] in ("date", "datetime", "time")]
    display_attr = next((a["name"] for a in attrs if a["py_type"] == "str"), "id")
    return {
        "name": cls.name,
        "lower": cls.name.lower(),
        "table_name": cls.name.lower(),
        "attributes": attrs,
        "fk_fields": fk_fields_by_class[cls.name],
        "relationships": relationships_by_class[cls.name],
        "m2m_create_fields": m2m_create_fields_by_class[cls.name],
        "display_attr": display_attr,
        "temporal_attrs": temporal_attrs,
    }

classes_ctx = [build_class_context(c) for c in all_classes]
class_names = [c.name for c in all_classes]
class_ctx_by_name = {c["name"]: c for c in classes_ctx}

m2m_target_class_names = sorted(set(m2m_role_to_class.values()))
m2m_role_display_attr = {
    role: class_ctx_by_name[target]["display_attr"]
    for role, target in m2m_role_to_class.items()
}

enums_ctx = [
    {"name": e.name, "literals": [lit.name for lit in e.literals]}
    for e in all_enums
]

def render(template_name, output_path, **ctx):
    tpl = env.get_template(template_name)
    content = tpl.render(**ctx)
    with open(output_path, "w") as f:
        f.write(content)
    print(f"  generisano: {os.path.relpath(output_path, BASE_DIR)}")

print("Generisanje pokrenuto...\n")

render("enum.py.j2", os.path.join(OUTPUT_DIR, "enums.py"), enums=enums_ctx)

# generated/__init__.py da bi paket radio (potrebno za sve buduce import-e)
open(os.path.join(OUTPUT_DIR, "__init__.py"), "w").close()

print("\nGenerisanje zavrseno.")