def get_product_package(slug: str) -> str:
    """
    Determine product package (RU / INT) based on slug.

    Business rules:
    - '-ru-' → RU version
    - '-int-' → INT version

    Side effects:
    - None

    Invariants:
    - Returns '—' if format is unknown
    """

    if "-ru-" in slug:
        return "RU"
    if "-int-" in slug:
        return "INT"
    return "—"