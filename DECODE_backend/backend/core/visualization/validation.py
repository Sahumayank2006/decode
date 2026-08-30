def validate_svg(svg):
    if not svg:
        return False

    if "<svg" not in svg:
        return False

    if "</svg>" not in svg:
        return False

    return True
