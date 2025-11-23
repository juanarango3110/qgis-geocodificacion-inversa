from qgis.core import QgsApplication
from .geocodificacion_inversa_alg import GeocodificacionProvider

class GeocodificacionPlugin:
    def __init__(self, iface):
        self.provider = None

    def initGui(self):
        # Aquí es donde QGIS busca el método initGui
        self.provider = GeocodificacionProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        # Limpieza al cerrar
        if self.provider:
            QgsApplication.processingRegistry().removeProvider(self.provider)

def classFactory(iface):
    return GeocodificacionPlugin(iface)