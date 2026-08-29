"""
Script educativo para comparar el ISO usado en distintas fotos, a partir
de sus metadatos EXIF.

Idea general:
- Cada foto guarda en sus metadatos EXIF, entre otras cosas, el valor de
  ISO con el que fue tomada.
- A mayor ISO, el sensor (o el procesamiento posterior) amplifica más la
  señal captada. Eso permite fotografiar con menos luz, pero como
  "amplifica" también amplifica el ruido propio del sensor: por eso las
  fotos en ISO alto suelen verse con más grano/ruido visible, en especial
  en cámaras con sensores de píxeles chicos (como las de celulares),
  donde cada píxel capta menos luz y el ruido relativo es mayor.

Uso:
    python3 comparar_iso.py foto1.jpg foto2.jpg foto3.jpg ...
"""

import sys

from PIL import Image
from PIL.ExifTags import TAGS


def obtener_iso(ruta_imagen):
    """
    Intenta obtener el valor de ISO desde los metadatos EXIF de una imagen.

    Devuelve el valor de ISO (int) si lo encuentra, o None si la imagen
    no tiene EXIF o no tiene el campo de ISO.
    """
    try:
        imagen = Image.open(ruta_imagen)
        datos_exif = imagen.getexif()
    except Exception as error:
        print(f"No se pudo abrir '{ruta_imagen}': {error}")
        return None

    if not datos_exif:
        # La imagen no tiene metadatos EXIF en absoluto.
        return None

    # Recorremos los tags EXIF buscando el que corresponde a ISO.
    # El nombre del tag puede ser "ISOSpeedRatings" o "PhotographicSensitivity"
    # según la versión de EXIF, por eso probamos ambos nombres.
    for codigo_tag, valor in datos_exif.items():
        nombre_tag = TAGS.get(codigo_tag, codigo_tag)
        if nombre_tag in ("ISOSpeedRatings", "PhotographicSensitivity", "ISO"):
            # A veces el valor viene como una tupla/lista de un solo elemento.
            if isinstance(valor, (tuple, list)):
                valor = valor[0]
            return int(valor)

    # A veces el ISO está dentro del sub-bloque "Exif" (IFD anidado).
    try:
        exif_extendido = imagen.getexif().get_ifd(0x8769)  # 0x8769 = tag "Exif IFD"
        for codigo_tag, valor in exif_extendido.items():
            nombre_tag = TAGS.get(codigo_tag, codigo_tag)
            if nombre_tag in ("ISOSpeedRatings", "PhotographicSensitivity", "ISO"):
                if isinstance(valor, (tuple, list)):
                    valor = valor[0]
                return int(valor)
    except Exception:
        pass

    return None


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 comparar_iso.py imagen1 imagen2 [imagen3 ...]")
        print("(se necesitan al menos dos imágenes para comparar)")
        sys.exit(1)

    rutas_imagenes = sys.argv[1:]

    # Guardamos pares (ruta, iso) donde iso puede ser None si no se encontró.
    resultados = []
    for ruta in rutas_imagenes:
        iso = obtener_iso(ruta)
        resultados.append((ruta, iso))

    # Ordenamos de menor a mayor ISO. Las imágenes sin ISO (None) las
    # mandamos al final, para no romper la comparación numérica.
    resultados_ordenados = sorted(
        resultados, key=lambda item: (item[1] is None, item[1])
    )

    # --- Tabla simple por consola ---
    print("\n--- ISO por imagen (ordenado de menor a mayor) ---")
    print(f"{'Archivo':<40} | ISO")
    print("-" * 55)
    for ruta, iso in resultados_ordenados:
        texto_iso = str(iso) if iso is not None else "sin datos EXIF / sin ISO"
        print(f"{ruta:<40} | {texto_iso}")

    print("\nRecordar: a mayor ISO, mayor amplificación de la señal del sensor,")
    print("y por lo tanto más ruido visible (grano) en la imagen, especialmente")
    print("en sensores con píxeles chicos (por ejemplo, cámaras de celulares).")

    # --- Ayuda visual opcional con matplotlib ---
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no está disponible: se omite la comparación visual)")
        return

    cantidad_imagenes = len(resultados_ordenados)
    figura, ejes = plt.subplots(1, cantidad_imagenes, figsize=(4 * cantidad_imagenes, 4))

    # Si hay una sola imagen, matplotlib no devuelve una lista de ejes,
    # así que la convertimos en lista para poder iterar igual.
    if cantidad_imagenes == 1:
        ejes = [ejes]

    for eje, (ruta, iso) in zip(ejes, resultados_ordenados):
        try:
            imagen = Image.open(ruta)
            eje.imshow(imagen)
        except Exception as error:
            eje.text(0.5, 0.5, "no se pudo cargar", ha="center", va="center")
            print(f"No se pudo mostrar '{ruta}': {error}")

        titulo = f"ISO {iso}" if iso is not None else "ISO desconocido"
        eje.set_title(titulo)
        eje.axis("off")  # Ocultamos los ejes, no aportan info útil acá.

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
