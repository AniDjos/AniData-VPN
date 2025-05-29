# Migration de PyQt5 vers PySide6

Ce guide explique comment migrer l'application AniData VPN de PyQt5 vers PySide6.

## Pourquoi migrer vers PySide6 ?

- **Licence plus permissive** : PySide6 est sous licence LGPL, tandis que PyQt5 est sous licence GPL.
- **Support officiel** : PySide6 est développé et maintenu directement par Qt Company.
- **API presque identique** : La transition est simple car les API sont très similaires.
- **Meilleure intégration** avec d'autres outils Qt.

## Instructions pour la migration automatique

1. **Utilisez le script de migration automatique** :

```bash
cd <répertoire-parent-de-VPN_anicet>
./VPN_anicet/migrate_to_pyside6.sh
```

Ce script effectue automatiquement :
- L'installation de PySide6 et des dépendances nécessaires
- La modification des fichiers source pour utiliser PySide6
- La création d'un module de compatibilité

2. **Exécutez l'application** :

```bash
python VPN_anicet/run_modern_ui.py
```

## Migration manuelle (si nécessaire)

Si vous préférez effectuer la migration manuellement :

1. **Installez PySide6** :
```bash
pip install PySide6 pyqtgraph numpy
```

2. **Modifiez les imports** dans les fichiers suivants :
   - `run_modern_ui.py`
   - `ui/desktop/modern_bridge.py`
   - `ui/desktop/modern_ui.py`
   - `ui/desktop/bandwidth_graph.py`
   - `ui/desktop/main.py`

   Remplacez :
   ```python
   from PyQt5.X import Y
   ```
   Par :
   ```python
   from PySide6.X import Y
   ```

3. **Remplacez les signaux** :
   - Remplacez `pyqtSignal` par `Signal`
   - Ajustez les connexions de signaux si nécessaire

## Principales différences entre PyQt5 et PySide6

1. **Signaux et slots** :
   - PyQt5 : `pyqtSignal`, `pyqtSlot`
   - PySide6 : `Signal`, `Slot`

2. **Comportement de `connect()`** :
   - Les deux bibliothèques acceptent la même syntaxe, mais PySide6 est parfois plus strict

3. **Gestion des surcharges de méthodes** :
   - Des ajustements mineurs peuvent être nécessaires pour les méthodes surchargées

## Dépannage

Si vous rencontrez des problèmes après la migration :

1. **Erreurs d'import** : Vérifiez que PySide6 est correctement installé
   ```bash
   pip show PySide6
   ```

2. **Erreurs avec les signaux** : Assurez-vous que tous les `pyqtSignal` ont été convertis en `Signal`

3. **Problèmes avec QtWebEngineWidgets** : Assurez-vous que la version complète de PySide6 est installée
   ```bash
   pip uninstall PySide6
   pip install PySide6
   ```

4. **Incompatibilités avec pyqtgraph** : Mettez à jour pyqtgraph vers la dernière version
   ```bash
   pip install --upgrade pyqtgraph
   ```

## Ressources supplémentaires

- [Documentation officielle de PySide6](https://doc.qt.io/qtforpython-6/)
- [Guide de migration Qt for Python](https://wiki.qt.io/Qt_for_Python_Migration_Guide)