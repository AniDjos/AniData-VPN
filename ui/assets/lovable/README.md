# Style Lovable.ai pour AniData VPN

Ce répertoire contient les fichiers de thème et les ressources graphiques pour appliquer le style Lovable.ai à l'application AniData VPN.

## Caractéristiques du style Lovable.ai

Le style Lovable.ai est caractérisé par :

- Un design épuré et moderne avec des bords arrondis
- Des couleurs vives mais harmonieuses
- Une expérience utilisateur intuitive et agréable
- Des transitions douces et des animations subtiles
- Une typographie claire et lisible

## Éléments inclus

- **lovable_theme.css** : Feuille de style principale définissant l'apparence de l'interface
- **Icônes** : Ensemble d'icônes conçues dans le style Lovable.ai
  - connect.png : Bouton de connexion
  - disconnect.png : Bouton de déconnexion
  - settings.png : Icône des paramètres
  - tray_icon.png : Icône de la barre système
  - logo.png : Logo de l'application
  - status_*.png : Indicateurs d'état
  - dropdown_arrow.png : Flèche pour les menus déroulants

## Utilisation

Le thème est automatiquement appliqué lorsque l'option "lovable" est sélectionnée dans les paramètres de l'application. Vous pouvez modifier cette option dans :

Paramètres → Interface utilisateur → Thème → lovable

## Personnalisation

Vous pouvez personnaliser davantage ce thème en modifiant le fichier CSS ou en remplaçant les icônes par vos propres designs. Assurez-vous de conserver les mêmes noms de fichiers pour garantir la compatibilité.

## Génération des icônes

Les icônes peuvent être régénérées à l'aide du script Python inclus :

```
python generate_lovable_icons.py
```

Ce script nécessite la bibliothèque PIL (Pillow) pour fonctionner.