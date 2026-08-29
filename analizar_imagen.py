"""
analizar_imagen.py

Script simple que recibe la ruta de una imagen por línea de comandos y
reporta información sobre ella: dimensiones, canales, dtype, tamaño en
memoria vs en disco, y espacio de color.

Uso:
    python analizar_imagen.py ruta/a/la/imagen.jpg
"""

import sys
import os
import cv2

# Extensiones típicas de archivos RAW de cámara
EXTENSIONES_RAW = (".nef", ".cr2", ".arw", ".dng")


def analizar_raw(ruta):
    """Carga una imagen RAW usando rawpy y devuelve el array como numpy."""
    try:
        import rawpy
    except ImportError:
        print("Error: el archivo parece ser RAW, pero la librería 'rawpy' no está instalada.")
        print("Instalala con: pip install rawpy")
        return None

    try:
        with rawpy.imread(ruta) as raw:
            # postprocess() devuelve la imagen ya "revelada" como array RGB
            img = raw.postprocess()
        print("Nota: archivo RAW cargado con rawpy (no con cv2.imread).")
        print("La imagen resultante está en formato RGB (postprocesada por rawpy), no BGR.")
        return img
    except Exception as e:
        print(f"Error al leer el archivo RAW con rawpy: {e}")
        return None


def main():
    # Verificamos que se haya pasado la ruta como argumento
    if len(sys.argv) != 2:
        print("Uso: python analizar_imagen.py <ruta_de_la_imagen>")
        return

    ruta = sys.argv[1]

    # Verificamos que el archivo exista
    if not os.path.isfile(ruta):
        print(f"Error: el archivo '{ruta}' no existe.")
        return

    _, extension = os.path.splitext(ruta)
    extension = extension.lower()

    # Si es un formato RAW, usamos rawpy en vez de cv2.imread
    if extension in EXTENSIONES_RAW:
        img = analizar_raw(ruta)
    else:
        # cv2.imread carga la imagen y la representa internamente en BGR
        img = cv2.imread(ruta)
        if img is not None:
            print("Nota: la imagen fue cargada con cv2.imread.")
            print("OpenCV representa las imágenes internamente en formato BGR (no RGB),")
            print("independientemente del formato en el que esté guardada en disco.")

    # Si no se pudo cargar la imagen (archivo corrupto, formato no soportado, etc.)
    if img is None:
        print(f"Error: no se pudo leer la imagen '{ruta}'. Puede estar corrupta o en un formato no soportado.")
        return

    print("\n--- Reporte de la imagen ---")

    # 1. Dimensiones en píxeles (shape completo)
    if img.ndim == 3:
        alto, ancho, canales = img.shape
    else:
        # Algunas imágenes en escala de grises tienen shape (alto, ancho), sin canales
        alto, ancho = img.shape
        canales = 1

    print(f"Dimensiones (alto x ancho x canales): {alto} x {ancho} x {canales}")

    # 2. Cantidad de canales y dtype (profundidad de bits)
    bytes_por_canal = img.itemsize  # cantidad de bytes que ocupa cada valor (ej. uint8 -> 1 byte)
    bits_por_canal = bytes_por_canal * 8
    print(f"Cantidad de canales: {canales}")
    print(f"Tipo de dato (dtype): {img.dtype} -> {bits_por_canal} bits por canal")

    # 3. Tamaño en memoria vs tamaño en disco
    tamano_memoria = img.nbytes
    tamano_disco = os.path.getsize(ruta)

    print(f"\nTamaño en memoria (array descomprimido): {tamano_memoria} bytes")
    print(f"Tamaño en disco (archivo): {tamano_disco} bytes")

    print(
        "Explicación: el tamaño en memoria es el array 'crudo' sin comprimir "
        f"(alto x ancho x canales x bytes_por_canal = {alto} x {ancho} x {canales} x {bytes_por_canal} = {tamano_memoria} bytes). "
        "El tamaño en disco suele ser distinto porque los formatos de imagen aplican compresión: "
        "JPEG usa compresión CON pérdida (descarta información para pesar menos), mientras que PNG usa "
        "compresión SIN pérdida (más pesado que JPEG pero reconstruye la imagen exacta). "
        "Por eso el archivo en disco casi siempre pesa menos que el array descomprimido en memoria."
    )

    print("--- Fin del reporte ---\n")


if __name__ == "__main__":
    main()
