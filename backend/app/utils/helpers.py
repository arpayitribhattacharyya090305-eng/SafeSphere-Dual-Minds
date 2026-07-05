def get_iso_lang_code(language_name: str) -> str:
    """
    Return the English ISO 639-1 code for TTS.
    """
    return "en"

def format_distance(distance_km: float) -> str:
    if distance_km < 1.0:
        return f"{int(distance_km * 1000)} meters"
    return f"{distance_km:.2f} km"
