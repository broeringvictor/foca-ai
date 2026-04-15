


def format_errors(errors: list) -> list:
    formatted = []
    for err in errors:
        loc = err.get("loc", ())
        source = None
        field_parts = []
        for index, loc_item in enumerate(loc):
            if index == 0 and loc_item in {"body", "query", "path", "header", "cookie"}:
                source = str(loc_item)
                continue
            field_parts.append(str(loc_item))

        field = " → ".join(field_parts)
        message = err.get("msg", "")

        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")

        formatted.append(
            {"field": field or "geral", "message": message, "source": source}
        )

    return formatted
