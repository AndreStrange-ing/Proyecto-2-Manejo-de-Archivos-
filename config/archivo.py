import json
import os
import shutil

from config.valores import VALORES_DEFECTO, validar

carpeta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
carpeta_perfiles = os.path.join(carpeta, "perfiles")
ruta_config = os.path.join(carpeta, "config.json")

# caracteres que windows no deja usar en nombres de archivo
caracteres_invalidos = '\\/:*?"<>|'


# el bak y el tmp van al lado del json con el mismo nombre
def rutas_extra(ruta):
    base = os.path.splitext(ruta)[0]
    return base + ".bak", base + ".tmp"


def leer_json(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


# devuelve (config, aviso), aviso queda en None si no hubo problemas
def cargar(ruta=ruta_config):
    nombre = os.path.basename(ruta)
    ruta_bak = rutas_extra(ruta)[0]
    aviso = None
    try:
        datos = leer_json(ruta)
    except FileNotFoundError:
        return VALORES_DEFECTO.copy(), f"No existe {nombre}, se usan los valores por defecto."
    except PermissionError:
        return VALORES_DEFECTO.copy(), f"No hay permiso para leer {nombre}, se usan los valores por defecto."
    except ValueError:
        # json mal formado o no esta en utf-8, se intenta con el respaldo
        try:
            datos = leer_json(ruta_bak)
            aviso = f"{nombre} está dañado, se cargó el respaldo {os.path.basename(ruta_bak)}."
        except (OSError, ValueError):
            return VALORES_DEFECTO.copy(), f"{nombre} está dañado y el respaldo tampoco sirve, se usan los valores por defecto."
    except OSError as e:
        return VALORES_DEFECTO.copy(), f"No se pudo leer {nombre} ({e}), se usan los valores por defecto."

    config, errores = validar(datos)
    if errores:
        campos = "Valores inválidos, se usaron los de defecto en: " + ", ".join(errores)
        aviso = f"{aviso}\n{campos}" if aviso else campos
    return config, aviso


def json_valido(ruta):
    try:
        leer_json(ruta)
        return True
    except (OSError, ValueError):
        return False


# 1. escribir el tmp  2. copiar el json actual al bak  3. reemplazar
# si algo falla antes del paso 3 el json original queda intacto
def guardar(config, ruta=ruta_config):
    ruta_bak, ruta_tmp = rutas_extra(ruta)
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta_tmp, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        # si el json actual esta dañado no se copia, para no perder un bak bueno
        # copyfile y no copy2, copy2 tambien copia si el archivo es de solo lectura
        if json_valido(ruta):
            shutil.copyfile(ruta, ruta_bak)
        os.replace(ruta_tmp, ruta)
    except PermissionError:
        borrar(ruta_tmp)
        return "No hay permiso para escribir el archivo, no se guardó la configuración."
    except OSError as e:
        borrar(ruta_tmp)
        return f"No se pudo guardar la configuración ({e})."
    return None


def borrar(ruta):
    try:
        os.remove(ruta)
    except OSError:
        pass


# perfiles: cada uno es un json aparte en data/perfiles y usa el mismo cargar y guardar

def ruta_perfil(nombre):
    return os.path.join(carpeta_perfiles, nombre + ".json")


def listar_perfiles():
    try:
        return sorted(os.path.splitext(n)[0] for n in os.listdir(carpeta_perfiles) if n.endswith(".json"))
    except OSError:
        return []


def nombre_perfil_valido(nombre):
    # windows quita solo los puntos y espacios del final, mejor no aceptarlos
    return (nombre != "" and nombre == nombre.strip() and not nombre.endswith(".")
            and not any(c in caracteres_invalidos for c in nombre))
