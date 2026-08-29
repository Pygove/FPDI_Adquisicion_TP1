"""
analizar_carpeta.py

Script simple que recibe la ruta de una carpeta por línea de comandos,
recorre todas las imágenes que encuentra dentro (formatos estándar y RAW)
y reporta información de cada una por consola.

Uso:
    python analizar_carpeta.py ruta/a/la/carpeta
"""

import sys
import os
import cv2

# Extensiones que consideramos "estándar" (se cargan con cv2.imread)
EXTENSIONES_ESTANDAR = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")

# Extensiones RAW (se cargan con rawpy)
EXTENSIONES_RAW = (".nef", ".cr2", ".arw", ".dng")


def gms_a_grados_decimales(valor_gms, referencia):
    """
    Convierte una coordenada GPS del formato crudo de exifread
    (grados, minutos, segundos, como fracciones) a grados decimales.

    'referencia' es el hemisferio ('N', 'S', 'E' o 'W'): si es S o W,
    el resultado se devuelve en negativo.
    """
    grados, minutos, segundos = [float(x.num) / float(x.den) for x in valor_gms.values]

    decimal = grados + (minutos / 60.0) + (segundos / 3600.0)

    if referencia in ("S", "W"):
        decimal = -decimal

    return decimal


def mostrar_exif(ruta):
    """
    Lee y muestra los metadatos EXIF de un archivo, leyéndolo directamente
    desde disco con exifread (no desde el array ya decodificado).

    Esto es importante porque en archivos RAW los píxeles se decodifican
    con rawpy, pero los metadatos EXIF embebidos se leen igual con exifread,
    tanto para imágenes estándar como para RAW.

    Devuelve una tupla (tiene_exif, tiene_geolocalizacion).
    """
    try:
        import exifread
    except ImportError:
        print("Error: la librería 'exifread' no está instalada, no se pueden leer los metadatos EXIF.")
        print("Instalala con: pip install exifread")
        return False, False

    with open(ruta, "rb") as f:
        tags = exifread.process_file(f, details=False)

    if not tags:
        print("EXIF: no se encontraron metadatos EXIF en esta imagen.")
        return False, False

    # Mapeo de las etiquetas EXIF "simples" que nos interesan a un nombre legible
    etiquetas_interes = {
        "EXIF ISOSpeedRatings": "ISO",
        "EXIF FNumber": "Apertura (f-number)",
        "EXIF ExposureTime": "Velocidad de obturación",
        "EXIF FocalLength": "Distancia focal",
        "Image Model": "Modelo de equipo",
    }

    print("EXIF encontrado:")
    for clave_exif, etiqueta_legible in etiquetas_interes.items():
        if clave_exif in tags:
            print(f"  {etiqueta_legible}: {tags[clave_exif]}")

    # Geolocalización: viene como grados/minutos/segundos, hay que convertirla
    tiene_geolocalizacion = False
    claves_gps = ("GPS GPSLatitude", "GPS GPSLatitudeRef", "GPS GPSLongitude", "GPS GPSLongitudeRef")

    if all(clave in tags for clave in claves_gps):
        latitud = gms_a_grados_decimales(tags["GPS GPSLatitude"], str(tags["GPS GPSLatitudeRef"]))
        longitud = gms_a_grados_decimales(tags["GPS GPSLongitude"], str(tags["GPS GPSLongitudeRef"]))
        print(f"  Geolocalización: {latitud:.4f}, {longitud:.4f}")
        tiene_geolocalizacion = True
    else:
        print("  Geolocalización: sin geolocalización")

    return True, tiene_geolocalizacion


def main():
    # Verificamos que se haya pasado la carpeta como argumento
    if len(sys.argv) != 2:
        print("Uso: python analizar_carpeta.py <ruta_de_la_carpeta>")
        return

    carpeta = sys.argv[1]

    # Verificamos que la carpeta exista y sea un directorio
    if not os.path.isdir(carpeta):
        print(f"Error: '{carpeta}' no es una carpeta válida.")
        return

    # Contadores para el resumen final
    total_procesadas = 0
    total_raw = 0
    total_errores = 0
    total_con_exif = 0
    total_con_geolocalizacion = 0

    # Recorremos los archivos de la carpeta (orden alfabético, sin subcarpetas)
    for nombre_archivo in sorted(os.listdir(carpeta)):
        ruta = os.path.join(carpeta, nombre_archivo)

        # Ignoramos subcarpetas, solo nos interesan archivos
        if not os.path.isfile(ruta):
            continue

        _, extension = os.path.splitext(nombre_archivo)
        extension = extension.lower()

        # Si la extensión no es ni estándar ni RAW, ignoramos el archivo (no es una imagen conocida)
        if extension not in EXTENSIONES_ESTANDAR and extension not in EXTENSIONES_RAW:
            continue

        print(f"\n--- Analizando: {nombre_archivo} ---")

        img = None
        es_raw = extension in EXTENSIONES_RAW

        if es_raw:
            # Carga de imagen RAW usando rawpy
            try:
                import rawpy
            except ImportError:
                print("Error: la librería 'rawpy' no está instalada, no se puede leer este archivo RAW.")
                print("Instalala con: pip install rawpy")
                total_errores += 1
                continue

            try:
                with rawpy.imread(ruta) as raw:
                    # postprocess() "revela" el RAW y devuelve un array RGB manipulable
                    img = raw.postprocess()
                print("Cargada como RAW con rawpy. Nota: rawpy devuelve la imagen en RGB (no BGR).")
            except Exception as e:
                print(f"Error al leer el archivo RAW con rawpy: {e}")
                total_errores += 1
                continue
        else:
            # Carga de imagen estándar con OpenCV
            img = cv2.imread(ruta)
            if img is not None:
                print("Cargada como estándar con cv2.imread. Nota: OpenCV representa la imagen en BGR (no RGB).")

        # Si no se pudo cargar la imagen (corrupta, formato no soportado, etc.)
        if img is None:
            print(f"Error: no se pudo leer la imagen '{nombre_archivo}'.")
            total_errores += 1
            continue

        # Shape y dtype
        if img.ndim == 3:
            alto, ancho, canales = img.shape
        else:
            alto, ancho = img.shape
            canales = 1

        print(f"Shape: {img.shape} (alto={alto}, ancho={ancho}, canales={canales})")
        print(f"dtype: {img.dtype}")

        # Tamaño en disco vs en memoria
        tamano_disco = os.path.getsize(ruta)
        tamano_memoria = img.nbytes
        print(f"Tamaño en disco: {tamano_disco} bytes")
        print(f"Tamaño en memoria: {tamano_memoria} bytes")

        # Metadatos EXIF: se leen del archivo en disco, no del array decodificado.
        # Sirve tanto para imágenes estándar como para RAW.
        tiene_exif, tiene_geolocalizacion = mostrar_exif(ruta)

        total_procesadas += 1
        if es_raw:
            total_raw += 1
        if tiene_exif:
            total_con_exif += 1
        if tiene_geolocalizacion:
            total_con_geolocalizacion += 1

    # Resumen final
    print("\n--- Resumen ---")
    print(f"Imágenes procesadas correctamente: {total_procesadas}")
    print(f"De esas, formato RAW: {total_raw}")
    print(f"Imágenes con metadatos EXIF disponibles: {total_con_exif} de {total_procesadas}")
    print(f"Imágenes con geolocalización disponible: {total_con_geolocalizacion} de {total_procesadas}")
    print(f"Imágenes que no se pudieron leer: {total_errores}")


if __name__ == "__main__":
    main()
