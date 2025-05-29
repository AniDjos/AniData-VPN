# AniData VPN - Core Package
# © 2023-2024 AniData

"""
Package core pour les fonctionnalités principales d'AniData VPN
Ce package fournit les implémentations des différents protocoles et services
"""

from .vpn import WireGuardManager, RealVPNManager

__all__ = ['WireGuardManager', 'RealVPNManager']