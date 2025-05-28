AniData VPN - Édition 163 Pays
==============================

Guide d'installation et d'utilisation pour Windows
-------------------------------------------------

1. Prérequis:
   - Python 3.8 ou supérieur installé
   - Les bibliothèques Python: tkinter, pillow (PIL)
   - Optionnel: WireGuard pour des connexions VPN complètes

2. Installation sur Windows:
   a) Installez Python depuis python.org
   b) Ouvrez l'invite de commande en tant qu'administrateur
   c) Installez les dépendances requises:
      pip install pillow

3. Lancement de l'application:
   - Double-cliquez sur le fichier "AniDataVPN_163Countries.bat"
   - OU ouvrez une invite de commande et exécutez:
     python scripts/simple_vpn.py

4. Création d'un installateur Windows (avancé):
   - Si vous souhaitez créer un installateur Windows (.exe):
   - Installez PyInstaller: pip install pyinstaller
   - Installez Inno Setup (https://jrsoftware.org/isinfo.php)
   - Exécutez: python scripts/windows_package.py

En cas de problème:
------------------
- Vérifiez que Python et toutes les dépendances sont installés
- Consultez la documentation dans le dossier "docs/"
- Si les 163 pays ne s'affichent pas, assurez-vous que le fichier 
  "infrastructure/servers/expanded_config.json" existe

Profitez de votre accès VPN mondial!
