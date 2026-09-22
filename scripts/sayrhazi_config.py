#!/usr/bin/env python3
"""Socle Sayrhazi : parseur YAML minimal + validation JSON-Schema, stdlib uniquement.

Couvre le sous-ensemble utilise par sayrhazi.yaml : mappings imbriques par
indentation (2 espaces), scalaires (string/bool/null/nombre), listes flow
`[a, b]`, commentaires `#`, chaines quotees. Le reste (multiligne `|`,
anchors...) est refuse avec une erreur claire.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


def _strip_comment(line: str) -> str:
    out: list[str] = []
    quote: str | None = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        elif ch == "#" and out and out[-1] in (" ", "\t"):
            break
        else:
            out.append(ch)
        i += 1
    return "".join(out).rstrip()


def _scalar(raw: str):
    s = raw.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    low = s.lower()
    if low in ("null", "~"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        return [] if not inner else [_scalar(p) for p in inner.split(",")]
    return s


def parse_simple_yaml(text: str) -> tuple[dict | None, str | None]:
    """Retourne (donnees, None) ou (None, message_erreur)."""
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for lineno, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if "\t" in raw[:indent]:
            return None, f"ligne {lineno} : tabulations interdites (espaces uniquement)"
        if indent % 2:
            return None, f"ligne {lineno} : indentation impaire ({indent} espaces)"
        content = line.strip()
        if ":" not in content and not content.startswith("- "):
            return None, f"ligne {lineno} : attendu `cle: valeur` (listes `- ` non supportees)"
        if content.startswith("- "):
            return None, f"ligne {lineno} : listes `- ` non supportees (utiliser `[a, b]`)"
        key, _, value = content.partition(":")
        key = key.strip()
        if not key or " " in key:
            return None, f"ligne {lineno} : cle invalide `{key}`"
        value = value.strip()
        if value.startswith(("|", ">")):
            return None, f"ligne {lineno} : blocs multiligne non supportes"
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if key in parent:
            return None, f"ligne {lineno} : cle dupliquee `{key}`"
        if value == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _scalar(value)
    return root, None


def _type_ok(value, want: str) -> bool:
    if want == "string":
        return isinstance(value, str)
    if want == "boolean":
        return isinstance(value, bool)
    if want == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if want == "array":
        return isinstance(value, list)
    if want == "object":
        return isinstance(value, dict)
    if want == "null":
        return value is None
    return True


def validate_against_schema(data: dict, schema: dict, path: str = "$") -> list[str]:
    """Verifie data contre un sous-ensemble JSON-Schema. Retourne les violations."""
    errors: list[str] = []
    want = schema.get("type")
    if want is not None:
        wants = [want] if isinstance(want, str) else list(want)
        if not any(_type_ok(data, w) for w in wants):
            return [f"{path} : type attendu {wants}, valeur {data!r}"]
    if "const" in schema and data != schema["const"]:
        errors.append(f"{path} : doit valoir {schema['const']!r}")
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path} : {data!r} non autorise (attendu : {schema['enum']})")
    if "minLength" in schema and isinstance(data, str) and len(data) < schema["minLength"]:
        errors.append(f"{path} : trop court (min {schema['minLength']})")
    if isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"{path} : cle requise manquante `{key}`")
        props = schema.get("properties", {})
        for key, value in data.items():
            if key in props:
                errors.extend(validate_against_schema(value, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path} : cle inattendue `{key}`")
    if isinstance(data, list) and "items" in schema:
        for i, value in enumerate(data):
            errors.extend(validate_against_schema(value, schema["items"], f"{path}[{i}]"))
    not_rule = schema.get("not")
    if isinstance(not_rule, dict) and "const" in not_rule and data == not_rule["const"]:
        errors.append(f"{path} : valeur interdite {data!r}")
    return errors


def load_schema(core_root: Path) -> tuple[dict | None, str | None]:
    """Charge schemas/sayrhazi.schema.json depuis la racine du noyau."""
    path = core_root / "schemas" / "sayrhazi.schema.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, f"schema illisible : {exc}"
    except json.JSONDecodeError as exc:
        return None, f"schema JSON invalide : {exc}"
