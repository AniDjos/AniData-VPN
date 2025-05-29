# AniData VPN - Interface Tkinter

Cette version d'AniData VPN utilise Tkinter comme alternative à PyQt5/PyQtWebEngine. Tkinter est inclus dans l'installation standard de Python, ce qui rend cette version plus facile à installer et à exécuter sans environnements virtuels.

## Avantages de l'interface Tkinter

- **Pas d'environnement virtuel nécessaire** : Tkinter est inclus dans Python
- **Dépendances minimales** : Nécessite uniquement matplotlib et numpy
- **Installation simple** : Fonctionne sur la plupart des systèmes sans configuration complexe
- **Interface légère** : Consomme moins de ressources que les alternatives basées sur Qt

## Installation

Le script de lancement `run_tkinter_ui.sh` vérifie et installe automatiquement les dépendances nécessaires :

```bash
./run_tkinter_ui.sh
```

Si vous préférez installer manuellement les dépendances :

```bash
# Sur Debian/Ubuntu/Kali
sudo apt-get install python3-tk python3-numpy python3-matplotlib

# Sur Fedora
sudo dnf install python3-tkinter python3-numpy python3-matplotlib

# Sur ArchLinux
sudo pacman -S tk python-numpy python-matplotlib
```

## Utilisation

1. Lancez l'application :
```bash
./run_tkinter_ui.sh
```

2. Sélectionnez un serveur VPN dans la liste
3. Cliquez sur "Connect" pour établir la connexion VPN
4. Consultez les statistiques de connexion et le graphique de bande passante
5. Utilisez les paramètres pour personnaliser votre expérience

## Fonctionnalités

- **Carte du monde** : Visualisation des emplacements des serveurs (version statique)
- **Liste de serveurs** : Recherche et sélection de serveurs VPN
- **Statistiques en temps réel** : Vitesse de téléchargement/envoi et données transférées
- **Graphique de bande passante** : Visualisation de l'utilisation du réseau
- **Paramètres configurables** : Thème, protection contre les fuites, protocole par défaut

## Résolution des problèmes

### Problèmes d'affichage

Si l'interface s'affiche mal (éléments mal positionnés ou trop petits/grands) :

```bash
export TCLLIBPATH=/usr/lib/tcltk/x86_64-linux-gnu/
export TK_LIBRARY=/usr/lib/tcltk/x86_64-linux-gnu/tk8.6
./run_tkinter_ui.sh
```

### Erreur "no display name and no $DISPLAY environment variable"

Cette erreur se produit lorsque vous essayez d'exécuter l'application dans un environnement sans interface graphique :

```bash
# Solution si vous utilisez SSH
ssh -X user@host  # Activer le transfert X11, puis lancer l'application
```

### Matplotlib ou Numpy manquants

Si vous rencontrez des erreurs liées à matplotlib ou numpy :

```bash
pip3 install --user matplotlib numpy
```

## Différences avec la version PyQt5/PySide6

- Interface légèrement simplifiée mais toutes les fonctionnalités principales sont présentes
- La carte interactive est remplacée par une visualisation statique
- Le rendu graphique utilise matplotlib au lieu de pyqtgraph
- Les animations et transitions sont moins fluides mais l'application est plus légère

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une pull request pour améliorer cette version de l'interface.