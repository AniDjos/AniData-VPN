# AniData VPN - Core VPN Package
# © 2023-2024 AniData

"""
Package core pour les fonctionnalités VPN d'AniData
Ce package fournit les implémentations des différents protocoles VPN supportés.
"""

from .wireguard_manager import WireGuardManager, RealVPNManager

__all__ = ['WireGuardManager', 'RealVPNManager']