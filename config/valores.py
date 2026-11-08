import re

VALORES_DEFECTO = {
    "nombre_usuario": "Andre Strange - Sistemas",
    "tema_interfaz": "claro",
    "idioma": "es-ES",
    "tamaño_fuente": 12,
    "color_barra_menu": "#e0e0e0",
    "color_letra": "#000000",
    "foto_perfil": "",
}

TEMAS = ("claro", "oscuro")
IDIOMAS = ("es", "es-ES", "en", "en-US")
FUENTE_MIN = 8
FUENTE_MAX = 32

patron_color = re.compile(r"#[0-9a-fA-F]{6}")


def es_color(valor):
    return isinstance(valor, str) and patron_color.fullmatch(valor) is not None


# type() en vez de isinstance para que True/False no pasen como int
reglas = {
    "nombre_usuario": lambda v: isinstance(v, str) and v.strip() != "",
    "tema_interfaz": lambda v: v in TEMAS,
    "idioma": lambda v: v in IDIOMAS,
    "tamaño_fuente": lambda v: type(v) is int and FUENTE_MIN <= v <= FUENTE_MAX,
    "color_barra_menu": es_color,
    "color_letra": es_color,
    "foto_perfil": lambda v: isinstance(v, str),
}


# revisa campo por campo, si uno esta mal o falta se usa el de defecto
# y se devuelve la lista de campos malos para avisarle al usuario
def validar(datos):
    config = VALORES_DEFECTO.copy()
    if not isinstance(datos, dict):
        return config, list(VALORES_DEFECTO)

    errores = []
    for campo, regla in reglas.items():
        valor = datos.get(campo)
        if regla(valor):
            config[campo] = valor
        else:
            errores.append(campo)
    return config, errores
