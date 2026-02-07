from openlocationcode import openlocationcode as olc

# Default reference location (you can change this)
# Example: Chennai, India
REFERENCE_LAT = 13.0827
REFERENCE_LNG = 80.2707


def extract_plus_code(text):
    import re
    match = re.search(r"[23456789CFGHJMPQRVWX]{4,8}\+[23456789CFGHJMPQRVWX]{2,3}", text)
    return match.group(0) if match else None


def decode_plus(code):
    try:
        # If full Plus Code → decode directly
        if olc.isFull(code):
            loc = olc.decode(code)

        # If short Plus Code → recover using reference city
        elif olc.isShort(code):
            recovered = olc.recoverNearest(code, REFERENCE_LAT, REFERENCE_LNG)
            loc = olc.decode(recovered)

        else:
            return None, None

        return loc.latitudeCenter, loc.longitudeCenter

    except Exception:
        # Never crash backend
        return None, None
