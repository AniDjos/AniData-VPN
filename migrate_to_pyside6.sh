#!/bin/bash
# Script de migration de PyQt5 à PySide6 pour AniData VPN

set -e # Arrêter en cas d'erreur

echo "Migration de PyQt5 à PySide6 pour AniData VPN"
echo "=============================================="

# Déterminer le chemin du script et le répertoire du projet
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Si nous sommes déjà dans le répertoire VPN_anicet
if [[ "$SCRIPT_DIR" == *"/VPN_anicet" ]]; then
  PROJECT_DIR="$SCRIPT_DIR"
fi

cd "$PROJECT_DIR"

# Créer et activer un environnement virtuel
echo "Création d'un environnement virtuel..."
VENV_DIR="$PROJECT_DIR/venv_pyside6"

# Vérifier si python3-venv est installé
if ! dpkg -l | grep -q python3-venv; then
  echo "Installation de python3-venv..."
  sudo apt-get update
  sudo apt-get install -y python3-venv
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

# Activer l'environnement virtuel
source "$VENV_DIR/bin/activate"

# Mettre à jour pip
echo "Mise à jour de pip..."
pip install --upgrade pip

# Installer PySide6 et dépendances
echo "Installation des dépendances dans l'environnement virtuel..."
pip install PySide6 pyqtgraph numpy

# Remplacer PyQt5 par PySide6 dans les fichiers Python
echo "Modification des fichiers source..."

# Liste des fichiers à modifier
FILES=(
  "run_modern_ui.py"
  "ui/desktop/modern_bridge.py"
  "ui/desktop/modern_ui.py"
  "ui/desktop/bandwidth_graph.py"
  "ui/desktop/main.py"
)

for file in "${FILES[@]}"; do
  echo "Traitement de $file"
  
  # Remplacer les imports
  sed -i 's/from PyQt5\./from PySide6./g' "$file"
  sed -i 's/import PyQt5\./import PySide6./g' "$file"
  
  # Remplacer pyqtSignal par Signal
  sed -i 's/pyqtSignal/Signal/g' "$file"
  
  # Remplacer le message d'erreur
  sed -i 's/ERROR: PyQt5 and PyQtWebEngine are required. Install with:/ERROR: PySide6 is required. Install with:/g' "$file"
  sed -i 's/pip install PyQt5 PyQtWebEngine/pip install PySide6/g' "$file"
done

# Créer un module de compatibilité
echo "Création du module de compatibilité..."
mkdir -p ui/compat
cat > ui/compat/__init__.py << 'EOF'
# Module de compatibilité pour faciliter la transition PyQt5 -> PySide6
from PySide6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

# Alias pour les noms de classe PyQt5
QtCore.pyqtSignal = QtCore.Signal
QtCore.pyqtSlot = QtCore.Slot
QtCore.pyqtProperty = QtCore.Property
EOF

echo "Migration terminée avec succès!"
echo "Pour exécuter l'application:"
echo "1. Activez d'abord l'environnement virtuel:"
echo "   source $VENV_DIR/bin/activate"
echo "2. Puis lancez l'application:"
echo "   python run_modern_ui.py"

# Créer un script de lancement rapide
cat > run_with_pyside6.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$SCRIPT_DIR/venv_pyside6/bin/activate"
python "$SCRIPT_DIR/run_modern_ui.py"
EOF

chmod +x run_with_pyside6.sh

echo ""
echo "Un script de lancement rapide a été créé. Vous pouvez aussi simplement exécuter:"
echo "   ./run_with_pyside6.sh"

# Désactiver l'environnement virtuel
deactivate