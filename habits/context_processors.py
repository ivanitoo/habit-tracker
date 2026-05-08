from .traducciones import TRADUCCIONES


def idioma_processor(request):
    lang = request.GET.get("lang")
    if lang in ("en", "es"):
        request.session["lang"] = lang
    elif "lang" not in request.session:
        request.session["lang"] = "es"

    idioma = request.session.get("lang", "es")
    return {
        "lang": idioma,
        "t": lambda key: TRADUCCIONES.get(idioma, TRADUCCIONES["es"]).get(key, key),
    }
