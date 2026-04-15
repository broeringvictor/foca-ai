


def format_errors(errors: list) -> list:
    formatted = []
    for err in errors:
        field = " → ".join(str(loc) for loc in err["loc"] if loc != "body")
        message = err["msg"]

        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")

        formatted.append({"field": field or "geral", "message": message})

    return formatted
