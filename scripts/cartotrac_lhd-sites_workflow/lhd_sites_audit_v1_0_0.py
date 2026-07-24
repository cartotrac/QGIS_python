# =====================================================================
# Lidar-HD sites : Audit Structuré, Nuages, Rasters & Vecteurs CBN (V1.0.0)/
# =====================================================================
import os
import re
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterFolderDestination,
    QgsFeatureRequest,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextScope,
    QgsProject,
    QgsSpatialIndex,
    QgsExpressionContextUtils
)
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QHeaderView, QAbstractItemView
)
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QFont, QColor


class LHD_Advanced_Diagnostic_Dialog(QDialog):
    """
    Interface graphique d'audit Qt v1.0.0.
    Affiche l'état des nuages de points, des Rasters métier et des Vecteurs CBN,
    avec colorisation des colonnes, tri dynamique et gestion de largeur optimisée.
    """
    def __init__(self, sites_data, has_sources_analyzed=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lidar-HD sites : Tableau de Bord d'Analyse Multimodal (v1.0.0)")
        self.resize(1750, 750)
        self.setMinimumSize(1400, 500)
        
        layout = QVBoxLayout(self)
        
        info_txt = "<b>Suivi de production des fichiers LidarHD Sites :</b> Cliquez sur les en-têtes de colonnes pour trier le tableau.<br>"
        if has_sources_analyzed:
            info_txt += "Complément (colonne de droite) : États du répertoire <b>/_dl_data</b> du géocatalogue."
        else:
            info_txt += "<i>Le contrôle complémentaire du répertoire des dalles sources (_dl_data) est désactivé.</i>"
            
        info_label = QLabel(info_txt)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Porteur",
            "Nom de l'Emprise (Partie)", 
            "Sites LidarHD",        
            "Version Crop (C_)", 
            "Version Cut (C-cut_)", 
            "Rasters Métier (MNT|MNS|MNB)",
            "Vecteurs CBN (MNT|MNS|MNB)",
            "Poids (LAZ | COPC)",  
            "Poids Rasters",                
            "Poids CBN",
            "Diagnostic / Statut",  
            "Dalles Sources (_dl_data)" 
        ])
        
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        
        # --- 📐 CONFIGURATION RAFFINÉE DES COLONNES (v1.0.0) ---
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        # Ajustements au contenu pour les données courtes fixes
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Porteur
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Statut Base
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Crop
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Cut
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents) # Poids Points
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents) # Poids Rasters
        header.setSectionResizeMode(9, QHeaderView.ResizeMode.ResizeToContents) # Poids CBN

        # Distribution proportionnelle de l'espace pour les colonnes textuelles
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)          # Nom Emprise
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)          # Rasters Métier
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)          # Vecteurs CBN
        header.setSectionResizeMode(10, QHeaderView.ResizeMode.Stretch)         # Diagnostic
        
        if has_sources_analyzed:
            header.setSectionResizeMode(11, QHeaderView.ResizeMode.Stretch)     # Dalles Sources
        else:
            self.table.setColumnHidden(11, True)
            
        # Design général de la grille
        self.table.verticalHeader().setDefaultSectionSize(32) # Hauteur de ligne aérée
        
        # Désactivation temporaire pendant le chargement pour éviter les glitchs graphiques
        self.table.setUpdatesEnabled(False)
        self.table.setSortingEnabled(False)
        
        self.table.setRowCount(len(sites_data))
        for row, data in enumerate(sites_data):
            
            # --- 🎨 DÉFINITION DES COULEURS PASTEL ---
            color_pts = QColor(235, 245, 255)    # Bleu clair adouci
            color_raster = QColor(255, 248, 235) # Orange clair adouci
            color_vect = QColor(240, 248, 240)   # Vert clair adouci

            # 0. Porteur
            self.table.setItem(row, 0, QTableWidgetItem(data['porteur']))
            
            # 1. Nom de l'emprise
            self.table.setItem(row, 1, QTableWidgetItem(data['name_with_part']))
            
            # 2. Base de données
            item_base = QTableWidgetItem("✅" if data['lidarhd_val'] else "❌")
            item_base.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, item_base)
            
            # 3. Version Crop (Points)
            item_crop = QTableWidgetItem(f"LAZ: {data['crop_laz']} | COPC: {data['crop_copc']}")
            item_crop.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_crop.setBackground(color_pts)
            self.table.setItem(row, 3, item_crop)
            
            # 4. Version Cut (Points)
            item_cut = QTableWidgetItem(f"LAZ: {data['cut_laz']} | COPC: {data['cut_copc']}")
            item_cut.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_cut.setBackground(color_pts)
            self.table.setItem(row, 4, item_cut)
            
            # 5. Rasters
            item_rasters = QTableWidgetItem(data['rasters_txt'])
            item_rasters.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_rasters.setBackground(color_raster)
            self.table.setItem(row, 5, item_rasters)

            # 6. Vecteurs CBN
            item_cbn = QTableWidgetItem(data['cbn_txt'])
            item_cbn.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_cbn.setBackground(color_vect)
            self.table.setItem(row, 6, item_cbn)
            
            # 7. Poids Points
            item_poids = QTableWidgetItem(data['poids_str'])
            item_poids.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_poids.setBackground(color_pts)
            self.table.setItem(row, 7, item_poids)
            
            # 8. Poids Rasters
            item_poids_rast = QTableWidgetItem(data['poids_raster_str'])
            item_poids_rast.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_poids_rast.setBackground(color_raster)
            self.table.setItem(row, 8, item_poids_rast)

            # 9. Poids Vecteurs CBN
            item_poids_cbn = QTableWidgetItem(data['poids_cbn_str'])
            item_poids_cbn.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_poids_cbn.setBackground(color_vect)
            self.table.setItem(row, 9, item_poids_cbn)
            
            # 10. Diagnostic
            item_diag = QTableWidgetItem(f"{data['emoji']} {data['diag_msg']}")
            if data['emoji'] == "🔴":
                item_diag.setBackground(QColor(255, 230, 230))
            elif data['emoji'] == "🟠":
                item_diag.setBackground(QColor(255, 245, 215))
            elif data['emoji'] == "🟢":
                item_diag.setBackground(QColor(230, 250, 230))
            self.table.setItem(row, 10, item_diag)
            
            # 11. Dalles sources
            item_sources = QTableWidgetItem(data['dalles_sources_txt'])
            item_sources.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(row, 11, item_sources)
            
        # Réactivation propre après alimentation des items pour un rendu stable
        self.table.setSortingEnabled(True)
        self.table.setUpdatesEnabled(True)
        self.table.resizeRowsToContents() 
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        self.btn_close = QPushButton("Fermer l'analyse")
        self.btn_close.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_close.setStyleSheet("padding: 6px; min-width: 140px;")
        self.btn_close.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)


class LHD_sites_Audit_Split_Weights_Script_V1_0_0(QgsProcessingAlgorithm):
    """
    Algorithme LiDAR-HD v1.0.0.
    Audit croisé incluant le volume LAZ/COPC, les Rasters et les Vecteurs CBN.
    """
    
    INPUT_SITES = 'INPUT_SITES'
    INPUT_LHD_TILES = 'INPUT_LHD_TILES'
    DIR_VARIABLE = 'DIR_VARIABLE'

    def flags(self):
        # Désactivation du multithreading pour permettre l'ouverture sécurisée de la boîte de dialogue Qt depuis le thread principal de QGIS
        return QgsProcessingAlgorithm.FlagNoThreading

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_SITES, "Couche des sites (Emprises)",
            types=[QgsProcessing.TypeVectorPolygon],
            defaultValue='sites'))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LHD_TILES, "Couche des dalles LiDAR-HD (Dallage IGN) [OPTIONNELLE]",
            types=[QgsProcessing.TypeVectorPolygon],
            optional=True))

        project = QgsProject.instance()
        current_dir = QgsExpressionContextUtils.projectScope(project).variable('datadir_lidarHD')
        if not current_dir:
            current_dir = "G:/IGN_LIDAR-HD"

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.DIR_VARIABLE,
            "Emplacement racine des dalles LidarHD (@datadir_lidarHD)",
            defaultValue=current_dir))

    def clean_path_slashes(self, raw_path):
        """Force l'utilisation exclusive des slashes '/' pour QGIS et élimine les doublons."""
        if not raw_path: return ""
        return os.path.normpath(raw_path).replace("\\", "/")

    def processAlgorithm(self, parameters, context, feedback):
        
        selected_dir = self.clean_path_slashes(self.parameterAsString(parameters, self.DIR_VARIABLE, context))
        project = QgsProject.instance()
        
        # Persistance de la variable projet
        QgsExpressionContextUtils.setProjectVariable(project, 'datadir_lidarHD', selected_dir)
        
        # Construction et normalisation des chemins réseau
        pc_folder = self.clean_path_slashes(os.path.join(selected_dir, 'PC'))
        raster_folder = self.clean_path_slashes(os.path.join(selected_dir, 'Raster'))
        cbn_folder = self.clean_path_slashes(os.path.join(selected_dir, 'CBN'))
        dl_data_folder = self.clean_path_slashes(os.path.join(selected_dir, '_dl_data'))

        # Lecture sécurisée des répertoires pour éviter un crash si l'un d'eux manque
        raster_files = os.listdir(raster_folder) if os.path.exists(raster_folder) else []
        cbn_files = os.listdir(cbn_folder) if os.path.exists(cbn_folder) else []

        source_sites = self.parameterAsSource(parameters, self.INPUT_SITES, context)
        
        has_sources_analyzed = False
        source_tiles = None
        spatial_index = None
        tile_name_field = 'name'
        
        # Initialisation du dallage optionnel
        if parameters.get(self.INPUT_LHD_TILES):
            source_tiles = self.parameterAsSource(parameters, self.INPUT_LHD_TILES, context)
            if source_tiles:
                has_sources_analyzed = True
                feedback.pushInfo("⚡ Initialisation du dallage IGN optionnel...")
                spatial_index = QgsSpatialIndex(source_tiles.getFeatures())
                
                tile_fields = source_tiles.fields()
                for f in tile_fields:
                    if f.name().lower() == 'name':
                        tile_name_field = f.name()
                        break
                if tile_fields.indexOf(tile_name_field) == -1 and tile_fields.count() > 0:
                    tile_name_field = tile_fields.at(0).name()

        features = list(source_sites.getFeatures())
        if not features:
            feedback.reportError("Erreur : Aucune donnée trouvée à analyser selon vos filtres de sélection.")
            return {}

        idx_porteur = source_sites.fields().indexOf('porteur')
        idx_lidarhd = source_sites.fields().indexOf('lidarhd')
        
        exp_context = QgsExpressionContext()
        exp_context.appendScope(QgsExpressionContextUtils.projectScope(project))
        naming_base_expr = QgsExpression("\"dossier_client\" || if(\"ct_client\"='COMMUNE','','_'||\"lieux\") || '_' || coalesce(\"type\"||'_'||\"type2\", \"type\")")

        sites_audit_list = []
        
        # Compteurs globaux pour le rapport final de la console
        global_mnt_count, global_mns_count, global_mnb_count = 0, 0, 0
        global_mnt_cbn_count, global_mns_cbn_count, global_mnb_cbn_count = 0, 0, 0

        for feat in features:
            if feedback.isCanceled(): break
                
            geom = feat.geometry()
            if geom.isNull() or geom.isEmpty(): continue
            
            try:
                feat_parts = list(geom.asGeometryCollection()) if geom.isMultipart() else [geom]
            except Exception:
                feat_parts = [geom]
            
            num_parts_this_feat = len(feat_parts)

            porteur_val = "N/A"
            if idx_porteur != -1:
                p_attr = feat.attribute(idx_porteur)
                if p_attr is not None: porteur_val = str(p_attr).strip()

            scope = QgsExpressionContextScope()
            scope.setFeature(feat)
            exp_context.appendScope(scope)
            part_name_base = naming_base_expr.evaluate(exp_context)
            exp_context.popScope()

            if naming_base_expr.hasEvalError() or not part_name_base:
                part_name_base_clean = f"ATTRIBUT_MANQUANT_ID_{feat.id()}"
            else:
                part_name_base_clean = re.sub(r'[\\/*?:"<>|]', '-', str(part_name_base)).strip()

            lidarhd_val = False
            if idx_lidarhd != -1:
                val_attr = feat.attribute(idx_lidarhd)
                if val_attr is not None and str(val_attr).lower() in ('true', '1', 't', 'y', 'yes'):
                    lidarhd_val = True

            # Analyse itérative de chaque composante géométrique (Parts)
            for p_idx, part_geom in enumerate(feat_parts, start=1):
                part_suffix = f"_{p_idx}-{num_parts_this_feat}"
                name_with_part = f"{part_name_base_clean} ({p_idx}/{num_parts_this_feat})"

                # --- 🎯 ANALYSE DES NUAGES DE POINTS ---
                base_crop = f"LHD-PTS-C_{part_name_base_clean}_L93_IGN69{part_suffix}"
                base_cut = f"LHD-PTS-C-cut_{part_name_base_clean}_L93_IGN69{part_suffix}"

                path_laz_crop = self.clean_path_slashes(os.path.join(pc_folder, f"{base_crop}.laz"))
                path_copc_crop = self.clean_path_slashes(os.path.join(pc_folder, f"{base_crop}.copc.laz"))
                path_laz_cut = self.clean_path_slashes(os.path.join(pc_folder, f"{base_cut}.laz"))
                path_copc_cut = self.clean_path_slashes(os.path.join(pc_folder, f"{base_cut}.copc.laz"))

                has_laz_crop = os.path.exists(path_laz_crop)
                has_copc_crop = os.path.exists(path_copc_crop)
                has_laz_cut = os.path.exists(path_laz_cut)
                has_copc_cut = os.path.exists(path_copc_cut)

                laz_bytes = sum(os.path.getsize(p) for p in [path_laz_crop, path_laz_cut] if os.path.exists(p))
                copc_bytes = sum(os.path.getsize(p) for p in [path_copc_crop, path_copc_cut] if os.path.exists(p))
                
                laz_size_str = f"{laz_bytes / (1024 * 1024):.1f} Mo" if laz_bytes > 0 else "0 Mo"
                copc_size_str = f"{copc_bytes / (1024 * 1024):.1f} Mo" if copc_bytes > 0 else "0 Mo"
                poids_str = f"LAZ: {laz_size_str} | COPC: {copc_size_str}"
                
                files_found_count = sum([has_laz_crop, has_copc_crop, has_laz_cut, has_copc_cut])

                # --- 🎯 ANALYSE DES RASTERS METIER ---
                prefix_mnt = f"LHD-MNT_{part_name_base_clean}{part_suffix}_"
                prefix_mns = f"LHD-MNS_{part_name_base_clean}{part_suffix}_"
                prefix_mnb = f"LHD-MNB_{part_name_base_clean}{part_suffix}_"

                mnt_resolutions, mns_resolutions, mnb_resolutions = [], [], []
                raster_bytes = 0

                for f in raster_files:
                    f_path = self.clean_path_slashes(os.path.join(raster_folder, f))
                    if f.startswith(prefix_mnt) and f.endswith("_2154.tif"):
                        mnt_resolutions.append(f[len(prefix_mnt):-9])
                        raster_bytes += os.path.getsize(f_path)
                        global_mnt_count += 1
                    elif f.startswith(prefix_mns) and f.endswith("_2154.tif"):
                        mns_resolutions.append(f[len(prefix_mns):-9])
                        raster_bytes += os.path.getsize(f_path)
                        global_mns_count += 1
                    elif f.startswith(prefix_mnb) and f.endswith("_2154.tif"):
                        mnb_resolutions.append(f[len(prefix_mnb):-9])
                        raster_bytes += os.path.getsize(f_path)
                        global_mnb_count += 1

                mnt_status = f"✅ ({mnt_resolutions[0]})" if mnt_resolutions else "❌"
                mns_status = f"✅ ({mns_resolutions[0]})" if mns_resolutions else "❌"
                mnb_status = f"✅ ({mnb_resolutions[0]})" if mnb_resolutions else "❌"
                rasters_txt = f"MNT: {mnt_status} | MNS: {mns_status} | MNB: {mnb_status}"
                poids_raster_str = f"{raster_bytes / (1024 * 1024):.1f} Mo" if raster_bytes > 0 else "0 Mo"

                # --- 🎯 ANALYSE DES VECTEURS CBN ---
                prefix_mnt_cbn = f"LHD-MNT-CBN_{part_name_base_clean}_"
                prefix_mns_cbn = f"LHD-MNS-CBN_{part_name_base_clean}_"
                prefix_mnb_cbn = f"LHD-MNB-CBN_{part_name_base_clean}_"

                mnt_cbn_steps, mns_cbn_steps, mnb_cbn_steps = [], [], []
                cbn_bytes = 0

                for f in cbn_files:
                    if part_suffix not in f: continue
                    
                    f_path = self.clean_path_slashes(os.path.join(cbn_folder, f))
                    match = re.search(r'_(\d+M\d+)_L(\d)', f)
                    meta_str = f"{match.group(1)}-L{match.group(2)}" if match else "OK"

                    if f.startswith(prefix_mnt_cbn) and f.endswith(".gpkg"):
                        mnt_cbn_steps.append(meta_str)
                        cbn_bytes += os.path.getsize(f_path)
                        global_mnt_cbn_count += 1
                    elif f.startswith(prefix_mns_cbn) and f.endswith(".gpkg"):
                        mns_cbn_steps.append(meta_str)
                        cbn_bytes += os.path.getsize(f_path)
                        global_mns_cbn_count += 1
                    elif f.startswith(prefix_mnb_cbn) and f.endswith(".gpkg"):
                        mnb_cbn_steps.append(meta_str)
                        cbn_bytes += os.path.getsize(f_path)
                        global_mnb_cbn_count += 1

                mnt_cbn_status = f"✅ ({mnt_cbn_steps[0]})" if mnt_cbn_steps else "❌"
                mns_cbn_status = f"✅ ({mns_cbn_steps[0]})" if mns_cbn_steps else "❌"
                mnb_cbn_status = f"✅ ({mnb_cbn_steps[0]})" if mnb_cbn_steps else "❌"
                
                cbn_txt = f"MNT: {mnt_cbn_status} | MNS: {mns_cbn_status} | MNB: {mnb_cbn_status}"
                poids_cbn_str = f"{cbn_bytes / (1024 * 1024):.1f} Mo" if cbn_bytes > 0 else "0 Mo"

                # --- 🎯 ARBRE LOGIQUE DU DIAGNOSTIC ---
                has_any_raster = bool(mnt_resolutions or mns_resolutions or mnb_resolutions)
                has_any_cbn = bool(mnt_cbn_steps or mns_cbn_steps or mnb_cbn_steps)
                
                if files_found_count == 0:
                    emoji = "🔴"
                    if has_any_raster or has_any_cbn:
                        diag_msg = "PC absents mais Rasters/CBN existants (Incohérence)"
                    else:
                        diag_msg = "Livrables absents du stockage" if not lidarhd_val else "ALERTE : Validé en base mais introuvable !"
                elif files_found_count < 4:
                    emoji = "🔴"
                    missing_details = []
                    if not has_laz_crop: missing_details.append("Crop LAZ")
                    if not has_copc_crop: missing_details.append("Crop COPC")
                    if not has_laz_cut: missing_details.append("Cut LAZ")
                    if not has_copc_cut: missing_details.append("Cut COPC")
                    diag_msg = f"PC Incomplet (Manque : {', '.join(missing_details)})"
                else:
                    if not lidarhd_val:
                        emoji = "🟠"
                        diag_msg = "PC complets mais champ 'lidarhd' décoché (False)"
                    elif not (mnt_resolutions and mns_resolutions and mnb_resolutions):
                        emoji = "🟠"
                        diag_msg = "PC OK, mais matrice d'imagerie Raster incomplète"
                    elif not (mnt_cbn_steps and mns_cbn_steps and mnb_cbn_steps):
                        emoji = "🟠"
                        diag_msg = "PC & Rasters OK, mais Vecteurs CBN incomplets"
                    else:
                        emoji = "🟢"
                        diag_msg = "Tout OK (PC, Rasters & CBN validés sur le réseau)"

                # --- 🎯 ANALYSE CROISÉE DU REPERTOIRE _DL_DATA ---
                if has_sources_analyzed and spatial_index:
                    intersecting_ids = spatial_index.intersects(part_geom.boundingBox())
                    intersecting_tiles_status = []
                    
                    if intersecting_ids:
                        tile_req = QgsFeatureRequest().setFilterFids(intersecting_ids)
                        for tile_feat in source_tiles.getFeatures(tile_req):
                            if tile_feat.geometry().intersects(part_geom):
                                raw_tile_name = str(tile_feat.attribute(tile_name_field)).strip()
                                
                                base_tile = raw_tile_name
                                if base_tile.lower().endswith('.copc.laz'): base_tile = base_tile[:-9]
                                elif base_tile.lower().endswith('.laz'): base_tile = base_tile[:-4]

                                src_laz_copc = self.clean_path_slashes(os.path.join(dl_data_folder, f"{base_tile}.copc.laz"))
                                src_idx_copc = self.clean_path_slashes(os.path.join(dl_data_folder, f"{base_tile}.copc.copc.laz"))
                                
                                is_dl_active = False
                                for ext_tmp in ['.download', '.part', '.tmp', '.copc.laz.download', '.copc.laz.part']:
                                    if os.path.exists(src_laz_copc + ext_tmp) or os.path.exists(self.clean_path_slashes(os.path.join(dl_data_folder, f"{base_tile}{ext_tmp}"))):
                                        is_dl_active = True
                                        break

                                if os.path.exists(src_laz_copc) and os.path.exists(src_idx_copc):
                                    state_txt = "[3] Index erroné ⚠️" if os.path.getsize(src_idx_copc) == 0 else "[4] Dispo géocatalogue ✅"
                                elif os.path.exists(src_laz_copc) and not os.path.exists(src_idx_copc):
                                    state_txt = "[2] Index manquant ❌"
                                elif is_dl_active:
                                    state_txt = "[1] En téléchargement ⏳"
                                else:
                                    state_txt = "[0] À télécharger 📥"

                                intersecting_tiles_status.append(f"• {base_tile} ➔ {state_txt}")
                    
                    dalles_sources_txt = "\n".join(intersecting_tiles_status) if intersecting_tiles_status else "Aucune dalle source intersectée"
                else:
                    dalles_sources_txt = "Non audité"

                # Agrégation des informations métriques récoltées
                sites_audit_list.append({
                    'porteur': porteur_val,
                    'name_with_part': name_with_part,
                    'lidarhd_val': lidarhd_val,
                    'crop_laz': "✅" if has_laz_crop else "❌",
                    'crop_copc': "✅" if has_copc_crop else "❌",
                    'cut_laz': "✅" if has_laz_cut else "❌",
                    'cut_copc': "✅" if has_copc_cut else "❌",
                    'rasters_txt': rasters_txt,
                    'cbn_txt': cbn_txt,
                    'dalles_sources_txt': dalles_sources_txt,
                    'poids_str': poids_str,
                    'poids_raster_str': poids_raster_str,
                    'poids_cbn_str': poids_cbn_str,
                    'emoji': emoji,
                    'diag_msg': diag_msg
                })

        # Tri d'initialisation par chaîne alphanumérique sur le porteur et l'emprise
        sites_audit_list.sort(key=lambda x: (x['porteur'].lower(), x['name_with_part'].lower()))

        # Instanciation et affichage de la fenêtre d'audit
        if sites_audit_list:
            dialogue = LHD_Advanced_Diagnostic_Dialog(sites_audit_list, has_sources_analyzed=has_sources_analyzed)
            dialogue.exec()
        else:
            feedback.reportError("L'audit n'a renvoyé aucune ligne exploitable.")

        # Affichage du bilan de masse dans le panneau de log QGIS Processing
        feedback.pushInfo("\n" + "="*50)
        feedback.pushInfo(f"📊 DIAGNOSTIC CONSOLIDÉ SITES")
        feedback.pushInfo(f"• Fichiers Rasters -> MNT: {global_mnt_count} | MNS: {global_mns_count} | MNB: {global_mnb_count}")
        feedback.pushInfo(f"• Fichiers CBN    -> MNT: {global_mnt_cbn_count} | MNS: {global_mns_cbn_count} | MNB: {global_mnb_cbn_count}")
        feedback.pushInfo("="*50 + "\n")

        return {'DOSSIER_RESEAU_VERIFIE': pc_folder}

    def name(self): return 'lhd_sites_audit_script_v1_0_0'
    def displayName(self): return '[Lidar-HD sites] - Audit Global - Points, Rasters, Vecteurs (V1.0.0)'
    def group(self): return 'CartOtraC_lhd-sites_workflow'
    def groupId(self): return 'CartOtraC_lhd-sites_workflow'
    def createInstance(self): return LHD_sites_Audit_Split_Weights_Script_V1_0_0()
