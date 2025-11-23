# Geocodificación Inversa Catastral (Rutas Ambientales)

**Autor:** Daniel Arango Irreño
**Versión:** 1.0.0
**Categoría:** Processing / Vector

---

## 🌎 Descripción General

Esta herramienta es un algoritmo de procesamiento diseñado para automatizar la **Geocodificación Inversa Masiva** de capas de puntos, con un enfoque en la estandarización de la nomenclatura vial para aplicaciones de ingeniería ambiental y gestión catastral.

El plugin se encuentra en la **Caja de Herramientas de Procesos**, bajo el grupo **Rutas Ambientales**.

## ⚙️ Funcionalidad y Características Clave

1.  **Entrada de Datos:** Requiere una única capa de puntos de entrada.
2.  **Reproyección Automática:** La herramienta detecta automáticamente el Sistema de Coordenadas de Referencia (CRS) de la capa de entrada (ej., Magna Sirgas, UTM) y realiza la transformación interna a **WGS 84 (EPSG:4326)** para cumplir con los requisitos de la API de geocodificación.
3.  **Consulta Externa (Nominatim):** Utiliza el servicio de **Nominatim (OpenStreetMap)** para obtener la dirección postal correspondiente a cada coordenada.
4.  **Estandarización de Nomenclatura:** La dirección obtenida se procesa y se estandariza automáticamente utilizando abreviaturas comunes (ej., **'Calle'** $\rightarrow$ **'CL'**, **'Carrera'** $\rightarrow$ **'KR'**, **'Diagonal'** $\rightarrow$ **'DG'**).
5.  **Respaldo Inteligente (Fallback):** Si no se encuentra una nomenclatura vial específica (ej., en parques, lotes grandes), el plugin utiliza la descripción de lugar más cercana (`display_name`) en lugar de devolver un error o un valor vacío.
6.  **Salida:** Genera una nueva capa de puntos que incluye todos los atributos originales más el nuevo campo **`direccion_osm`** con la dirección estandarizada.

## ⚠️ Limitaciones y Tasa de Uso

Este plugin utiliza el servicio público y gratuito de Nominatim (OpenStreetMap). Por respeto a sus políticas de uso, el algoritmo incluye una pausa obligatoria de **1.1 segundos** entre cada consulta.

* **Tasa de Procesamiento:** Aproximadamente 55-60 puntos por minuto.
* **Advertencia:** Intentar modificar o eliminar el retardo (`time.sleep(1.1)`) podría resultar en el bloqueo temporal de tu dirección IP por parte de los servidores de Nominatim.

## 📄 Instalación

1.  Descargue el archivo ZIP del repositorio.
2.  En QGIS, vaya a **Complementos** $\rightarrow$ **Administrar e instalar complementos...**
3.  Seleccione **Instalar a partir de ZIP** y cargue el archivo.
4.  La herramienta aparecerá en la **Caja de Herramientas de Procesos** bajo el grupo **Rutas Ambientales**.

---