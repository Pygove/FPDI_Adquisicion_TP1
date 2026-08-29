# TP — Procesamiento Digital de Imágenes - Adquisición

Trabajo práctico sobre adquisición y análisis de imágenes digitales: captura desde
cámara, lectura de metadatos (EXIF y GeoTIFF), comparación de ISO/enfoque,
histogramas, e imágenes satelitales multiespectrales (Sentinel-2).

## Entorno

- Python 3.12, Linux
- Entorno virtual (`venv`) — no se versiona, ver `.gitignore`
- Dependencias en `requirements.txt`

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Nota (Ubuntu/Debian):** si al crear el `venv` la carpeta `venv/bin` no
> incluye `activate` ni `pip`, falta el paquete del sistema que completa el
> módulo `venv`: `sudo apt install python3.12-venv`, y volver a crear el
> entorno.

---

## 1. Teoría de base

### Tamaño de sensor y factor de recorte (crop factor)
El tamaño físico del sensor (en mm) determina cuánto de la imagen proyectada
por el lente se capta. El factor de recorte compara la diagonal de un sensor
contra la diagonal de referencia full frame (36×24mm):

```
factor de recorte = diagonal_full_frame / diagonal_sensor
```

Sensores más chicos (APS-C, Micro 4/3, 1", el de un celular) "recortan" el
campo de visión, equivalente a multiplicar la distancia focal real por ese
factor.

### Megapíxeles vs. calidad de imagen
Los megapíxeles son la cantidad de fotositos del sensor, no una medida de
calidad. Lo que realmente determina calidad es el **tamaño físico del
píxel** (pixel pitch = tamaño del sensor / cantidad de píxeles por lado):
píxeles más grandes captan más fotones → mejor relación señal/ruido (SNR) y
menos ruido visible, independientemente de cuántos megapíxeles tenga la
cámara.

### Rango dinámico
Capacidad de un sensor de captar luces y sombras en una misma escena,
medido en **stops** (escala logarítmica en base 2):

```
DR (stops) = log2(full well capacity / ruido de piso en electrones)
```

Una cámara moderna ronda ~14 stops. Este límite es el motivo por el que
existen técnicas de compresión de rango dinámico (tone mapping, gamma,
ecualización de histograma) al pasar de una escena real a una pantalla de
8 bits (~6-8 stops efectivos).

### Muestreo, cuantización y Nyquist
El sensor muestrea espacialmente la escena (una grilla de píxeles) y
cuantiza la intensidad de luz en niveles discretos (bits por canal). El
teorema de Nyquist determina cuánto detalle espacial se puede capturar sin
generar aliasing, en función de esa densidad de muestreo.

### Formatos de archivo: JPEG/PNG vs. RAW vs. GeoTIFF
- **JPEG/PNG**: imágenes ya procesadas, con o sin compresión con pérdida.
- **RAW** (`.NEF`, `.CR2`, `.ARW`, `.DNG`): datos crudos del sensor sin
  procesar, requieren una librería específica (`rawpy`) para decodificar,
  y devuelven los canales en **RGB** (al revés de OpenCV, que usa **BGR**).
- **GeoTIFF**: formato TIFF con metadata geoespacial embebida (sistema de
  coordenadas, transformación afín) usado en imágenes satelitales. No tiene
  relación con los tags EXIF de una foto de cámara — es un estándar
  completamente distinto, y requiere una librería geoespacial (`rasterio`)
  para leer su georreferenciación correctamente.

---

## 2. Scripts

### `capturar_camara.py`
Captura imágenes desde la webcam usando `cv2.VideoCapture`.
- ESPACIO: captura el frame actual y lo guarda en `img_capturadas/`.
- `q`: cierra sin guardar.

```bash
python capturar_camara.py
```

### `analizar_imagen.py`
Analiza una única imagen: dimensiones, canales, dtype, tamaño en memoria vs.
disco (y por qué difieren por compresión), y espacio de color (aclarando el
orden BGR de OpenCV). Soporta RAW vía `rawpy` según extensión.

```bash
python analizar_imagen.py ruta/a/imagen.jpg
```

### `analizar_carpeta.py`
Analiza en lote todas las imágenes de una carpeta: estándar (`.jpg`, `.png`,
`.bmp`, `.tiff`/`.tif`) y RAW (`.NEF`, `.CR2`, `.ARW`, `.DNG`). Además extrae
metadatos EXIF (ISO, apertura, velocidad, distancia focal, modelo, GPS) leyendo
el archivo directamente con `exifread` — válido tanto para estándar como para
RAW, ya que la metadata EXIF suele viajar embebida incluso cuando los
píxeles requieren `rawpy` para decodificarse. La geolocalización EXIF se
convierte de grados/minutos/segundos a decimal.

```bash
python analizar_carpeta.py img_capturadas
```

> Nota: la geolocalización EXIF (GPS de cámara) es un mecanismo distinto a
> la georreferenciación de un GeoTIFF satelital — ver `explorar_geotiff.py`.

### `detectar_camaras.py`
Prueba índices de `cv2.VideoCapture(0..9)` e informa cuáles abren
correctamente, junto con su resolución por defecto. En Linux, cruza el
resultado contra los dispositivos `/dev/video*` del sistema.

```bash
python detectar_camaras.py
```

### `comparar_iso.py`
Compara el ISO (EXIF) entre varias imágenes y las ordena de menor a mayor,
relacionándolo con el ruido esperado (a mayor ISO, más amplificación de
señal y más ruido visible). Muestra las imágenes en grilla con el ISO como
título.

```bash
python comparar_iso.py foto1.jpg foto2.jpg foto3.jpg
```

### `comparar_enfoque.py`
Mide nitidez con la varianza del Laplaciano (`cv2.Laplacian(...).var()`) —
bordes nítidos generan cambios abruptos de intensidad que el Laplaciano
resalta; una imagen desenfocada tiene varianza baja. Ordena de más nítida a
más desenfocada.

```bash
python comparar_enfoque.py foto1.jpg foto2.jpg foto3.jpg
```

### `histograma.py`
Calcula y grafica el histograma de una imagen: por canal de color (BGR) y
en escala de grises. Un histograma concentrado en un rango chico indica
bajo contraste o pérdida de rango dinámico (highlights o sombras
saturadas).

```bash
python histograma.py imagen.jpg
```

### `explorar_geotiff.py`
Lee metadata geoespacial de un GeoTIFF (ej. exportado del Copernicus Data
Space Browser) con `rasterio`: CRS, dimensiones, dtype, transformación
afín, bounding box geográfico y resolución espacial. Compara contra cargar
el mismo archivo con `cv2.imread`, que ignora toda la georreferenciación y
solo devuelve el array de píxeles.

```bash
python explorar_geotiff.py imagen_satelital.tiff
```

### `comparar_bandas.py`
Compara bandas individuales de Sentinel-2 (B01...B12, B8A) descargadas del
Copernicus Data Space Browser: longitud de onda central, resolución nativa
esperada vs. real, dimensiones, dtype y estadísticas de píxel (min, max,
media, desvío). Grafica todas las bandas en escala de grises para comparar
visualmente (ej. vegetación mucho más brillante en B08/NIR que en B04/rojo).

```bash
python comparar_bandas.py zona_B01.tif zona_B02.tif ... zona_B12.tif
```

---

## 3. Fuentes de imágenes utilizadas

- **[Copernicus Data Space Browser](https://browser.dataspace.copernicus.eu/)**
  — imágenes satelitales Sentinel-2 (L2A) de la zona de Oberá, Misiones,
  usadas para `explorar_geotiff.py` y `comparar_bandas.py`.
- **[Unsplash](https://unsplash.com/es)** — fotografías de referencia con
  metadata EXIF, usadas para `comparar_iso.py` y `comparar_enfoque.py`.

---

## 4. Notas de troubleshooting (aprendizajes durante el desarrollo)

- **Bandas de Sentinel-2 en cero**: si `comparar_bandas.py` reporta min/max/
  media en 0 para todas las bandas, verificar la fecha elegida en Copernicus.
  Con `dateMode=MOSAIC` y un rango de un solo día, si no hubo pasada del
  satélite ese día exacto, el raster exportado queda vacío pero con las
  dimensiones "correctas" (por eso el error no es obvio a simple vista).
  Solución: usar "Show latest date" o ampliar el rango a 15–30 días antes
  de descargar.
- **B10 ausente en L2A**: es esperado. La banda cirrus (B10) se descarta
  durante la corrección atmosférica; solo existe en el producto L1C.
- **Formato de descarga (8/16/32-bit) en capas Raw**: el selector de bit-depth
  del browser parece aplicarse solo a las capas visualizadas (True color,
  NDVI, etc.). Las capas Raw siempre vienen en su formato nativo `uint16`
  (reflectancia de superficie escalada x10000), independientemente de la
  opción elegida.
- **Tamaños de archivo idénticos entre bandas distintas**: señal fuerte de
  que el raster está vacío (todo ceros), no un problema de formato.
- **EXIF vs. GeoTIFF**: `exifread` no sirve para leer georreferenciación de
  imágenes satelitales (usan tags GeoTIFF, no EXIF). Para eso se usa
  `rasterio`.