"""
explorar_geotiff.py

Script educativo para explorar un archivo TIFF georreferenciado
(por ejemplo, imágenes Sentinel-2 exportadas desde el Copernicus
Data Space Browser).

Uso:
    python explorar_geotiff.py ruta/al/archivo.tif

Objetivo: mostrar la diferencia entre leer una imagen con una
librería que entiende georreferenciación (rasterio) y una que
solo ve píxeles crudos (OpenCV / cv2).
"""

import sys
import os


def explorar_con_rasterio(ruta):
    """Abre el archivo con rasterio y reporta toda la info georreferenciada."""
    try:
        import rasterio
    except ImportError:
        print("=" * 60)
        print("ERROR: no está instalada la librería 'rasterio'.")
        print("Instalarla con: pip install rasterio")
        print("rasterio depende de GDAL, que debe estar disponible")
        print("en el sistema (en Windows/Mac suele venir incluido")
        print("con el propio paquete; en Linux a veces hay que")
        print("instalar además 'libgdal-dev' o usar conda).")
        print("=" * 60)
        return

    print("=" * 60)
    print("RASTERIO: lectura con georreferenciación")
    print("=" * 60)

    with rasterio.open(ruta) as dataset:
        # --- CRS (sistema de coordenadas) ---
        crs = dataset.crs
        if crs is None:
            print("El archivo NO tiene información de georreferenciación (CRS = None).")
            print("Esto pasa, por ejemplo, si se descargó como 'JPG (no georeference)'")
            print("en vez de GeoTIFF: la imagen se puede ver, pero no se sabe dónde")
            print("está ubicada en el mundo. Para georreferenciar hace falta el TIFF.")
        else:
            print(f"CRS (sistema de coordenadas): {crs}")

        # --- Dimensiones y bandas ---
        print(f"Ancho x Alto (píxeles): {dataset.width} x {dataset.height}")
        print(f"Cantidad de bandas: {dataset.count}")

        # --- dtype ---
        print(f"Tipo de dato (dtype) de las bandas: {dataset.dtypes}")
        print("Nota: en Sentinel-2 las bandas 'raw' (crudas, reflectancia)")
        print("suelen venir en 16 bits (uint16). Una composición 'true color'")
        print("(RGB) pensada solo para visualizar suele exportarse ya")
        print("reescalada a 8 bits (uint8).")

        # --- Transform y bounding box ---
        transform = dataset.transform
        print(f"Transformación afín (transform): {transform}")

        if crs is not None:
            # Esquina superior-izquierda e inferior-derecha en coords del CRS del dataset
            left, top = transform * (0, 0)
            right, bottom = transform * (dataset.width, dataset.height)
            print(f"Bounding box en coordenadas del CRS del dataset:")
            print(f"  Superior-izquierda: ({left}, {top})")
            print(f"  Inferior-derecha:  ({right}, {bottom})")

            # Si el CRS no es geográfico (ej. UTM), convertir a lat/long (EPSG:4326)
            if not crs.is_geographic:
                from rasterio.warp import transform as warp_transform
                xs, ys = warp_transform(crs, "EPSG:4326", [left, right], [top, bottom])
                print(f"Bounding box en lat/long (EPSG:4326):")
                print(f"  Superior-izquierda: (lat={ys[0]}, lon={xs[0]})")
                print(f"  Inferior-derecha:  (lat={ys[1]}, lon={xs[1]})")

            # --- Resolución espacial ---
            res_x, res_y = dataset.res
            unidad = "grados" if crs.is_geographic else "metros (u otra unidad lineal del CRS)"
            print(f"Resolución espacial por píxel: {res_x} x {res_y} ({unidad})")


def explorar_con_opencv(ruta):
    """Abre el mismo archivo con cv2 para comparar."""
    print()
    print("=" * 60)
    print("OPENCV (cv2): lectura SIN georreferenciación")
    print("=" * 60)

    try:
        import cv2
    except ImportError:
        print("ERROR: no está instalada la librería 'opencv-python'.")
        print("Instalarla con: pip install opencv-python")
        return

    img = cv2.imread(ruta, cv2.IMREAD_UNCHANGED)
    if img is None:
        print("cv2.imread no pudo leer el archivo (devolvió None).")
        return

    print(f"Shape (alto, ancho, canales): {img.shape}")
    print(f"dtype: {img.dtype}")
    print()
    print("IMPORTANTE: OpenCV ignora por completo la georreferenciación.")
    print("cv2.imread solo devuelve el array de píxeles crudo: no sabe qué")
    print("CRS tiene la imagen, ni su transform, ni su bounding box en el")
    print("mundo real. Sirve para visualizar o procesar píxeles, pero NO")
    print("para saber dónde está ubicada la imagen geográficamente.")
    print()
    print("Esto contrasta con las fotos de cámara comunes, donde la")
    print("ubicación (si el dispositivo tiene GPS) se guarda como metadato")
    print("EXIF (tags GPSLatitude/GPSLongitude) dentro del propio JPG.")
    print("Esos tags se leen con librerías como 'exifread', no con rasterio")
    print("(que está pensado para georreferenciación raster tipo GIS, con")
    print("CRS y transformaciones afines, no para tags EXIF de cámaras).")


def main():
    if len(sys.argv) != 2:
        print("Uso: python explorar_geotiff.py ruta/al/archivo.tif")
        sys.exit(1)

    ruta = sys.argv[1]

    if not os.path.isfile(ruta):
        print(f"ERROR: no se encontró el archivo '{ruta}'.")
        sys.exit(1)

    explorar_con_rasterio(ruta)
    explorar_con_opencv(ruta)


if __name__ == "__main__":
    main()
