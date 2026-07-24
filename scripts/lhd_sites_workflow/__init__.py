# Module pour les scripts/traitements Lidar-HD sites
# Enregistrement de l'algorithme dans QGIS

from qgis.core import QgsApplication
from .lhd_sites_audit_v1_0_0 import LHD_sites_Audit_Split_Weights_Script_V1_0_0

def classFactory(iface):
    """
    Fonction requise par QGIS pour créer une instance de l'algorithme.
    """
    return LHD_sites_Audit_Split_Weights_Script_V1_0_0()
