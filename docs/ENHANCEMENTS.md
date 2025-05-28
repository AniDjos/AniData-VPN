# Améliorations d'AniData VPN

Ce document détaille les améliorations apportées à l'application AniData VPN pour en faire un produit professionnel complet.

## Table des matières

1. [Interface utilisateur](#interface-utilisateur)
2. [Packaging et installation](#packaging-et-installation)
3. [Intégration système](#intégration-système)
4. [Expansion des serveurs](#expansion-des-serveurs)
5. [Guide de build](#guide-de-build)

---

## Interface utilisateur

### Thème Bleu Azur

La couleur principale de l'application a été modifiée pour utiliser le Bleu Azur (#007FFF) comme arrière-plan. Les modifications incluent :

- Fond uniforme Bleu Azur avec éléments décoratifs subtils
- Contraste amélioré pour assurer la lisibilité du texte
- Styles spécifiques pour les composants sur fond bleu (boutons, étiquettes, etc.)
- Design unifié sur toutes les plateformes

Les modifications ont été appliquées à la méthode `create_background()` et aux styles TTK pour assurer la cohérence visuelle.

---

## Packaging et installation

### Windows

Le script de packaging Windows (`scripts/package_windows.py`) a été amélioré pour :

- Créer un véritable installeur Windows (.exe) via Inno Setup
- S'assurer que l'application apparaît dans la liste des programmes installés
- Ajouter l'application au menu Démarrer
- Créer un raccourci sur le bureau (optionnel)
- Gérer l'intégration du VPN au système Windows

Pour compiler le package Windows :

```bash
cd VPN_anicet/scripts
python package_windows.py
```

### Linux

Un nouveau script de packaging Linux a été créé (`scripts/packaging/package_linux.py`) qui permet de générer :

- Des packages Debian (.deb) pour Ubuntu/Debian
- Des packages RPM (.rpm) pour Fedora/CentOS
- Des AppImages exécutables sur toutes les distributions Linux

Pour compiler le package Linux :

```bash
cd VPN_anicet/scripts/packaging
python package_linux.py --type all  # Options: deb, rpm, appimage, all
```

---

## Intégration système

### Windows

- L'application est reconnue comme fournisseur VPN par Windows
- Utilisation du TAP-Windows Virtual Network Adapter pour la connexion VPN
- Installation d'un service système pour gérer la connexion VPN en arrière-plan
- Intégration avec le panneau de configuration réseau de Windows

### Linux

- Intégration avec NetworkManager pour la gestion des connexions VPN
- Script d'installation pour les fichiers de configuration système
- Support de DBus pour les notifications système
- Apparition dans les paramètres réseau du système

---

## Expansion des serveurs

L'application prend désormais en charge plus de 150 pays pour les connexions VPN.

- Le script `scripts/update_servers.py` a été créé pour générer automatiquement des serveurs supplémentaires
- Tous les nouveaux serveurs respectent le même format de configuration que les serveurs existants
- Chaque serveur inclut des informations de coordonnées, bande passante, et protocoles disponibles
- Les fonctionnalités de détection automatique de charge et ping fonctionnent sur tous les serveurs

Pour mettre à jour la liste des serveurs :

```bash
cd VPN_anicet/scripts
python update_servers.py -i ../infrastructure/servers/config.json -o ../infrastructure/servers/expanded_config.json
```

---

## Guide de build

### Prérequis

#### Windows
- Python 3.8 ou supérieur
- Inno Setup 6 (installé automatiquement par le script si absent)
- PyInstaller (`pip install pyinstaller`)
- Pillow (`pip install Pillow`)
- pywin32 (`pip install pywin32`)

#### Linux
- Python 3.8 ou supérieur
- Outils de build selon la distribution (installés automatiquement)
- PyInstaller (`pip install pyinstaller`)
- Pillow (`pip install Pillow`)
- Outils de packaging : dpkg-deb (Debian), rpmbuild (RPM), appimagetool (AppImage)

### Procédure de compilation

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-repo/VPN_anicet.git
   cd VPN_anicet
   ```

2. Mettre à jour la liste des serveurs :
   ```bash
   python scripts/update_servers.py
   ```

3. Compiler le package pour votre plateforme :

   **Windows** :
   ```bash
   python scripts/package_windows.py
   ```

   **Linux** :
   ```bash
   python scripts/packaging/package_linux.py
   ```

4. Les fichiers d'installation se trouveront dans le dossier `dist/`

### Tests

Pour tester l'application après l'installation :

1. Vérifier que l'application apparaît dans le menu Démarrer/Applications
2. Vérifier que le raccourci du bureau fonctionne
3. Lancer l'application et tester la connexion à différents serveurs
4. Vérifier l'intégration dans les paramètres réseau du système
5. Tester la détection automatique de charge des serveurs

---

## Dépannage

- **Windows** : Si l'intégration VPN ne fonctionne pas, vérifiez que TAP-Windows est correctement installé
- **Linux** : Si le VPN n'apparaît pas dans NetworkManager, exécutez `sudo systemctl restart NetworkManager`
- **Serveurs** : Si certains serveurs ne sont pas disponibles, utilisez l'outil de diagnostic avec `--check-servers`

---

Pour plus d'informations, consultez la documentation complète dans le répertoire `docs/`.