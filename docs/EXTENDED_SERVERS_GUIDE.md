# Guide d'utilisation de l'édition 163 Pays d'AniData VPN

Ce guide explique comment utiliser la version étendue d'AniData VPN qui offre un accès à 163 pays à travers le monde.

## Introduction

AniData VPN - Édition 163 Pays est une version spéciale de notre application qui inclut tous les pays disponibles dans notre réseau mondial. Cette version vous permet d'établir des connexions VPN sécurisées vers un nombre beaucoup plus important de localisations par rapport à la version standard.

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Tkinter (pour l'interface graphique)
- Pillow/PIL (pour les éléments graphiques)
- WireGuard (recommandé pour les connexions VPN)

## Lancement de l'application avec 163 pays

Pour profiter de l'accès à tous les pays, vous devez utiliser le script de lancement spécial :

```bash
bash scripts/run_extended_servers.sh
```

Ce script :
1. Vérifie toutes les dépendances requises
2. S'assure que la configuration étendue est disponible et à jour
3. Lance l'application avec l'accès aux 163 pays

## Naviguer dans l'interface étendue

L'interface de l'édition 163 pays est similaire à celle de la version standard, mais avec une liste de serveurs beaucoup plus longue.

### Recherche de pays

Pour naviguer efficacement parmi les 163 pays :
1. Utilisez le menu déroulant par région pour filtrer par continent
2. Utilisez la barre de recherche pour trouver rapidement un pays spécifique
3. Faites défiler la liste complète des serveurs regroupés par région

### Performances des serveurs

Les performances des serveurs varient selon leur emplacement géographique :
- **Serveurs Tier 1** (Europe occidentale, Amérique du Nord, Asie de l'Est) : Bande passante 8-10 Gbps
- **Serveurs Tier 2** (Europe de l'Est, Asie du Sud-Est, Océanie) : Bande passante 5-8 Gbps
- **Serveurs Tier 3** (Afrique, Amérique du Sud, Moyen-Orient) : Bande passante 2-5 Gbps

## Connexion aux serveurs exotiques

Certains pays parmi les 163 disponibles peuvent avoir des caractéristiques particulières :

### Serveurs à haute latence
Les pays dans des régions éloignées peuvent présenter une latence plus élevée. Dans ces cas :
- Utilisez le protocole WireGuard pour de meilleures performances
- Activez l'option de compression dans les paramètres
- Désactivez les fonctionnalités multi-hop qui augmentent la latence

### Serveurs à accès restreint
Certains pays peuvent avoir des restrictions Internet spécifiques :
- Activez le mode "Furtif" (Stealth Mode) pour contourner les restrictions
- Utilisez l'option "Obfuscation" pour masquer le trafic VPN
- Activez le double routage pour une sécurité accrue

## Résolution des problèmes

### Le serveur choisi ne se connecte pas
1. Vérifiez votre connexion Internet
2. Essayez un autre protocole (OpenVPN au lieu de WireGuard)
3. Essayez un serveur différent dans le même pays
4. Redémarrez l'application

### La liste complète des pays ne s'affiche pas
1. Assurez-vous d'utiliser le script `run_extended_servers.sh`
2. Vérifiez que le fichier de configuration étendue existe
3. Si le problème persiste, régénérez la configuration :
   ```bash
   python3 scripts/update_servers.py -i infrastructure/servers/config.json -o infrastructure/servers/new_expanded_config.json
   ```

## Fonctionnalités spéciales

### Multi-hop sur serveurs internationaux
L'édition 163 pays vous permet de créer des chaînes de connexion multi-hop impliquant plusieurs continents :
1. Accédez aux paramètres avancés
2. Activez "Multi-hop routing"
3. Sélectionnez jusqu'à 3 pays pour le routage en cascade
4. Cliquez sur "Appliquer" pour configurer votre route personnalisée

### Rotation automatique des pays
Pour une anonymité maximale :
1. Activez "Rotation automatique" dans les paramètres
2. Définissez un intervalle (par exemple 30 minutes)
3. Sélectionnez des régions préférées pour la rotation
4. L'application changera automatiquement de pays selon l'intervalle défini

## Support et commentaires

Si vous rencontrez des problèmes avec l'édition 163 pays ou si vous avez des suggestions pour améliorer la couverture ou les performances, veuillez ouvrir un ticket sur notre dépôt GitHub ou contacter notre support technique.

---

*AniData VPN - Votre passeport digital pour le monde entier*