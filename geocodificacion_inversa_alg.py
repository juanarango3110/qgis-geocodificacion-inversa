import time
import os
from qgis.core import (
    QgsProcessingAlgorithm, 
    QgsProcessingParameterFeatureSource, 
    QgsProcessingParameterFeatureSink,
    QgsProcessingFeedback, 
    QgsVectorLayer, 
    QgsField, 
    QgsFeature, 
    QgsProcessing, 
    QgsFeatureSink, 
    QgsProcessingProvider,
    QgsCoordinateReferenceSystem, # <<-- NUEVO: Para manejar sistemas de coordenadas
    QgsCoordinateTransform,       # <<-- NUEVO: Para transformar a WGS84
    QgsProject
)
from qgis.PyQt.QtCore import QVariant, QCoreApplication
from qgis.PyQt.QtGui import QIcon

OUTPUT = 'OUTPUT' 

class GeocodificacionInversaAlg(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    # Eliminamos FIELD_X y FIELD_Y porque ya no los necesitamos
    
    ABREVIATURAS = {
        'Calle': 'CL', 'Carrera': 'KR', 'Avenida': 'AV', 'Autopista': 'AUTOP', 
        'Transversal': 'TV', 'Diagonal': 'DG', 'Circular': 'CIR', 'Camino': 'CM', 
        'Vía': 'VIA', 'Manzana': 'MZTA', 'Bloque': 'BL', 'Edificio': 'ED', 
        'Sector': 'SEC', 'Zona': 'ZN'
    }

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def name(self):
        return 'geocodificacion_inversa'

    def displayName(self):
        return self.tr('Geocodificación Inversa con Nomenclatura')

    def group(self):
        return self.tr('Rutas Ambientales')

    def groupId(self):
        return 'rutasambientales'

    def shortHelpString(self):
        return self.tr("""
            <h3>Geocodificación Inversa Automática</h3>
            <p><b>Autor:</b> Daniel Arango Irreño</p>
            <p>Obtiene direcciones estandarizadas consultando Nominatim (OSM).</p>
            
            <h4>Novedades:</h4>
            <ul>
                <li><b>Automático:</b> Detecta el sistema de coordenadas de la capa y lo convierte a GPS (WGS84) internamente.</li>
                <li><b>Inteligente:</b> Si no hay nomenclatura exacta, busca la dirección referencial más cercana.</li>
            </ul>
        """)

    def icon(self):
        plugin_dir = os.path.dirname(__file__)
        return QIcon(os.path.join(plugin_dir, 'icon.png'))

    def createInstance(self):
        return GeocodificacionInversaAlg()

    def initAlgorithm(self, config=None):
        # Solo pedimos la capa de entrada, nada más
        self.addParameter(QgsProcessingParameterFeatureSource(self.INPUT_LAYER, self.tr('Capa de Puntos (Cualquier Sistema de Coordenadas)'), [QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterFeatureSink(OUTPUT, self.tr('Capa con Direcciones OSM')))

    def processAlgorithm(self, parameters, context, feedback: QgsProcessingFeedback):
        try:
            import requests
        except ImportError:
            feedback.reportError("Falta la librería 'requests'. Instálala en OSGeo4W Shell: pip install requests")
            return {}

        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        
        # --- LÓGICA DE TRANSFORMACIÓN DE COORDENADAS ---
        source_crs = source.sourceCrs()
        target_crs = QgsCoordinateReferenceSystem("EPSG:4326") # WGS84 (Lat/Lon)
        
        # Creamos el transformador (De la capa -> a WGS84)
        transform = QgsCoordinateTransform(source_crs, target_crs, context.project())
        
        fields = source.fields()
        # 1. CAMBIO DE NOMBRE DEL CAMPO
        fields.append(QgsField('direccion_osm', QVariant.String, 'String', 255))
        
        sink, dest_id = self.parameterAsSink(parameters, OUTPUT, context, fields, source.wkbType(), source.sourceCrs())
        
        total = source.featureCount()
        features = source.getFeatures()
        
        feedback.pushInfo(f"Iniciando geocodificación inteligente de {total} puntos...")

        for i, feat in enumerate(features):
            if feedback.isCanceled(): break
            
            try:
                # 2. OBTENCIÓN AUTOMÁTICA DE GEOMETRÍA
                geom = feat.geometry()
                
                # Reproyectamos el punto a WGS84 para tener Lat/Lon reales
                geom.transform(transform)
                point = geom.asPoint()
                
                lon = point.x()
                lat = point.y()

                url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
                
                resp = requests.get(url, headers={'User-Agent': 'QGIS_Plugin_DanielArango'})
                data = resp.json() if resp.status_code == 200 else {}
                
                # Lógica de Nomenclatura
                addr = data.get('address', {})
                calle = addr.get('road', '')
                
                # Si no hay calle, buscar barrio o suburbio
                if not calle: 
                    calle = addr.get('neighbourhood', '') or addr.get('suburb', '')

                # Estandarización (Tus abreviaturas)
                for k, v in self.ABREVIATURAS.items():
                    if calle and calle.startswith(k):
                        calle = calle.replace(k, v)
                        break
                
                num = addr.get('house_number', '')
                
                # Construcción de la dirección
                if calle and num:
                    direc = f"{calle} # {num}"
                elif calle:
                    direc = calle
                else:
                    # 3. DIRECCIÓN MÁS CERCANA (FALLBACK)
                    # Si falló todo lo anterior, tomamos el 'display_name' completo que devuelve OSM
                    direc = data.get('display_name', 'Sin datos en OSM')

            except Exception as e:
                direc = f"Error: {str(e)}"

            new_feat = QgsFeature(fields)
            # Usamos la geometría ORIGINAL (sin transformar) para guardarla en la capa de salida
            # (porque la capa de salida conserva el sistema de coordenadas original)
            new_feat.setGeometry(feat.geometry()) 
            
            for idx, name in enumerate(source.fields().names()):
                new_feat[name] = feat[name]
            
            new_feat['direccion_osm'] = direc
            
            sink.addFeature(new_feat, QgsFeatureSink.FastInsert)
            feedback.setProgress(int((i/total)*100))
            time.sleep(1.1) 

        return {OUTPUT: dest_id}

class GeocodificacionProvider(QgsProcessingProvider):
    def loadAlgorithms(self):
        self.addAlgorithm(GeocodificacionInversaAlg())

    def id(self):
        return 'rutasambientalesprovider'

    def name(self):
        return 'Rutas Ambientales'

    def icon(self):
        plugin_dir = os.path.dirname(__file__)
        return QIcon(os.path.join(plugin_dir, 'icon.png'))