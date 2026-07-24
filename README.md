# QGIS_python

Scripts et modèles de traitements, plugins Python pour QGIS.

## Structure du projet

```
QGIS_python/
├── README.md                          # Documentation générale
├── LICENSE                            # Licence du projet
└── scripts/                           # Dossier principal pour les scripts QGIS
    ├── __init__.py                    # Initialisation du module scripts
    └── cartotrac_lhd-sites_workflow/  # Module dédié aux scripts/traitements CartOtraC Lidar-HD sites
        ├── __init__.py                # Enregistrement de l'algorithme dans QGIS
        └── lhd_sites_audit_v1_0_0.py   # Script d'audit des données locales (V1.0.0)
```

## Modules disponibles

### 1. **Audit Lidar-HD Sites (V1.0.0)**
**Chemin** : `scripts/cartotrac_lhd-sites_workflow/`

**Description** :
Outil d'audit structuré pour les données Lidar-HD, incluant :
- **Nuages de points** (LAZ/COPC) : Vérification des versions Crop et Cut.
- **Rasters métier** (MNT, MNS, MNB) : Analyse des fichiers TIFF et de leurs résolutions.
- **Vecteurs CBN** : Vérification des fichiers GeoPackage (MNT-CBN, MNS-CBN, MNB-CBN).
- **Diagnostic global** : Statut visuel (🔴/🟠/🟢) avec messages détaillés.
- **Analyse optionnelle** : Vérification du répertoire `_dl_data` pour les dalles sources.

**Fonctionnalités clés** :
- Interface graphique Qt avec tableau dynamique (tri, colorisation, redimensionnement intelligent).
- Calcul des poids (taille en Mo) pour chaque type de données.
- Persistance de la variable de projet `datadir_lidarHD` dans QGIS.
- Support des géométries multipartites.

**Utilisation** :
1. Dans QGIS, ouvrez la boîte à outils de traitement (`Traitement > Boîte à outils`).
2. Cherchez l'algorithme : **`[Lidar-HD sites] - Audit Global - Points, Rasters, Vecteurs (V1.0.0)`**.
3. Sélectionnez :
   - **Couche des sites (Emprises)** : Une couche vectorielle polygonale (ex : `sites`).
   - **Couche des dalles LiDAR-HD (optionnelle)** : Une couche de dallage IGN pour l'analyse croisée.
   - **Emplacement racine des dalles LidarHD** : Répertoire parent (ex : `G:/IGN_LIDAR-HD`).
4. Exécutez l'algorithme pour afficher le tableau de bord d'audit.

**Champs requis pour la couche des sites** :
- `porteur` (optionnel) : Nom du porteur du projet.
- `lidarhd` (booléen) : Indique si le site est validé en base (True/False).
- `dossier_client`, `ct_client`, `lieux`, `type`, `type2` : Utilisés pour générer le nom de l'emprise.

**Variables de projet QGIS** :
- `datadir_lidarHD` : Chemin racine des données Lidar-HD. Persisté entre les exécutions.

**Structure attendue des répertoires** :
```
[datadir_lidarHD]/
├── PC/               # Nuages de points (LAZ/COPC)
├── Raster/           # Rasters métier (TIFF)
├── CBN/              # Vecteurs CBN (GeoPackage)
└── _dl_data/        # Dalles sources (optionnel)
```

**Exemple de nommage des fichiers** :
- Nuages de points : `LHD-PTS-C_[NOM]_L93_IGN69_[PART].laz` ou `.copc.laz`
- Rasters : `LHD-MNT_[NOM][PART]_[RÉSOLUTION]_2154.tif`
- Vecteurs CBN : `LHD-MNT-CBN_[NOM]_[MÉTADONNÉES].gpkg`

---

## Installation

### Méthode 1 : Intégration manuelle dans QGIS
1. Copiez le dossier `scripts/` dans le répertoire des plugins QGIS :
   - Windows : `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - Linux/macOS : `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
2. Redémarrez QGIS.
3. L'algorithme sera disponible dans la boîte à outils de traitement.

### Méthode 2 : Utilisation via un dépôt Git
1. Clonez ce dépôt dans un dossier accessible par QGIS.
2. Ajoutez le chemin du dossier `scripts/` dans les paramètres Python de QGIS :
   - `Options > Système > Variables d'environnement > PYTHONPATH`
3. Redémarrez QGIS.

---

## Développement

### Prérequis
- QGIS 3.x (testé avec QGIS 3.28+)
- Python 3.9+
- Bibliothèques : `qgis.core`, `qgis.PyQt` (inclus avec QGIS)

### Contribution
1. Forkez le dépôt.
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/ma-fonctionnalité`).
3. Commitez vos modifications (`git commit -m "Ajout de ma fonctionnalité"`).
4. Poussez vers votre fork (`git push origin feature/ma-fonctionnalité`).
5. Ouvrez une Pull Request.

---

## Licence
Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
