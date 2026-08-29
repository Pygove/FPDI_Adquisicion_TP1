"""
Script educativo para comparar la nitidez (enfoque) de distintas imágenes,
usando la varianza del Laplaciano.

Idea general:
- El operador Laplaciano es un filtro que resalta cambios abruptos de
  intensidad en la imagen (bordes), ya que aproxima la segunda derivada
  de la imagen.
- En una imagen bien enfocada, los bordes son nítidos (transiciones
  bruscas de intensidad), por lo que el Laplaciano toma valores altos
  (positivos y negativos) en esas zonas. Eso genera una varianza alta en
  el resultado.
- En una imagen desenfocada, los bordes están "suavizados" (transiciones
  graduales de intensidad), por lo que el Laplaciano toma valores cercanos
  a cero en casi toda la imagen, y por lo tanto la varianza es baja.
- Por eso, la varianza del Laplaciano es una métrica simple y bastante
  usada como indicador de nitidez: a mayor varianza, imagen más nítida.

Uso:
    python3 comparar_enfoque.py foto1.jpg foto2.jpg foto3.jpg ...
"""

import sys

import cv2


def calcular_nitidez(ruta_imagen):
    """
    Calcula la métrica de nitidez de una imagen usando la varianza del
    Laplaciano. Devuelve el valor de nitidez (float), o None si la imagen
    no se pudo cargar.
    """
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        print(f"No se pudo abrir '{ruta_imagen}'")
        return None

    # Convertimos a escala de grises: la nitidez se evalúa sobre la
    # intensidad, no hace falta trabajar con los 3 canales de color.
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Aplicamos el Laplaciano y calculamos la varianza del resultado.
    # Usamos CV_64F (float de 64 bits) para no perder los valores negativos
    # que aparecen en los bordes (con un tipo entero sin signo se recortarían).
    laplaciano = cv2.Laplacian(imagen_gris, cv2.CV_64F)
    nitidez = laplaciano.var()

    return nitidez


def main():
    if len(sys.argv) < 3:
        print("Uso: python3 comparar_enfoque.py imagen1 imagen2 [imagen3 ...]")
        print("(se necesitan al menos dos imágenes para comparar)")
        sys.exit(1)

    rutas_imagenes = sys.argv[1:]

    # Guardamos pares (ruta, nitidez), donde nitidez puede ser None si la
    # imagen no se pudo cargar.
    resultados = []
    for ruta in rutas_imagenes:
        nitidez = calcular_nitidez(ruta)
        resultados.append((ruta, nitidez))

    # Ordenamos de más nítida a más desenfocada. Las imágenes que no se
    # pudieron cargar (None) van al final.
    resultados_ordenados = sorted(
        resultados, key=lambda item: (item[1] is None, -(item[1] or 0))
    )

    # --- Tabla simple por consola ---
    print("\n--- Nitidez por imagen (de más nítida a más desenfocada) ---")
    print(f"{'Archivo':<40} | Nitidez (var. Laplaciano)")
    print("-" * 70)
    for ruta, nitidez in resultados_ordenados:
        texto_nitidez = f"{nitidez:.2f}" if nitidez is not None else "no se pudo calcular"
        print(f"{ruta:<40} | {texto_nitidez}")

    # --- Ayuda visual opcional con matplotlib ---
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib no está disponible: se omite la comparación visual)")
        return

    # Filtramos las que sí se pudieron cargar, para mostrarlas.
    resultados_validos = [(r, n) for r, n in resultados_ordenados if n is not None]

    if not resultados_validos:
        return

    cantidad_imagenes = len(resultados_validos)
    figura, ejes = plt.subplots(1, cantidad_imagenes, figsize=(4 * cantidad_imagenes, 4))

    # Si hay una sola imagen, matplotlib no devuelve una lista de ejes,
    # así que la convertimos en lista para poder iterar igual.
    if cantidad_imagenes == 1:
        ejes = [ejes]

    for eje, (ruta, nitidez) in zip(ejes, resultados_validos):
        imagen = cv2.imread(ruta)
        # OpenCV carga en BGR, pero matplotlib espera RGB. Convertimos
        # antes de mostrar para que los colores se vean correctos.
        imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)

        eje.imshow(imagen_rgb)
        eje.set_title(f"Nitidez: {nitidez:.1f}")
        eje.axis("off")  # Ocultamos los ejes, no aportan info útil acá.

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
