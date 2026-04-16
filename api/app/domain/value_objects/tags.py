from typing import Annotated

from pydantic import AfterValidator

MAX_TAGS = 20
MAX_TAG_LEN = 30


def _normalize_tags(raw: list[str]) -> list[str]:
    """Valida e normaliza uma lista de tags.

    Regras:
        - Descarta tags vazias após ``strip``.
        - Deduplica case-insensitive (preserva a primeira ocorrência).
        - Cada tag deve ter no máximo 30 caracteres.
        - Máximo de 20 tags.
    """

    result: list[str] = []
    seen: set[str] = set()
    for tag in raw:
        if not isinstance(tag, str):
            raise ValueError("Tag deve ser string")
        tag = tag.strip()
        if not tag:
            continue
        if len(tag) > MAX_TAG_LEN:
            raise ValueError("Tag excede 30 caracteres")
        lowered = tag.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(tag)

    if len(result) > MAX_TAGS:
        raise ValueError("Quantidade máxima de tags excedida")

    return result


Tags = Annotated[list[str], AfterValidator(_normalize_tags)]
