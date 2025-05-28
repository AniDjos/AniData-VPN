# Guide pour publier AniData VPN sur GitHub

Ce guide explique comment publier votre application AniData VPN sur GitHub pour permettre à d'autres utilisateurs de la télécharger et l'installer facilement.

## 1. Préparation

J'ai créé plusieurs fichiers pour vous aider à préparer votre projet pour GitHub:

1. **README_GITHUB.md** - Un README attractif qui servira de page d'accueil pour votre dépôt
2. **.gitignore** - Pour éviter de committer des fichiers inutiles
3. **LICENSE** - Une licence propriétaire pour protéger votre code
4. **docs/GITHUB_SETUP.md** - Instructions détaillées sur l'initialisation du dépôt
5. **scripts/prepare_release.py** - Script pour préparer des releases

## 2. Étapes de publication

### Configuration initiale

1. Ouvrez un terminal et naviguez vers le répertoire du projet:
   ```bash
   cd chemin/vers/VPN_anicet
   ```

2. Remplacez le README actuel par celui préparé pour GitHub:
   ```bash
   mv README_GITHUB.md README.md
   ```

3. Initialisez un dépôt Git:
   ```bash
   git init
   git config user.name "Votre Nom"
   git config user.email "votre.email@exemple.com"
   ```

4. Ajoutez les fichiers au suivi Git:
   ```bash
   git add .
   git commit -m "Version initiale d'AniData VPN"
   ```

### Création du dépôt GitHub

1. Connectez-vous à GitHub et créez un nouveau dépôt nommé "AniData-VPN"
2. Ne cochez PAS l'option "Initialize this repository with a README"
3. Suivez les instructions pour lier votre dépôt local:
   ```bash
   git remote add origin https://github.com/votre-username/AniData-VPN.git
   git branch -M main
   git push -u origin main
   ```

### Préparation des releases

1. Créez des versions installables pour les différentes plateformes:
   ```bash
   python scripts/prepare_release.py --version 1.0.0
   ```
   
   Ce script va:
   - Mettre à jour les informations de version
   - Générer des packages pour Windows et/ou Linux (selon votre OS)
   - Créer des notes de release et des checksums
   - Tout placer dans un dossier "releases"

2. Committez les fichiers de release:
   ```bash
   git add releases/
   git commit -m "Ajout des installateurs pour la version 1.0.0"
   git push origin main
   ```

### Publication sur GitHub

1. Créez un tag pour la version:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

2. Sur GitHub, allez dans votre dépôt et cliquez sur "Releases" puis "Create a new release"
3. Sélectionnez le tag "v1.0.0"
4. Donnez un titre et copiez le contenu de releases/RELEASE_NOTES_1.0.0.md
5. Téléversez tous les fichiers du dossier "releases"
6. Cliquez sur "Publish release"

## 3. Maintenance et mises à jour

Pour les futures mises à jour:

1. Modifiez votre code et testez-le
2. Exécutez le script prepare_release.py avec une nouvelle version:
   ```bash
   python scripts/prepare_release.py --version 1.0.1
   ```
3. Committez les changements et créez un nouveau tag:
   ```bash
   git commit -am "Version 1.0.1 avec corrections de bugs"
   git tag -a v1.0.1 -m "Version 1.0.1"
   git push origin main --tags
   ```
4. Créez une nouvelle release sur GitHub avec les fichiers générés

## 4. Promotion de votre application

Une fois votre application publiée:

1. Ajoutez des captures d'écran dans docs/screenshots/
2. Activez GitHub Pages dans les paramètres du dépôt
3. Partagez l'URL de votre dépôt et la page des releases

Pour plus de détails, consultez docs/GITHUB_SETUP.md.