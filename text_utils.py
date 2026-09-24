def sanitize_text(content: str) -> str:
    if not content:
        return ""

    return content.strip()


def parse_cors_origins(value: str) -> list[str]:
    if not value:
        return []

    return [
        origin.strip()
        for origin in value.split(",")
        if origin.strip()
    ]