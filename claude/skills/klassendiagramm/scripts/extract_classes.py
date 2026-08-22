#!/usr/bin/env python3
"""Extrahiert ein UML-Klassendiagramm (PlantUML-Syntax) aus Python-Quelldateien via ast.

Nutzt ausschliesslich die Python-Standardbibliothek, kein pip-Install noetig.
Verknuepft Klassen ueber die uebergebenen Dateien hinweg per Namensabgleich
(keine Import-Auflösung) - siehe SKILL.md, Abschnitt "Umfang der Code-Analyse".
"""
import argparse
import ast
import re
import sys
from pathlib import Path

CONTAINER_TYPES = {
    "List", "list", "Set", "set", "FrozenSet", "frozenset",
    "Sequence", "Iterable", "Tuple", "tuple", "Collection",
}
ENUM_BASES = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag"}
INTERFACE_MARKER_BASES = {"ABC", "Protocol"}
SKIP_BASES = ENUM_BASES | INTERFACE_MARKER_BASES | {"object"}


def visibility(name: str) -> str:
    if name.startswith("__") and not name.endswith("__"):
        return "-"
    if name.startswith("_"):
        return "#"
    return "+"


def unparse(node) -> str | None:
    if node is None:
        return None
    try:
        text = ast.unparse(node)
    except Exception:
        return None
    # Forward-Referenzen wie `owner: "Owner"` unparsen zu "'Owner'" - fuer die Anzeige
    # und den Typabgleich stoeren die Anfuehrungszeichen, also entfernen.
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "'\"":
        return text[1:-1]
    return text


def base_name(node) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return unparse(node) or "?"


def decorator_name(node) -> str:
    target = node.func if isinstance(node, ast.Call) else node
    return base_name(target)


class ClassInfo:
    def __init__(self, name: str, qualname: str, source_file: str):
        self.name = name
        self.qualname = qualname
        self.source_file = source_file
        self.bases: list[str] = []
        self.attributes: dict[str, str | None] = {}
        self.methods: list[dict] = []
        self.enum_values: list[str] = []
        self.is_enum = False
        self.is_interface = False
        self.is_abstract = False


def collect_self_attr(target, annotation, into: dict):
    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
        if annotation is not None:
            into[target.attr] = unparse(annotation)
        else:
            into.setdefault(target.attr, None)


def extract_class(node: ast.ClassDef, module_prefix: str, source_file: str) -> ClassInfo:
    qualname = f"{module_prefix}.{node.name}" if module_prefix else node.name
    info = ClassInfo(node.name, qualname, source_file)
    info.bases = [base_name(b) for b in node.bases]
    info.is_enum = any(b in ENUM_BASES for b in info.bases)

    for item in node.body:
        if info.is_enum:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                info.enum_values.append(item.target.id)
            elif isinstance(item, ast.Assign):
                for t in item.targets:
                    if isinstance(t, ast.Name):
                        info.enum_values.append(t.id)
            continue
        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
            info.attributes.setdefault(item.target.id, unparse(item.annotation))
        elif isinstance(item, ast.Assign):
            for t in item.targets:
                if isinstance(t, ast.Name):
                    info.attributes.setdefault(t.id, None)

    has_methods = False
    all_abstract = True

    for item in node.body:
        if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = [decorator_name(d) for d in item.decorator_list]
        is_static = "staticmethod" in decorators or "classmethod" in decorators
        is_abstract = "abstractmethod" in decorators

        if item.name == "__init__":
            param_types = {
                a.arg: unparse(a.annotation)
                for a in item.args.args + item.args.kwonlyargs
                if a.annotation is not None
            }
            for stmt in ast.walk(item):
                if isinstance(stmt, ast.AnnAssign):
                    collect_self_attr(stmt.target, stmt.annotation, info.attributes)
                elif isinstance(stmt, ast.Assign):
                    for t in stmt.targets:
                        if (
                            isinstance(t, ast.Attribute)
                            and isinstance(t.value, ast.Name)
                            and t.value.id == "self"
                            and isinstance(stmt.value, ast.Name)
                            and stmt.value.id in param_types
                        ):
                            # self.x = x, wobei x ein typisierter Konstruktor-Parameter ist:
                            # Typ wird strukturell übernommen, nicht geraten.
                            info.attributes.setdefault(t.attr, param_types[stmt.value.id])
                        else:
                            collect_self_attr(t, None, info.attributes)
            continue  # Konstruktor selbst nicht als Methode auflisten

        if item.name.startswith("__") and item.name.endswith("__"):
            continue  # sonstige Dunder-Methoden nicht anzeigen

        has_methods = True
        if not is_abstract:
            all_abstract = False

        args = item.args
        arg_list = args.args[1:] if (args.args and args.args[0].arg in ("self", "cls")) else args.args
        params = []
        for a in arg_list:
            t = unparse(a.annotation)
            params.append(f"{a.arg}: {t}" if t else a.arg)
        returns = unparse(item.returns)
        if returns == "None":
            returns = "void"  # UML-Konvention statt Pythons None

        info.methods.append({
            "name": item.name,
            "visibility": visibility(item.name),
            "params": params,
            "returns": returns,
            "static": is_static,
            "abstract": is_abstract,
        })

    info.is_interface = ("Protocol" in info.bases) or (
        "ABC" in info.bases and has_methods and all_abstract
    )
    info.is_abstract = (not info.is_interface) and any(m["abstract"] for m in info.methods)
    return info


def collect_classes(paths: list[Path]) -> list[ClassInfo]:
    classes = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        module_prefix = path.stem
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.append(extract_class(node, module_prefix, str(path)))
    return classes


CONTAINER_RE = re.compile(r"^(\w+)\[(.+)\]$")
OPTIONAL_RE = re.compile(r"^Optional\[(.+)\]$")


def resolve_target(type_str: str | None, known: dict[str, ClassInfo]):
    """Liefert (ZielQualname, ist_multiwertig) oder (None, False), wenn kein Bezug erkennbar ist."""
    if not type_str:
        return None, False
    t = type_str.strip()
    m = OPTIONAL_RE.match(t)
    if m:
        t = m.group(1).strip()
    m = CONTAINER_RE.match(t)
    if m:
        container, inner = m.group(1), m.group(2)
        inner_name = inner.split(",")[0].strip().strip("'\"")
        if container in CONTAINER_TYPES and inner_name in known:
            return known[inner_name].qualname, True
        return None, False
    t = t.strip("'\"")
    if t in known:
        return known[t].qualname, False
    return None, False


def render_puml(classes: list[ClassInfo], skinparams: str) -> str:
    known_by_name = {c.name: c for c in classes}
    lines = ["@startuml", skinparams.rstrip(), ""]

    for c in classes:
        if c.is_enum:
            lines.append(f'enum "{c.name}" as {c.qualname} {{')
            for v in c.enum_values:
                lines.append(f"  {v}")
            lines.append("}")
        elif c.is_interface:
            lines.append(f'interface "{c.name}" as {c.qualname} {{')
            _emit_members(lines, c)
            lines.append("}")
        else:
            keyword = "abstract class" if c.is_abstract else "class"
            lines.append(f'{keyword} "{c.name}" as {c.qualname} {{')
            _emit_members(lines, c)
            lines.append("}")
        lines.append("")

    edges = []
    for c in classes:
        for b in c.bases:
            if b in SKIP_BASES:
                continue
            parent = known_by_name.get(b)
            if parent is None:
                continue  # externe Basisklasse ausserhalb der uebergebenen Dateien - nicht gezeichnet
            arrow = "..|>" if parent.is_interface else "--|>"
            edges.append(f"{c.qualname} {arrow} {parent.qualname}")

        for attr_name, attr_type in c.attributes.items():
            target_qualname, is_multi = resolve_target(attr_type, known_by_name)
            if target_qualname is None or target_qualname == c.qualname:
                continue
            if is_multi:
                edges.append(f'{c.qualname} --> "*" {target_qualname} : {attr_name}')
            else:
                edges.append(f"{c.qualname} --> {target_qualname} : {attr_name}")

    lines.extend(edges)
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def _emit_members(lines: list[str], c: ClassInfo):
    for attr_name, attr_type in c.attributes.items():
        type_suffix = f" : {attr_type}" if attr_type else ""
        lines.append(f"  {visibility(attr_name)}{attr_name}{type_suffix}")
    for m in c.methods:
        prefix = "{abstract} " if m["abstract"] else ("{static} " if m["static"] else "")
        params = ", ".join(m["params"])
        ret = f" : {m['returns']}" if m["returns"] else ""
        lines.append(f"  {prefix}{m['visibility']}{m['name']}({params}){ret}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="Python-Quelldateien")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Zieldatei fuer .puml-Quelltext")
    args = parser.parse_args()

    for f in args.files:
        if not f.is_file():
            print(f"Fehler: Datei nicht gefunden: {f}", file=sys.stderr)
            sys.exit(1)

    skinparams_path = Path(__file__).parent / "skinparams.puml"
    skinparams = skinparams_path.read_text(encoding="utf-8")

    classes = collect_classes(args.files)
    if not classes:
        print("Fehler: Keine Klassen in den angegebenen Dateien gefunden.", file=sys.stderr)
        sys.exit(1)

    puml_text = render_puml(classes, skinparams)
    args.output.write_text(puml_text, encoding="utf-8")
    print(f"{len(classes)} Klasse(n) extrahiert -> {args.output}")


if __name__ == "__main__":
    main()
