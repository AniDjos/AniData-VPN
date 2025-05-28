# Guide d'initialisation et de publication sur GitHub

Ce guide explique comment initialiser un dépôt Git local pour le projet AniData VPN et le publier sur GitHub.

## 1. Prérequis

- Un compte GitHub (créez-en un sur [github.com](https://github.com) si vous n'en avez pas encore)
- Git installé sur votre machine (vérifiez avec `git --version`)

## 2. Initialisation du dépôt Git local

Ouvrez un terminal et naviguez vers le répertoire racine du projet AniData VPN :

```bash
cd chemin/vers/VPN_anicet
```

Initialisez un nouveau dépôt Git :

```bash
git init
```

## 3. Configuration de votre identité Git

Configurez votre nom d'utilisateur et email Git (utilisez l'email associé à votre compte GitHub) :

```bash
git config user.name "Votre Nom"
git config user.email "votre.email@exemple.com"
```

## 4. Préparation des fichiers pour GitHub

Remplacez le README.md actuel par le README préparé pour GitHub :

```bash
mv README_GITHUB.md README.md
```

## 5. Premier commit

Ajoutez tous les fichiers au suivi Git :

```bash
git add .
```

Effectuez le premier commit :

```bash
git commit -m "Version initiale d'AniData VPN"
```

## 6. Création d'un nouveau dépôt sur GitHub

1. Connectez-vous à votre compte GitHub
2. Cliquez sur le bouton "+" en haut à droite, puis sélectionnez "New repository"
3. Nommez votre dépôt (ex: "AniData-VPN")
4. Ajoutez une description (optionnel) : "VPN ultra-sécurisé de nouvelle génération avec IA intégrée"
5. Choisissez si le dépôt doit être public ou privé
6. Ne cochez PAS l'option "Initialize this repository with a README"
7. Cliquez sur "Create repository"

## 7. Liaison avec le dépôt distant et premier push

GitHub vous affichera des instructions. Exécutez les commandes suivantes pour lier votre dépôt local au dépôt distant :

```bash
git remote add origin https://github.com/votre-username/AniData-VPN.git
git branch -M main
git push -u origin main
```

Remplacez `votre-username` par votre nom d'utilisateur GitHub et `AniData-VPN` par le nom que vous avez choisi pour votre dépôt.

## 8. Création d'une release pour les installateurs

1. Créez un dossier `releases` pour stocker les installateurs :

```bash
mkdir -p releases
```

2. Générez les installateurs pour différentes plateformes :

```bash
# Pour Windows (si vous êtes sur Windows)
python scripts/package_windows.py

# Pour Linux
python scripts/packaging/package_linux.py
```

3. Copiez les installateurs générés dans le dossier `releases` :

```bash
cp dist/*.exe releases/ 2>/dev/null
cp *.deb releases/ 2>/dev/null
cp *.rpm releases/ 2>/dev/null
cp *.AppImage releases/ 2>/dev/null
```

4. Ajoutez et committez ces fichiers :

```bash
git add releases/
git commit -m "Ajout des installateurs pour la version initiale"
git push origin main
```

5. Sur GitHub, naviguez vers votre dépôt et cliquez sur "Releases" dans le menu de droite
6. Cliquez sur "Create a new release"
7. Entrez "v1.0.0" comme tag de version
8. Donnez un titre à votre release (ex: "Version initiale d'AniData VPN")
9. Ajoutez une description détaillant les fonctionnalités
10. Téléversez les fichiers d'installation depuis votre dossier `releases`
11. Cliquez sur "Publish release"

## 9. Activer GitHub Pages pour la documentation (optionnel)

Pour héberger la documentation de votre projet :

1. Dans votre dépôt GitHub, allez dans "Settings" > "Pages"
2. Sous "Source", sélectionnez "main" et "/docs" comme dossier
3. Cliquez sur "Save"

La documentation sera disponible à l'adresse `https://votre-username.github.io/AniData-VPN/`.

## 10. Configuration d'un workflow CI/CD (optionnel)

Pour automatiser les tests et la génération des installateurs :

1. Créez un dossier `.github/workflows` dans votre projet :

```bash
mkdir -p .github/workflows
```

2. Créez un fichier de workflow CI/CD (voir la documentation GitHub Actions pour plus de détails)

## Résolution des problèmes courants

- **Erreur de push** : Si vous recevez une erreur lors du push, vérifiez que vous avez les droits d'accès au dépôt.
- **Fichiers trop volumineux** : GitHub limite la taille des fichiers. Utilisez Git LFS pour les gros fichiers.
- **Conflits de fusion** : Utilisez `git pull` avant de push pour synchroniser les changements.

Pour toute autre question, consultez la [documentation GitHub](https://docs.github.com).