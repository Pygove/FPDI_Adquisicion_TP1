"""
Script educativo para detectar cámaras conectadas usando OpenCV.

Idea general:
- OpenCV no tiene una función que "liste" las cámaras disponibles.
- Por eso, la forma habitual de detectarlas es ir probando índices
  (0, 1, 2, ...) e intentar abrir un VideoCapture con cada uno.
- Si se pudo abrir (isOpened() == True), asumimos que hay una cámara
  (o dispositivo de video) en ese índice.
"""

import glob

import cv2

# Cantidad máxima de índices a probar (0 a 9, o sea 10 índices en total).
CANTIDAD_INDICES_A_PROBAR = 10


def detectar_camaras_opencv():
    """
    Prueba abrir cv2.VideoCapture(i) para i entre 0 y CANTIDAD_INDICES_A_PROBAR - 1.
    Devuelve la cantidad de cámaras detectadas.
    """
    camaras_detectadas = 0

    for indice in range(CANTIDAD_INDICES_A_PROBAR):
        # Intentamos abrir la cámara en este índice.
        captura = cv2.VideoCapture(indice)

        if captura.isOpened():
            # Si se abrió correctamente, leemos la resolución por defecto
            # que reporta la cámara (no forzamos ninguna resolución).
            ancho = captura.get(cv2.CAP_PROP_FRAME_WIDTH)
            alto = captura.get(cv2.CAP_PROP_FRAME_HEIGHT)

            print(f"Cámara encontrada en índice {indice} "
                  f"- Resolución por defecto: {int(ancho)}x{int(alto)}")

            camaras_detectadas += 1
        else:
            print(f"Índice {indice}: no se pudo abrir (no hay cámara o no está disponible)")

        # Muy importante: liberar el dispositivo antes de probar el siguiente
        # índice, para no dejarlo "ocupado" y que el próximo intento falle
        # por estar el recurso en uso.
        captura.release()

    return camaras_detectadas


def listar_dispositivos_video_linux():
    """
    Información extra (solo Linux): lista los dispositivos /dev/video*
    que existen en el sistema, para poder comparar contra lo que detectó OpenCV.

    Nota: que exista /dev/video0 no siempre significa que sea una cámara
    "usable" directamente (a veces son dispositivos de metadata, por ejemplo),
    por eso puede no coincidir exactamente con lo que reporta OpenCV.
    """
    dispositivos = sorted(glob.glob("/dev/video*"))

    print("\n--- Dispositivos /dev/video* encontrados en el sistema (Linux) ---")
    if dispositivos:
        for dispositivo in dispositivos:
            print(dispositivo)
    else:
        print("No se encontraron dispositivos /dev/video* en el sistema.")


if __name__ == "__main__":
    print("--- Buscando cámaras con OpenCV (probando índices 0 a "
          f"{CANTIDAD_INDICES_A_PROBAR - 1}) ---\n")

    total_camaras = detectar_camaras_opencv()

    print("\n--- Resumen ---")
    print(f"Total de cámaras detectadas por OpenCV: {total_camaras}")

    # Información extra para comparar, ya que estamos en Linux.
    listar_dispositivos_video_linux()
