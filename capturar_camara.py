"""
capturar_camara.py

Script simple para capturar imágenes desde la webcam usando OpenCV.

Controles:
    ESPACIO -> captura el frame actual y lo guarda como PNG
    q       -> cierra el programa sin guardar nada
"""

import cv2
import os
from datetime import datetime

# Códigos de tecla (para que el código sea más legible)
TECLA_ESPACIO = 32
TECLA_Q = ord('q')

# Carpeta donde se guardan las capturas
CARPETA_CAPTURAS = "img_capturadas"


def main():
    # Abrimos la cámara por defecto (índice 0)
    camara = cv2.VideoCapture(0)

    # Si la cámara no pudo abrirse, avisamos y salimos sin crashear
    if not camara.isOpened():
        print("Error: no se pudo acceder a la cámara. Verificá que esté conectada y no esté en uso por otro programa.")
        return

    # Creamos la carpeta de capturas si todavía no existe
    os.makedirs(CARPETA_CAPTURAS, exist_ok=True)

    print("Cámara abierta correctamente.")
    print("Presioná ESPACIO para capturar una foto, o 'q' para salir.")

    while True:
        # Leemos un frame de la cámara
        ret, frame = camara.read()

        # Si no se pudo leer el frame, cortamos el bucle
        if not ret:
            print("Error: no se pudo leer el frame de la cámara.")
            break

        # Mostramos el frame en una ventana (preview en vivo)
        cv2.imshow("Preview de camara - ESPACIO: capturar | q: salir", frame)

        # Esperamos 1ms por una tecla (necesario para que se actualice la ventana)
        tecla = cv2.waitKey(1) & 0xFF

        if tecla == TECLA_ESPACIO:
            # Generamos el nombre del archivo con fecha y hora actual
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"captura_{timestamp}.png"
            ruta_archivo = os.path.join(CARPETA_CAPTURAS, nombre_archivo)

            # Guardamos el frame como PNG (formato sin pérdida)
            cv2.imwrite(ruta_archivo, frame)

            # Obtenemos ancho y alto del frame capturado
            alto, ancho = frame.shape[:2]

            print(f"Foto capturada -> Resolución: {ancho}x{alto} | Archivo guardado: {ruta_archivo}")

        elif tecla == TECLA_Q:
            print("Saliendo sin guardar.")
            break

    # Liberamos la cámara y cerramos las ventanas antes de terminar
    camara.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
