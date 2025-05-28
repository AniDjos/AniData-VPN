# Guide d'installation de AniData VPN sur Windows

Ce guide explique comment créer un installateur Windows pour AniData VPN et comment l'installer sur un système Windows.

## Prérequis pour la création de l'installateur

Pour créer l'installateur Windows, vous aurez besoin d'un système Windows avec :

- Python 3.8 ou supérieur
- Git pour Windows
- Inno Setup 6 (sera installé automatiquement par le script si nécessaire)

## Étape 1 : Cloner le dépôt sur Windows

Ouvrez PowerShell ou l'invite de commande Windows et exécutez :

```powershell
# Cloner le dépôt
git clone https://github.com/AniDjos/AniData-VPN.git
cd AniData-VPN
```

## Étape 2 : Installer les dépendances Python

```powershell
# Installer les dépendances nécessaires
pip install pyinstaller pywin32 pillow
```

## Étape 3 : Générer l'installateur Windows

```powershell
# Exécuter le script de packaging Windows
python scripts/package_windows.py
```

Ce script :
1. Vérifie et installe les dépendances nécessaires
2. Prépare la configuration étendue avec 163 pays
3. Compile l'application avec PyInstaller
4. Crée un installateur Windows avec Inno Setup

L'installateur généré se trouvera dans le dossier `dist/` avec un nom similaire à `AniDataVPN_1.0.0_Setup.exe`.

## Étape 4 : Installer AniData VPN sur Windows

1. Double-cliquez sur le fichier d'installation `AniDataVPN_1.0.0_Setup.exe`
2. Suivez les instructions de l'assistant d'installation :
   - Acceptez le contrat de licence
   - Choisissez le dossier d'installation (par défaut : `C:\Program Files\AniData VPN`)
   - Sélectionnez les options d'installation souhaitées (raccourci bureau, démarrage avec Windows)
   - Cliquez sur "Installer"
   - Attendez que l'installation se termine

3. Lorsque l'installation est terminée, vous pouvez démarrer AniData VPN de plusieurs façons :
   - Via le raccourci sur le bureau (si cette option a été choisie)
   - Via le menu Démarrer > AniData VPN
   - Via la recherche Windows en tapant "AniData VPN"

## Utilisation de l'application

Après le lancement, l'application AniData VPN - Édition 163 Pays s'ouvrira avec :

1. Une liste complète des 163 pays disponibles
2. La possibilité de se connecter à n'importe lequel de ces serveurs
3. Des options de configuration avancées pour personnaliser votre expérience VPN

## Résolution des problèmes

### L'installateur ne se lance pas
- Vérifiez que vous avez les droits administrateur
- Désactivez temporairement votre antivirus
- Vérifiez que Windows Defender n'a pas bloqué le fichier

### L'application ne se connecte pas
- Vérifiez votre connexion Internet
- Assurez-vous que les ports nécessaires ne sont pas bloqués par votre pare-feu
- Essayez de redémarrer l'application avec des droits administrateur

### Les 163 pays ne s'affichent pas
- Vérifiez que vous avez installé la version complète avec l'édition 163 pays
- Dans l'application, allez dans Paramètres > À propos pour vérifier la version
- Si nécessaire, réinstallez l'application en utilisant l'installateur généré avec le script modifié

## Désinstallation

Pour désinstaller AniData VPN :

1. Ouvrez le Panneau de configuration Windows
2. Accédez à "Programmes et fonctionnalités" ou "Applications et fonctionnalités"
3. Trouvez "AniData VPN" dans la liste
4. Sélectionnez-le et cliquez sur "Désinstaller"
5. Suivez les instructions pour terminer la désinstallation

## Support technique

Pour toute assistance supplémentaire, veuillez :
- Consulter la documentation dans le dossier `docs/`
- Ouvrir un ticket sur notre dépôt GitHub
- Contacter notre équipe de support à support@anidata-vpn.com