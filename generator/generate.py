"""
Glavni generator skript. Cita model/salon_model.py (B-UML model) i za svaku klasu,
enumeraciju i OCL ograničenje generise odgovarajući Python kod koristeći Jinja2 template-e
iz generator/templates/.

Pokretanje:  python3 generator/generate.py
"""
import sys
import os
import re
import shutil
import json

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
# 1. Mapiranje B-UML tipova
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
# Tip atributa -> HTML input type (za generisane forme)
HTML_INPUT_TYPE_MAP = {
    "str": "text",
    "int": "number",
    "float": "number",
    "bool": "checkbox",
    "date": "date",
    "datetime": "datetime-local",
    "time": "time",
}

def humanize(name: str) -> str:
    """'radnoVremeOd' -> 'Radno vreme od', 'trajanjeMin' -> 'Trajanje min'."""
    spaced = re.sub(r'(?<!^)(?=[A-Z])', ' ', name).replace("_", " ")
    return spaced[:1].upper() + spaced[1:].lower()

all_classes = sorted((t for t in domain_model.types if isinstance(t, Class)), key=lambda c: c.name)
all_enums = sorted((t for t in domain_model.types if isinstance(t, Enumeration)), key=lambda e: e.name)
enum_names_by_type = {e.name: e for e in all_enums}
enum_names = [e.name for e in all_enums]

def resolve_type(buml_type, attr_name):
    """Vraća (sql_type, py_type, sample_value, enum_literals|None) za dati B-UML tip atributa."""
    type_name = getattr(buml_type, "name", None)
    if type_name in enum_names_by_type:
        literals = sorted(lit.name for lit in enum_names_by_type[type_name].literals)
        return f"SAEnum({type_name})", type_name, literals[0], literals
    sql = SQL_TYPE_MAP.get(type_name, "String(100)")
    py = PY_TYPE_MAP.get(type_name, "str")
    sample = SAMPLE_VALUE_MAP.get(type_name, "primer")
    return sql, py, sample, None

MANY = 9999  # BESSER export koristi 9999 kao "unbounded" (*)

class_by_name = {c.name: c for c in all_classes}
fk_fields_by_class = {c.name: [] for c in all_classes}          # 1:N -> FK kolone
relationships_by_class = {c.name: [] for c in all_classes}       # SQLAlchemy relationship() pozivi
m2m_associations = []                                             # za association_table
m2m_create_fields_by_class = {c.name: [] for c in all_classes}   # role imena za *_ids polja u Create schemi
m2m_role_to_class = {}                                            # role -> ciljna klasa (za validaciju/repo)

for assoc in sorted(domain_model.associations, key=lambda a: a.name):
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
    for a in sorted(cls.attributes, key=lambda x: x.name):  # determinizam - cls.attributes je set
        sql_type, py_type, sample, options = resolve_type(a.type, a.name)
        is_enum = options is not None
        attrs.append({
            "name": a.name,
            "sql_type": sql_type,
            "py_type": py_type,
            "sample": sample,
            "label": humanize(a.name),
            "is_enum": is_enum,
            "options": options,
            "html_type": "select" if is_enum else HTML_INPUT_TYPE_MAP.get(py_type, "text"),
        })
    temporal_attrs = [a for a in attrs if a["py_type"] in ("date", "datetime", "time")]
    str_attr_names = sorted(a["name"] for a in attrs if a["py_type"] == "str")
    display_attr = next(
        (n for n in ("naziv", "ime", "name", "title") if n in str_attr_names),
        str_attr_names[0] if str_attr_names else "id",
    )
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

# Klase koje se pojavljuju kao META N:N veze (moraju dobiti "Ref" schema za prikaz)
m2m_target_class_names = sorted(set(m2m_role_to_class.values()))
# role -> koji atribut ciljne klase prikazati (npr. 'usluga' -> 'naziv')
m2m_role_display_attr = {
    role: class_ctx_by_name[target]["display_attr"]
    for role, target in m2m_role_to_class.items()
}
# role -> lowercase ime ciljne klase (za fetch URL u frontendu, npr. 'usluga' -> 'usluga')
m2m_role_target_lower = {role: target.lower() for role, target in m2m_role_to_class.items()}

# FK kolone dobijaju "label" (za forme/listu) i "display_attr" ciljne klase
# (da frontend može da prikaže npr. ime klijenta umesto sirovog klijent_id broja)
lower_to_class_name = {c.name.lower(): c.name for c in all_classes}
for cls_ctx in classes_ctx:
    for fk in cls_ctx["fk_fields"]:
        target_ctx = class_ctx_by_name[lower_to_class_name[fk["ref_table"]]]
        fk["display_attr"] = target_ctx["display_attr"]
        fk["label"] = humanize(re.sub(r"_id$", "", fk["column_name"]))

# M2M linkovi po klasi - za repository.py: kroz koju asocijativnu tabelu,
# koja kolona je "moja" (own_column) a koja ciljna (target_column)
m2m_links_by_class = {c.name: [] for c in all_classes}
for m in m2m_associations:
    m2m_links_by_class[m["class_a"]].append({
        "role": m["role_a"],
        "table_name": m["table_name"],
        "own_column": f'{m["table_a"]}_id',
        "target_column": f'{m["table_b"]}_id',
        "target_class": m["class_b"],
    })
    m2m_links_by_class[m["class_b"]].append({
        "role": m["role_b"],
        "table_name": m["table_name"],
        "own_column": f'{m["table_b"]}_id',
        "target_column": f'{m["table_a"]}_id',
        "target_class": m["class_a"],
    })
for cls_ctx in classes_ctx:
    cls_ctx["m2m_links"] = m2m_links_by_class[cls_ctx["name"]]

# Sample Create payload po klasi (za Postman kolekciju) - koristi vec izracunate
# attr["sample"] vrednosti, fk sample id=1, m2m sample id liste=[1]
for cls_ctx in classes_ctx:
    payload = {a["name"]: a["sample"] for a in cls_ctx["attributes"]}
    for fk in cls_ctx["fk_fields"]:
        payload[fk["column_name"]] = 1
    for role in cls_ctx["m2m_create_fields"]:
        payload[f"{role}_ids"] = [1]
    cls_ctx["sample_payload"] = payload

# Postman kolekcija - jedna folder po klasi sa List/Get/Create/Update/Delete
# zahtevima, prati REST konvenciju /{klasa.lower}[/{id}] koju ce routes.py.j2
# koristiti. Kolekcija se gradi kao obican Python dict pa serijalizuje u JSON
# ovde (umesto rucnog sastavljanja JSON-a u Jinja-i), da bi izlaz uvek bio
# validan JSON.
POSTMAN_BASE_URL = "http://localhost:8000"

def build_postman_folder(cls_ctx):
    base = "{{base_url}}/" + cls_ctx["lower"]
    payload_raw = json.dumps(cls_ctx["sample_payload"], indent=2, ensure_ascii=False)

    def request_item(name, method, path_suffix="", with_body=False):
        url_raw = base + path_suffix
        path_parts = [cls_ctx["lower"]] + ([ "1" ] if path_suffix else [])
        request = {
            "method": method,
            "header": [{"key": "Content-Type", "value": "application/json"}] if with_body else [],
            "url": {"raw": url_raw, "host": ["{{base_url}}"], "path": path_parts},
        }
        if with_body:
            request["body"] = {
                "mode": "raw",
                "raw": payload_raw,
                "options": {"raw": {"language": "json"}},
            }
        return {"name": name, "request": request}

    return {
        "name": cls_ctx["name"],
        "item": [
            request_item(f"List {cls_ctx['name']}", "GET"),
            request_item(f"Get {cls_ctx['name']} by id", "GET", "/1"),
            request_item(f"Create {cls_ctx['name']}", "POST", with_body=True),
            request_item(f"Update {cls_ctx['name']}", "PUT", "/1", with_body=True),
            request_item(f"Delete {cls_ctx['name']}", "DELETE", "/1"),
        ],
    }

postman_collection = {
    "info": {
        "name": "Salon Lepote API",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "item": [build_postman_folder(c) for c in classes_ctx],
    "variable": [{"key": "base_url", "value": POSTMAN_BASE_URL}],
}
postman_collection_json = json.dumps(postman_collection, indent=2, ensure_ascii=False)

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

render("entity.py.j2", os.path.join(OUTPUT_DIR, "entities.py"),
       classes=classes_ctx, enum_names=enum_names)

render("association_table.py.j2", os.path.join(OUTPUT_DIR, "association_tables.py"),
       associations=m2m_associations)

render("schema.py.j2", os.path.join(OUTPUT_DIR, "schema.py"),
       classes=classes_ctx, enum_names=enum_names)

render("dto.py.j2", os.path.join(OUTPUT_DIR, "dto.py"),
       classes=classes_ctx, enum_names=enum_names)

render("converter.py.j2", os.path.join(OUTPUT_DIR, "converter.py"),
       classes=classes_ctx, class_names=class_names)

render("repository.py.j2", os.path.join(OUTPUT_DIR, "repository.py"),
       classes=classes_ctx, class_names=class_names, associations=m2m_associations)

# business_rules.py se ne generise iz modela (rucno napisane OCL invarijante) -
# samo se kopira u generated/, bez Jinja2 obrade
shutil.copyfile(
    os.path.join(os.path.dirname(__file__), "business_rules.py"),
    os.path.join(OUTPUT_DIR, "business_rules.py"),
)
print(f"  generisano: {os.path.relpath(os.path.join(OUTPUT_DIR, 'business_rules.py'), BASE_DIR)}")

render("postman_collection.j2", os.path.join(OUTPUT_DIR, "postman_collection.json"),
       collection_json=postman_collection_json)

# generated/__init__.py da bi paket radio (potrebno za sve buduce import-e)
open(os.path.join(OUTPUT_DIR, "__init__.py"), "w").close()

print("\nGenerisanje završeno.")