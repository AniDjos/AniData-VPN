#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - WireGuard Protocol Implementation
# © 2023 AniData - All Rights Reserved

import os
import sys
import json
import socket
import logging
import subprocess
import ipaddress
import random
import time
import fcntl
import struct
from typing import Dict, List, Tuple, Optional, Union

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('anidata_wireguard')

class WireGuardError(Exception):
    """Base exception for WireGuard-related errors"""
    pass

class WireGuardInterface:
    """
    Class for managing WireGuard interfaces and connections
    """
    
    def __init__(self, 
                 interface_name: str = "anidata0", 
                 config_dir: str = "/opt/anidata/config/wireguard",
                 private_key_path: Optional[str] = None):
        """
        Initialize WireGuard interface manager
        
        Args:
            interface_name: Name of the WireGuard interface
            config_dir: Directory for storing WireGuard configurations
            private_key_path: Path to private key (generated if None)
        """
        self.interface_name = interface_name
        self.config_dir = config_dir
        self.private_key_path = private_key_path or os.path.join(config_dir, "private.key")
        self.public_key = None
        self.remote_endpoint = None
        self.remote_public_key = None
        self.local_ip = None
        self.dns_servers = ["1.1.1.1", "1.0.0.1"]  # Default DNS
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Check if WireGuard is installed
        self._check_wireguard_installed()
        
    def _check_wireguard_installed(self) -> None:
        """Check if WireGuard tools are installed"""
        try:
            subprocess.run(["wg", "--version"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL, 
                           check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            raise WireGuardError("WireGuard tools are not installed. Please install 'wireguard-tools' package.")
    
    def generate_keypair(self) -> Tuple[str, str]:
        """
        Generate WireGuard private and public keys
        
        Returns:
            Tuple of (private_key, public_key)
        """
        logger.info("Generating WireGuard keypair")
        
        # Generate private key
        private_key = subprocess.run(
            ["wg", "genkey"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        # Save private key to file with secure permissions
        os.makedirs(os.path.dirname(self.private_key_path), exist_ok=True)
        with open(self.private_key_path, 'w') as f:
            f.write(private_key)
        os.chmod(self.private_key_path, 0o600)
        
        # Generate public key from private key
        public_key = subprocess.run(
            ["wg", "pubkey"],
            input=private_key,
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        self.public_key = public_key
        return private_key, public_key
    
    def load_keypair(self) -> Tuple[str, str]:
        """
        Load existing keypair or generate a new one if it doesn't exist
        
        Returns:
            Tuple of (private_key, public_key)
        """
        if os.path.exists(self.private_key_path):
            with open(self.private_key_path, 'r') as f:
                private_key = f.read().strip()
                
            # Generate public key from private key
            public_key = subprocess.run(
                ["wg", "pubkey"],
                input=private_key,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            self.public_key = public_key
            logger.info(f"Loaded existing WireGuard keypair")
            return private_key, public_key
        else:
            return self.generate_keypair()
    
    def create_interface(self) -> None:
        """Create and configure the WireGuard interface"""
        logger.info(f"Creating WireGuard interface {self.interface_name}")
        
        try:
            # Check if interface already exists
            result = subprocess.run(
                ["sudo", "ip", "link", "show", self.interface_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            if result.returncode == 0:
                # Interface exists, delete it first
                logger.info(f"Interface {self.interface_name} already exists, recreating")
                subprocess.run(["sudo", "ip", "link", "del", self.interface_name], check=True)
            
            # Create WireGuard interface
            subprocess.run(["sudo", "ip", "link", "add", self.interface_name, "type", "wireguard"], check=True)
            
            # Load private key
            private_key, _ = self.load_keypair()
            
            # Set the private key
            subprocess.run(
                ["sudo", "wg", "set", self.interface_name, "private-key", self.private_key_path],
                check=True
            )
            
            logger.info(f"WireGuard interface {self.interface_name} created successfully")
        except subprocess.SubprocessError as e:
            raise WireGuardError(f"Failed to create WireGuard interface: {str(e)}")
    
    def configure_interface(self, 
                            local_ip: str,
                            mtu: int = 1420) -> None:
        """
        Configure WireGuard interface IP and MTU
        
        Args:
            local_ip: Local IP address with CIDR (e.g., "10.10.10.2/24")
            mtu: MTU value for the interface
        """
        logger.info(f"Configuring WireGuard interface {self.interface_name}")
        self.local_ip = local_ip
        
        try:
            # Set IP address
            subprocess.run(["sudo", "ip", "addr", "add", local_ip, "dev", self.interface_name], check=True)
            
            # Set MTU
            subprocess.run(["sudo", "ip", "link", "set", "mtu", str(mtu), "dev", self.interface_name], check=True)
            
            # Bring interface up
            subprocess.run(["sudo", "ip", "link", "set", "up", "dev", self.interface_name], check=True)
            
            logger.info(f"WireGuard interface {self.interface_name} configured with IP {local_ip}")
        except subprocess.SubprocessError as e:
            raise WireGuardError(f"Failed to configure WireGuard interface: {str(e)}")
    
    def add_peer(self, 
                 public_key: str, 
                 endpoint: str,
                 allowed_ips: str = "0.0.0.0/0",
                 keep_alive: int = 25) -> None:
        """
        Add a WireGuard peer
        
        Args:
            public_key: Public key of the peer
            endpoint: Endpoint in the format of "host:port"
            allowed_ips: Allowed IPs in CIDR format (default: "0.0.0.0/0")
            keep_alive: Persistent keepalive interval in seconds
        """
        logger.info(f"Adding WireGuard peer with endpoint {endpoint}")
        self.remote_endpoint = endpoint
        self.remote_public_key = public_key
        
        try:
            # Add peer configuration
            cmd = [
                "sudo", "wg", "set", self.interface_name,
                "peer", public_key,
                "allowed-ips", allowed_ips,
                "endpoint", endpoint,
                "persistent-keepalive", str(keep_alive)
            ]
            
            subprocess.run(cmd, check=True)
            logger.info(f"Added WireGuard peer {endpoint} successfully")
        except subprocess.SubprocessError as e:
            raise WireGuardError(f"Failed to add WireGuard peer: {str(e)}")
    
    def configure_routing(self, default_route: bool = True) -> None:
        """
        Configure routing for the WireGuard interface
        
        Args:
            default_route: Whether to route all traffic through WireGuard
        """
        logger.info("Configuring routing for WireGuard")
        
        try:
            # Enable IP forwarding
            subprocess.run(["sudo", "sh", "-c", "echo 1 > /proc/sys/net/ipv4/ip_forward"], check=True)
            
            if default_route:
                # Save the current default gateway
                default_gw = subprocess.run(
                    ["sudo", "ip", "route", "show", "default"],
                    capture_output=True,
                    text=True,
                    check=True
                ).stdout.strip()
                
                # Add default route through WireGuard
                subprocess.run(["sudo", "ip", "route", "add", "default", "dev", self.interface_name], check=True)
                
                # Save the original default route to a file for restoration
                with open(os.path.join(self.config_dir, "original_route.txt"), 'w') as f:
                    f.write(default_gw)
                
                logger.info("Set default route through WireGuard")
        except subprocess.SubprocessError as e:
            raise WireGuardError(f"Failed to configure routing: {str(e)}")
    
    def configure_dns(self, dns_servers: List[str] = None) -> None:
        """
        Configure DNS for the WireGuard connection
        
        Args:
            dns_servers: List of DNS server IP addresses
        """
        if dns_servers:
            self.dns_servers = dns_servers
            
        logger.info(f"Configuring DNS servers: {', '.join(self.dns_servers)}")
        
        try:
            # Create a temporary resolv.conf file
            temp_resolv_conf = os.path.join(self.config_dir, "resolv.conf.temp")
            with open(temp_resolv_conf, 'w') as f:
                for dns in self.dns_servers:
                    f.write(f"nameserver {dns}\n")
                f.write("options timeout:2 attempts:3\n")
            
            # Backup original resolv.conf
            if os.path.exists("/etc/resolv.conf") and not os.path.exists("/etc/resolv.conf.anidata.bak"):
                subprocess.run(["sudo", "cp", "/etc/resolv.conf", "/etc/resolv.conf.anidata.bak"], check=True)
            
            # Copy the temporary file to /etc/resolv.conf
            subprocess.run(["sudo", "cp", temp_resolv_conf, "/etc/resolv.conf"], check=True)
            
            logger.info("DNS configuration updated")
        except (subprocess.SubprocessError, IOError) as e:
            raise WireGuardError(f"Failed to configure DNS: {str(e)}")
    
    def restore_dns(self) -> None:
        """Restore original DNS configuration"""
        logger.info("Restoring original DNS configuration")
        
        if os.path.exists("/etc/resolv.conf.anidata.bak"):
            try:
                subprocess.run(["sudo", "mv", "/etc/resolv.conf.anidata.bak", "/etc/resolv.conf"], check=True)
                logger.info("Original DNS configuration restored")
            except subprocess.SubprocessError as e:
                raise WireGuardError(f"Failed to restore DNS configuration: {str(e)}")
    
    def restore_routing(self) -> None:
        """Restore original routing configuration"""
        logger.info("Restoring original routing configuration")
        
        original_route_file = os.path.join(self.config_dir, "original_route.txt")
        if os.path.exists(original_route_file):
            try:
                with open(original_route_file, 'r') as f:
                    original_route = f.read().strip()
                
                # Delete current default route
                subprocess.run(
                    ["sudo", "ip", "route", "del", "default"],
                    stderr=subprocess.DEVNULL,
                    check=False
                )
                
                # Restore original default route
                sudo_cmd = ["sudo"] + original_route.split()
                subprocess.run(sudo_cmd, check=True)
                logger.info("Original routing configuration restored")
            except (subprocess.SubprocessError, IOError) as e:
                raise WireGuardError(f"Failed to restore routing configuration: {str(e)}")
    
    def get_connection_status(self) -> Dict[str, any]:
        """
        Get current connection status
        
        Returns:
            Dictionary with connection information
        """
        try:
            # Get WireGuard status
            wg_output = subprocess.run(
                ["sudo", "wg", "show", self.interface_name],
                capture_output=True,
                text=True,
                check=True
            ).stdout
            
            # Parse the output
            status = {
                "interface": self.interface_name,
                "connected": False,
                "public_key": self.public_key,
                "local_ip": self.local_ip,
                "remote_endpoint": self.remote_endpoint,
                "latest_handshake": None,
                "transfer_rx": 0,
                "transfer_tx": 0,
                "persistent_keepalive": None
            }
            
            # Check for peer information
            if "peer" in wg_output:
                status["connected"] = True
                
                for line in wg_output.splitlines():
                    line = line.strip()
                    if "latest handshake:" in line.lower():
                        status["latest_handshake"] = line.split(":", 1)[1].strip()
                    elif "transfer:" in line.lower():
                        parts = line.split(":", 1)[1].strip().split()
                        status["transfer_rx"] = parts[0] + " " + parts[1]
                        status["transfer_tx"] = parts[2] + " " + parts[3]
                    elif "persistent keepalive:" in line.lower():
                        status["persistent_keepalive"] = line.split(":", 1)[1].strip()
            
            return status
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to get connection status: {str(e)}")
            return {"connected": False, "error": str(e)}
    
    def disconnect(self) -> None:
        """Disconnect from WireGuard VPN and clean up"""
        logger.info(f"Disconnecting from WireGuard VPN")
        
        try:
            # Restore DNS and routing first
            self.restore_dns()
            self.restore_routing()
            
            # Bring down the interface
            subprocess.run(["sudo", "ip", "link", "set", "down", "dev", self.interface_name], check=True)
            
            # Delete the interface
            subprocess.run(["sudo", "ip", "link", "del", self.interface_name], check=True)
            
            logger.info(f"Disconnected from WireGuard VPN successfully")
        except subprocess.SubprocessError as e:
            raise WireGuardError(f"Failed to disconnect from WireGuard VPN: {str(e)}")
    
    def generate_config_file(self, output_path: str = None) -> str:
        """
        Generate WireGuard configuration file
        
        Args:
            output_path: Path to save the configuration file (default: {config_dir}/{interface_name}.conf)
        
        Returns:
            Path to the generated configuration file
        """
        if not output_path:
            output_path = os.path.join(self.config_dir, f"{self.interface_name}.conf")
        
        logger.info(f"Generating WireGuard configuration file at {output_path}")
        
        private_key, _ = self.load_keypair()
        
        config = "[Interface]\n"
        config += f"PrivateKey = {private_key}\n"
        config += f"Address = {self.local_ip}\n"
        config += f"MTU = 1420\n\n"
        
        if self.remote_public_key and self.remote_endpoint:
            config += "[Peer]\n"
            config += f"PublicKey = {self.remote_public_key}\n"
            config += f"Endpoint = {self.remote_endpoint}\n"
            config += "AllowedIPs = 0.0.0.0/0, ::/0\n"
            config += "PersistentKeepalive = 25\n"
        
        with open(output_path, 'w') as f:
            f.write(config)
        
        # Set secure permissions
        os.chmod(output_path, 0o600)
        
        logger.info(f"WireGuard configuration file generated successfully")
        return output_path


class WireGuardManager:
    """
    Manager class for WireGuard connections with server selection functionality
    """
    
    def __init__(self, 
                 config_dir: str = "/opt/anidata/config/wireguard",
                 servers_file: str = "/opt/anidata/infrastructure/servers/config.json"):
        """
        Initialize WireGuard manager
        
        Args:
            config_dir: Directory for storing WireGuard configurations
            servers_file: Path to server configuration file
        """
        self.config_dir = config_dir
        self.servers_file = servers_file
        self.servers = []
        self.current_server = None
        self.interface = None
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load server configuration
        self._load_servers()
    
    def _load_servers(self) -> None:
        """Load server configuration from file"""
        try:
            if os.path.exists(self.servers_file):
                with open(self.servers_file, 'r') as f:
                    data = json.load(f)
                
                # Filter servers supporting WireGuard
                self.servers = [
                    server for server in data.get("servers", [])
                    if "wireguard" in server.get("protocols", [])
                ]
                
                logger.info(f"Loaded {len(self.servers)} WireGuard servers from config")
            else:
                logger.warning(f"Server configuration file not found: {self.servers_file}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load server configuration: {str(e)}")
            self.servers = []
    
    def get_server(self, server_id: str = None) -> Optional[Dict]:
        """
        Get server by ID or select best server if ID not provided
        
        Args:
            server_id: Server ID to select, or None for automatic selection
        
        Returns:
            Selected server configuration or None if not found
        """
        if not self.servers:
            logger.error("No servers available")
            return None
        
        if server_id:
            # Find specific server by ID
            for server in self.servers:
                if server.get("id") == server_id:
                    logger.info(f"Selected server: {server.get('country')}, {server.get('city')}")
                    return server
            
            logger.warning(f"Server with ID {server_id} not found")
            return None
        else:
            # Auto-select best server (simple implementation - random selection)
            # In a real implementation, you would consider latency, load, etc.
            server = random.choice(self.servers)
            logger.info(f"Auto-selected server: {server.get('country')}, {server.get('city')}")
            return server
    
    def connect(self, 
                server_id: str = None, 
                use_default_route: bool = True,
                dns_servers: List[str] = None) -> Dict[str, any]:
        """
        Connect to a WireGuard server
        
        Args:
            server_id: ID of the server to connect to (auto-select if None)
            use_default_route: Whether to route all traffic through the VPN
            dns_servers: List of DNS servers to use
        
        Returns:
            Connection status information
        """
        # Disconnect existing connection if any
        if self.interface:
            try:
                self.disconnect()
            except WireGuardError:
                pass
        
        # Select server
        server = self.get_server(server_id)
        if not server:
            return {"success": False, "error": "No suitable server found"}
        
        self.current_server = server
        
        try:
            # Create WireGuard interface
            self.interface = WireGuardInterface(
                interface_name="anidata0",
                config_dir=self.config_dir
            )
            
            # Create and configure interface
            self.interface.create_interface()
            self.interface.configure_interface(local_ip="10.10.10.2/24")
            
            # Extract endpoint from server config (usually port 51820 for WireGuard)
            server_ip = server.get("ip", "").replace("xx", "1")  # Replace xx with 1 for demo
            endpoint = f"{server_ip}:51820"
            
            # Add peer (server)
            # In a real implementation, you would get the actual public key from the server
            # Here we're generating a placeholder public key
            placeholder_pubkey = subprocess.run(
                ["wg", "genkey"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            placeholder_pubkey = subprocess.run(
                ["wg", "pubkey"],
                input=placeholder_pubkey,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            self.interface.add_peer(
                public_key=placeholder_pubkey,
                endpoint=endpoint,
                allowed_ips="0.0.0.0/0, ::/0",
                keep_alive=25
            )
            
            # Configure routing
            if use_default_route:
                self.interface.configure_routing(default_route=True)
            
            # Configure DNS
            if dns_servers:
                self.interface.configure_dns(dns_servers)
            else:
                self.interface.configure_dns(["1.1.1.1", "1.0.0.1"])
            
            # Generate config file
            config_path = self.interface.generate_config_file()
            
            return {
                "success": True,
                "server": {
                    "id": server.get("id"),
                    "country": server.get("country"),
                    "city": server.get("city")
                },
                "interface": self.interface.interface_name,
                "config_file": config_path,
                "public_key": self.interface.public_key
            }
        except WireGuardError as e:
            logger.error(f"Connection failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def disconnect(self) -> Dict[str, any]:
        """
        Disconnect from WireGuard server
        
        Returns:
            Status of the disconnection
        """
        if not self.interface:
            return {"success": True, "message": "Not connected"}
        
        try:
            self.interface.disconnect()
            self.interface = None
            self.current_server = None
            return {"success": True, "message": "Disconnected successfully"}
        except WireGuardError as e:
            logger.error(f"Disconnection failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current connection status
        
        Returns:
            Status information
        """
        if not self.interface:
            return {"connected": False, "message": "Not connected"}
        
        try:
            interface_status = self.interface.get_connection_status()
            
            return {
                "connected": interface_status.get("connected", False),
                "server": self.current_server,
                "connection_info": interface_status
            }
        except Exception as e:
            logger.error(f"Failed to get status: {str(e)}")
            return {"connected": False, "error": str(e)}


# CLI functions for testing
def main():
    """Main function for CLI testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AniData WireGuard VPN Client")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to VPN")
    connect_parser.add_argument("--server", help="Server ID to connect to")
    
    # Disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect from VPN")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check VPN connection status")
    
    # List servers command
    list_parser = subparsers.add_parser("list", help="List available servers")
    
    args = parser.parse_args()
    
    manager = WireGuardManager()
    
    if args.command == "connect":
        result = manager.connect(server_id=args.server)
        if result.get("success"):
            print(f"Connected to {result['server']['country']}, {result['server']['city']}")
        else:
            print(f"Connection failed: {result.get('error')}")
    
    elif args.command == "disconnect":
        result = manager.disconnect()
        if result.get("success"):
            print("Disconnected successfully")
        else:
            print(f"Disconnection failed: {result.get('error')}")
    
    elif args.command == "status":
        status = manager.get_status()
        if status.get("connected"):
            server = status.get("server", {})
            print(f"Connected to {server.get('country')}, {server.get('city')}")
            
            conn_info = status.get("connection_info", {})
            print(f"  Interface: {conn_info.get('interface')}")
            print(f"  Local IP: {conn_info.get('local_ip')}")
            print(f"  Remote: {conn_info.get('remote_endpoint')}")
            print(f"  Data transfer: RX: {conn_info.get('transfer_rx')}, TX: {conn_info.get('transfer_tx')}")
        else:
            print("Not connected")
    
    elif args.command == "list":
        print("Available servers:")
        for server in manager.servers:
            print(f"  {server['id']}: {server['country']}, {server['city']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()