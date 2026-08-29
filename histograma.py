"""
Script educativo para calcular y graficar el histograma de intensidades
de una imagen.

Idea general:
- El histograma muestra cuántos píxeles hay para cada nivel de intensidad
  (de 0 a 255). Nos permite ver de un vistazo cómo está distribuida la
  luminosidad/color de la imagen.
- Relación con el rango dinámico: si el histograma está concentrado en un
  rango chico de valores (por ejemplo, todo entre 50 y 120), la imagen
  tiene bajo contraste. Si está "pegado" a alguno de los extremos (0 o
  255), indica sombras o luces saturadas (se perdió información de detalle
  en esas zonas, porque quedaron "recortadas" al mínimo o máximo posible).
  Una imagen con buen rango dinámico suele tener el histograma más
  distribuido a lo largo de todo el rango 0-255.

Uso:
    python3 histograma.py imagen.jpg
"""

import os
import sys

import cv2
import matplotlib.pyplot as plt


def calcular_histograma(canal_imagen):
    """
    Calcula el histograma de un solo canal (imagen en escala de grises o
    un canal de color) usando cv2.calcHist.

    Parámetros de cv2.calcHist usados:
    - [canal_imagen]: la imagen (o canal) sobre la que se calcula.
    - [0]: se analiza el canal 0 (el único que tiene, ya que le pasamos
      un solo canal a la vez).
    - None: no usamos máscara, se analiza toda la imagen.
    - [256]: cantidad de "bins" (un bin por cada nivel de intensidad 0-255).
    - [0, 256]: rango de valores posibles de intensidad.
    """
    return cv2.calcHist([canal_imagen], [0], None, [256], [0, 256])


def main():
    if len(sys.argv) != 2:
        print("Uso: python3 histograma.py imagen.jpg")
        sys.exit(1)

    ruta_imagen = sys.argv[1]
    imagen = cv2.imread(ruta_imagen)

    if imagen is None:
        print(f"No se pudo abrir '{ruta_imagen}'")
        sys.exit(1)

    # Convertimos a escala de grises para tener también ese histograma.
    imagen_gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    es_color = len(imagen.shape) == 3 and imagen.shape[2] == 3

    # Preparamos la figura: un subplot para el histograma de color (si
    # corresponde) y otro para el histograma en escala de grises.
    if es_color:
        figura, (eje_color, eje_gris) = plt.subplots(1, 2, figsize=(12, 4))
    else:
        figura, eje_gris = plt.subplots(1, 1, figsize=(6, 4))

    if es_color:
        # OJO: OpenCV carga las imágenes en orden BGR (Blue, Green, Red),
        # no en RGB como suele asumirse. Por eso etiquetamos y coloreamos
        # las curvas respetando ese orden, para no confundir los canales.
        canales_bgr = cv2.split(imagen)
        nombres_canales = ("Azul (B)", "Verde (G)", "Rojo (R)")
        colores_curvas = ("b", "g", "r")

        for canal, nombre, color in zip(canales_bgr, nombres_canales, colores_curvas):
            hist_canal = calcular_histograma(canal)
            eje_color.plot(hist_canal, color=color, label=nombre)

        eje_color.set_title("Histograma por canal de color (BGR)")
        eje_color.set_xlabel("Intensidad (0-255)")
        eje_color.set_ylabel("Cantidad de píxeles")
        eje_color.set_xlim([0, 256])
        eje_color.legend()

    # Histograma en escala de grises.
    hist_gris = calcular_histograma(imagen_gris)
    eje_gris.plot(hist_gris, color="black")
    eje_gris.set_title("Histograma en escala de grises")
    eje_gris.set_xlabel("Intensidad (0-255)")
    eje_gris.set_ylabel("Cantidad de píxeles")
    eje_gris.set_xlim([0, 256])

    plt.tight_layout()

    # Guardamos el gráfico como PNG, usando el nombre original de la imagen.
    nombre_base = os.path.splitext(os.path.basename(ruta_imagen))[0]
    nombre_salida = f"histograma_{nombre_base}.png"
    plt.savefig(nombre_salida)
    print(f"Gráfico guardado en '{nombre_salida}'")

    plt.show()


if __name__ == "__main__":
    main()
