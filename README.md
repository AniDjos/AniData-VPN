# AniData VPN

![AniData VPN Logo](ui/assets/icon.png)

AniData VPN est un VPN ultra-sécurisé de nouvelle génération, conçu pour offrir un anonymat complet et une protection avancée contre la surveillance, même face à des acteurs étatiques sophistiqués.

## ✨ Caractéristiques principales

- **Sécurité maximale**: Chiffrement AES-256 + TLS 1.3, multi-hop routing, protection contre les fuites
- **IA intégrée**: Routage dynamique et intelligent piloté par intelligence artificielle
- **Couverture mondiale**: Accès à plus de 150 pays avec rotation automatique des serveurs
- **Multi-protocole**: WireGuard, OpenVPN, IKEv2/IPSec et mode furtif
- **Interface intuitive**: Tableau de bord graphique avec carte interactive et métriques en temps réel
- **Protection avancée**: DNS sécurisé (DoH/DoT), kill switch intégré, double authentification

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Tkinter (interface graphique)
- WireGuard (optionnel, mais recommandé pour les connexions VPN complètes)

### Linux

```bash
# Cloner le dépôt
git clone https://github.com/votre-username/AniData-VPN.git
cd AniData-VPN

# Installer les dépendances
sudo apt-get install python3-tk wireguard-tools  # Pour Ubuntu/Debian
# ou
sudo dnf install python3-tkinter wireguard-tools  # Pour Fedora/CentOS

# Lancer l'application
bash scripts/run_ui.sh
```

### Windows

1. Téléchargez le [dernier installeur Windows](https://github.com/votre-username/AniData-VPN/releases/latest/download/AniDataVPN_Setup.exe)
2. Exécutez l'installeur et suivez les instructions
3. Lancez AniData VPN depuis le menu Démarrer ou le raccourci sur le bureau

### Création d'un package Linux

```bash
cd AniData-VPN/scripts/packaging
python3 package_linux.py --type all  # Crée des packages .deb, .rpm et AppImage
```

## 📸 Captures d'écran

![Interface principale](docs/screenshots/main_interface.png)
![Sélection de serveur](docs/screenshots/server_selection.png)
![Statistiques de connexion](docs/screenshots/connection_stats.png)

## 🏗️ Architecture

AniData VPN est construit sur une architecture modulaire comprenant:

- **Core**: Le moteur central gérant les protocoles, le réseau et la sécurité
- **Infrastructure**: Gestion de l'infrastructure mondiale de serveurs
- **AI**: Modules d'intelligence artificielle pour l'optimisation des routes et la détection des menaces
- **UI**: Interface utilisateur multiplateforme
- **Scripts**: Utilitaires d'installation, de mise à jour et de diagnostic

## 🛠️ Technologies utilisées

- **Backend**: Python (Scapy, PyRoute2, Paramiko), Rust (performance réseau)
- **IA**: TensorFlow/PyTorch pour l'analyse réseau en temps réel
- **Système**: Bash pour la configuration système (iptables, netfilter, ufw)
- **Frontend**: PyQt/Electron pour l'interface graphique multiplateforme

## 🗺️ Couverture des serveurs

Notre réseau mondial s'étend sur plus de 150 pays, offrant une couverture inégalée:
- Europe: 40+ pays
- Asie: 45+ pays
- Amériques: 35+ pays
- Afrique: 25+ pays
- Océanie: 10+ pays

## 🤝 Contribution

Les contributions sont les bienvenues! Voici comment vous pouvez nous aider:

1. Fork le projet
2. Créez votre branche de fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commitez vos changements (`git commit -m 'Add some amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

Consultez les [problèmes en cours](https://github.com/votre-username/AniData-VPN/issues) pour voir sur quoi nous travaillons.

## 📚 Documentation

La documentation complète est disponible dans le répertoire `docs/`. Pour plus d'informations sur les dernières améliorations, consultez [ENHANCEMENTS.md](docs/ENHANCEMENTS.md).

## 📝 Licence

Propriétaire - Tous droits réservés © 2023-2025-2024

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à [ouvrir un ticket](https://github.com/votre-username/AniData-VPN/issues).

---

*AniData VPN - Votre confidentialité, notre priorité*