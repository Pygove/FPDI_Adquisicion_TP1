#!/usr/bin/env python3
"""
comparar_bandas.py

Script educativo para comparar bandas individuales de Sentinel-2
(archivos TIFF descargados del Copernicus Data Space Browser, ej.
"algo_B01.tif", "algo_B02.tif", etc.).

Busca automáticamente los archivos .tif/.tiff dentro de la carpeta
"img_cargadas_copernicus" (ubicada junto a este script) y los compara.

Uso:
    python comparar_bandas.py
"""

import glob
import os
import re
import sys

import numpy as np
import rasterio

# Carpeta donde se buscan las bandas, relativa a la ubicación de este script.
CARPETA_IMAGENES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_cargadas_copernicus")

# ---------------------------------------------------------------------------
# 1) Información estándar de las bandas de Sentinel-2.
#    Cada entrada: (longitud de onda central en nm, resolución nativa en m, descripción)
# ---------------------------------------------------------------------------
INFO_BANDAS = {
    "B01": (443, 60, "aerosol"),
    "B02": (490, 10, "azul"),
    "B03": (560, 10, "verde"),
    "B04": (665, 10, "rojo"),
    "B05": (705, 20, "red edge"),
    "B06": (740, 20, "red edge"),
    "B07": (783, 20, "red edge"),
    "B08": (842, 10, "NIR"),
    "B8A": (865, 20, "NIR estrecho"),
    "B09": (945, 60, "vapor de agua"),
    "B10": (1375, 60, "cirrus"),
    "B11": (1610, 20, "SWIR"),
    "B12": (2190, 20, "SWIR"),
}

# Expresión regular para detectar el código de banda en el nombre del archivo.
# Busca B seguido de dos dígitos, y opcionalmente una letra (para B8A).
PATRON_BANDA = re.compile(r"B(\d{2}[A]?)", re.IGNORECASE)


def identificar_banda(nombre_archivo):
    """
    Busca el código de banda (B01, B02, ..., B8A, ..., B12) en el nombre
    del archivo usando una expresión regular. Devuelve el código en
    mayúsculas si lo encuentra y es una banda conocida, o None si no.
    """
    coincidencia = PATRON_BANDA.search(nombre_archivo)
    if coincidencia is None:
        return None

    codigo = "B" + coincidencia.group(1).upper()
    if codigo in INFO_BANDAS:
        return codigo
    return None


def analizar_archivo(ruta):
    """
    Abre un archivo TIFF con rasterio y devuelve un diccionario con toda
    la información relevante: resolución real, dimensiones, dtype y
    estadísticas de los valores de píxel.
    """
    with rasterio.open(ruta) as dataset:
        # La resolución real se obtiene del transform afín: los
        # coeficientes 'a' y 'e' representan el tamaño de píxel en X e Y.
        transform = dataset.transform
        resolucion_x = abs(transform.a)
        resolucion_y = abs(transform.e)

        datos = dataset.read(1)  # Leemos la primera (única) banda del archivo.

        return {
            "ancho": dataset.width,
            "alto": dataset.height,
            "dtype": dataset.dtypes[0],
            "resolucion_x": resolucion_x,
            "resolucion_y": resolucion_y,
            "minimo": datos.min(),
            "maximo": datos.max(),
            "media": datos.mean(),
            "desvio": datos.std(),
            "datos": datos,  # se guarda para el gráfico opcional
        }


def imprimir_tabla(resultados):
    """
    Imprime una tabla comparativa prolija con toda la información
    recolectada para cada banda.
    """
    encabezado = (
        f"{'Banda':<6}{'λ (nm)':<9}{'Res. esperada':<15}{'Res. real (x,y)':<18}"
        f"{'Dimensiones':<15}{'Dtype':<10}{'Min':<10}{'Max':<10}{'Media':<10}{'Desvío':<10}"
    )
    print(encabezado)
    print("-" * len(encabezado))

    for codigo, r in resultados.items():
        longitud_onda, res_esperada, _descripcion = INFO_BANDAS[codigo]
        res_real = f"{r['resolucion_x']:.1f}x{r['resolucion_y']:.1f}"
        dimensiones = f"{r['ancho']}x{r['alto']}"
        print(
            f"{codigo:<6}{longitud_onda:<9}{res_esperada:<15}{res_real:<18}"
            f"{dimensiones:<15}{r['dtype']:<10}"
            f"{r['minimo']:<10.1f}{r['maximo']:<10.1f}{r['media']:<10.1f}{r['desvio']:<10.1f}"
        )

    # 4) Nota aclaratoria sobre las distintas dimensiones en píxeles.
    print(
        "\nNota: aunque todas las bandas cubren la misma zona geográfica, "
        "tienen distinta cantidad de píxeles porque Sentinel-2 tiene una "
        "resolución nativa distinta según la banda (10m, 20m o 60m por "
        "píxel). Esto NO es un error: es una característica del sensor. "
        "Las bandas de 10m (B02, B03, B04, B08) tienen más detalle "
        "espacial que las de 20m o 60m, que cubren más terreno con cada "
        "píxel."
    )


def graficar_bandas(resultados):
    """
    Muestra todas las bandas en una grilla en escala de grises, cada una
    normalizada individualmente (ya que sus rangos de valores crudos son
    muy distintos entre sí). Esto permite comparar visualmente, por
    ejemplo, cómo la vegetación se ve mucho más brillante en la banda
    NIR (B08) que en las bandas visibles.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no está disponible: se omite la visualización)")
        return

    n = len(resultados)
    columnas = min(4, n)
    filas = (n + columnas - 1) // columnas

    fig, ejes = plt.subplots(filas, columnas, figsize=(4 * columnas, 4 * filas))
    ejes = np.atleast_1d(ejes).flatten()

    for eje, (codigo, r) in zip(ejes, resultados.items()):
        longitud_onda, _res, _descripcion = INFO_BANDAS[codigo]
        datos = r["datos"].astype(float)

        # Normalización individual (min-max) para poder visualizar cada
        # banda pese a que sus rangos de valores crudos varían mucho.
        minimo, maximo = datos.min(), datos.max()
        if maximo > minimo:
            datos_normalizados = (datos - minimo) / (maximo - minimo)
        else:
            datos_normalizados = datos  # banda constante, evitar división por cero

        eje.imshow(datos_normalizados, cmap="gray")
        eje.set_title(f"{codigo} ({longitud_onda} nm)")
        eje.axis("off")

    # Ocultar subplots sobrantes si la grilla no se llena por completo.
    for eje in ejes[len(resultados):]:
        eje.axis("off")

    plt.tight_layout()
    plt.show()


def buscar_archivos_tiff(carpeta):
    """
    Busca todos los archivos .tif/.tiff dentro de la carpeta indicada.
    """
    patrones = [os.path.join(carpeta, "*.tif"), os.path.join(carpeta, "*.tiff")]
    archivos = []
    for patron in patrones:
        archivos.extend(glob.glob(patron))
    return sorted(archivos)


def main():
    if not os.path.isdir(CARPETA_IMAGENES):
        print(f"Error: no se encontró la carpeta '{CARPETA_IMAGENES}'.", file=sys.stderr)
        sys.exit(1)

    archivos = buscar_archivos_tiff(CARPETA_IMAGENES)
    if not archivos:
        print(f"Error: no se encontraron archivos .tif/.tiff en '{CARPETA_IMAGENES}'.", file=sys.stderr)
        sys.exit(1)

    resultados = {}

    for ruta in archivos:
        codigo = identificar_banda(ruta)

        # 2) Si no se puede identificar la banda, informar y seguir con el resto.
        if codigo is None:
            print(f"Aviso: no se pudo identificar la banda en el archivo '{ruta}', se omite.", file=sys.stderr)
            continue

        try:
            resultados[codigo] = analizar_archivo(ruta)
        except rasterio.errors.RasterioIOError as error:
            print(f"Aviso: no se pudo abrir '{ruta}' ({error}), se omite.", file=sys.stderr)

    if not resultados:
        print("No se pudo procesar ninguna banda.", file=sys.stderr)
        sys.exit(1)

    # Ordenamos por código de banda para que la tabla sea más legible.
    resultados = dict(sorted(resultados.items()))

    imprimir_tabla(resultados)
    graficar_bandas(resultados)


if __name__ == "__main__":
    main()
