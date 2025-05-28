#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Windows Packaging Script
# © 2023-2025-2024 AniData - All Rights Reserved

import os
import sys
import shutil
import subprocess
import platform
import winreg
from pathlib import Path
import ctypes

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import PyInstaller
        print("PyInstaller is installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    try:
        from PIL import Image
        print("Pillow is installed")
    except ImportError:
        print("Installing Pillow...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])

    try:
        import win32serviceutil
        import win32con
        import win32net
        import win32netcon
        import win32com.client
        print("pywin32 is installed")
    except ImportError:
        print("Installing pywin32...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        # Force post-install script to run to register COM components
        print("Running pywin32 post-install script...")
        pywin32_path = os.path.join(sys.prefix, "Scripts", "pywin32_postinstall.py")
        if os.path.exists(pywin32_path):
            subprocess.check_call([sys.executable, pywin32_path, "-install"])

    # Check if running as admin
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("WARNING: This script may require administrator privileges for full functionality")
        print("Some features like VPN network adapter integration might be limited")
        
    inno_setup_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(inno_setup_path):
        print("Inno Setup not found. Attempting to download and install...")
        try:
            # Download and install Inno Setup silently
            inno_url = "https://jrsoftware.org/download.php/is.exe"
            inno_installer = os.path.join(os.environ["TEMP"], "innosetup.exe")
            print("Downloading Inno Setup...")
            import urllib.request
            urllib.request.urlretrieve(inno_url, inno_installer)
            print("Installing Inno Setup silently...")
            subprocess.check_call([inno_installer, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"])
            print("Inno Setup installed successfully")
        except Exception as e:
            print(f"Error installing Inno Setup: {e}")
            print("Please install it manually from https://jrsoftware.org/isinfo.php")
    else:
        print("Inno Setup is installed.")
        
    # Check for TAP-Windows driver
    try:
        import win32com.shell.shell as shell
        print("Checking for TAP-Windows virtual network adapter...")
        result = subprocess.run(["netsh", "interface", "show", "interface", "name=TAP-Windows"], 
                               capture_output=True, text=True)
        if "TAP-Windows" not in result.stdout:
            print("TAP-Windows adapter not found. Will be installed during setup.")
        else:
            print("TAP-Windows adapter is installed.")
    except Exception as e:
        print(f"Could not check TAP-Windows adapter: {e}")

def get_app_info():
    return {
        "name": "AniData VPN",
        "version": "1.0.0",
        "entry_point": "scripts/simple_vpn.py",
        "description": "Ultra-secure next-generation VPN with global coverage",
        "author": "AniData",
        "company": "AniData Inc.",
        "copyright": "© 2023-2025-2024 AniData",
        "guid": "{E8CF1A5F-ECF2-4B70-B017-A0AC6B42A545}",  # Unique app identifier
        "website": "https://anidata-vpn.com",
    }

def get_icon_path():
    project_root = Path(__file__).resolve().parent.parent
    icon_path = project_root / "ui" / "assets" / "icon.ico"
    
    # If .ico doesn't exist, but .png does, convert it
    if not icon_path.exists():
        png_icon = project_root / "ui" / "assets" / "icon.png"
        if png_icon.exists():
            try:
                from PIL import Image
                img = Image.open(png_icon)
                icon_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                print(f"Created ICO file at {icon_path}")
            except Exception as e:
                print(f"Failed to convert PNG to ICO: {e}")
        else:
            # Try to generate icon using the generator script
            icon_script = project_root / "ui" / "assets" / "generate_icon.py"
            if icon_script.exists():
                subprocess.run([sys.executable, str(icon_script)], check=True)
    
    # If we still don't have an icon, create a simple one
    if not icon_path.exists():
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (256, 256), color=(0, 127, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw a simple VPN shield logo
            draw.rectangle((48, 48, 208, 208), fill=(255, 255, 255, 200))
            draw.polygon([(128, 32), (32, 96), (128, 224), (224, 96)], fill=(0, 127, 255, 255))
            
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
            print(f"Created default ICO file at {icon_path}")
        except Exception as e:
            print(f"Failed to create default icon: {e}")
            # Return a dummy path, the packager will use a default icon
            return "icon.ico"
    
    return str(icon_path)

def generate_inno_setup_script(app_info, dist_dir, icon_path):
    app_name = app_info["name"]
    app_version = "1.0.0"
    app_exe = f"{app_name.replace(' ', '')}.exe"
    app_guid = app_info.get("guid", "{E8CF1A5F-ECF2-4B70-B017-A0AC6B42A545}")
    app_website = app_info.get("website", "https://anidata-vpn.com")
    
    # Path to the TAP-Windows driver installer
    tap_installer = os.path.join(dist_dir, "tap-windows.exe")
    
    # Create a tap-windows.exe placeholder if it doesn't exist
    # In a real app, you would include the actual TAP-Windows installer
    if not os.path.exists(tap_installer):
        Path(tap_installer).touch()

    script_content = f"""
[Setup]
AppId={{{app_guid}}}
AppName={app_name}
AppVersion={app_version}
AppPublisher={app_info["company"]}
AppPublisherURL={app_website}
AppSupportURL={app_website}/support
AppUpdatesURL={app_website}/updates
DefaultDirName={{pf}}\\{app_name}
DefaultGroupName={app_name}
OutputDir=dist
OutputBaseFilename={app_name.replace(' ', '')}_{app_version}_Setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
SetupIconFile={icon_path}
UninstallDisplayIcon={{app}}\\{app_exe}
WizardStyle=modern
WizardImageFile={icon_path}
WizardSmallImageFile={icon_path}
PrivilegesRequired=admin
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\\French.isl"

[Files]
Source: "{dist_dir}\\{app_exe}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{dist_dir}\\*.dll"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs
Source: "{dist_dir}\\*.pyd"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs
Source: "{dist_dir}\\*.manifest"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs
Source: "{dist_dir}\\tap-windows.exe"; DestDir: "{{app}}\\drivers"; Flags: ignoreversion
Source: "{dist_dir}\\*"; Excludes: "*.exe,*.dll,*.pyd,*.manifest"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{{group}}\\{app_name}"; Filename: "{{app}}\\{app_exe}"
Name: "{{group}}\\Uninstall {app_name}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{app_name}"; Filename: "{{app}}\\{app_exe}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startmenuicon"; Description: "Create a &Start Menu icon"; GroupDescription: "Additional icons:"; Flags: checkedonce
Name: "startwithwindows"; Description: "Start {app_name} when Windows starts"; GroupDescription: "Windows integration:"; Flags: unchecked

[Registry]
; Add application to installed programs list with detailed info
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{app_guid}}}_is1"; ValueType: string; ValueName: "DisplayIcon"; ValueData: "{{app}}\\{app_exe}"
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{app_guid}}}_is1"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "{app_version}"
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{app_guid}}}_is1"; ValueType: string; ValueName: "Publisher"; ValueData: "{app_info["company"]}"
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{app_guid}}}_is1"; ValueType: string; ValueName: "URLInfoAbout"; ValueData: "{app_website}"
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{{{app_guid}}}_is1"; ValueType: string; ValueName: "HelpLink"; ValueData: "{app_website}/support"

; Register as a VPN provider in Windows
Root: HKLM; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Control Panel\\Cpls"; ValueType: string; ValueName: "{app_name}"; ValueData: "{{app}}\\{app_exe}"; Flags: uninsdeletevalue
Root: HKLM; Subkey: "SYSTEM\\CurrentControlSet\\Services\\RasMan\\Config"; ValueType: dword; ValueName: "{app_name}"; ValueData: "1"; Flags: uninsdeletevalue

; Add to startup if selected
Root: HKCU; Subkey: "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "{app_name}"; ValueData: "{{app}}\\{app_exe} --minimize"; Flags: uninsdeletevalue; Tasks: startwithwindows

[Run]
; Install TAP driver
Filename: "{{app}}\\drivers\\tap-windows.exe"; Description: "Install TAP Virtual Network Driver"; StatusMsg: "Installing virtual network adapter..."; Parameters: "/S"; Flags: runhidden waituntilterminated
; Launch after install
Filename: "{{app}}\\{app_exe}"; Description: "Launch {app_name}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Uninstall TAP driver when uninstalling the app
Filename: "{{app}}\\drivers\\tap-windows.exe"; Parameters: "/S /U"; Flags: runhidden waituntilterminated

[Code]
// Custom code to ensure the VPN appears in Windows network connections
procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Register the VPN with Windows networking
    Exec(ExpandConstant('{{app}}\\{app_exe}'), '--register-vpn', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
"""

    script_path = Path("dist") / "setup_script.iss"
    os.makedirs("dist", exist_ok=True)
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content.strip())
    return str(script_path)

def create_service_stub():
    service_code = r"""
import os
import sys
import json
import time
import logging
import socket
import subprocess
import win32serviceutil
import win32service
import win32event
import win32net
import win32netcon
import servicemanager
import winreg

# Setup logging
log_path = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'AniData VPN', 'logs')
os.makedirs(log_path, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_path, 'vpn_service.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AniDataVPNService(win32serviceutil.ServiceFramework):
    _svc_name_ = "AniDataVPN"
    _svc_display_name_ = "AniData VPN Service"
    _svc_description_ = "Provides secure VPN connection services for AniData VPN client"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        self.logger = logging.getLogger('AniDataVPNService')
        
        # Find installation directory
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{E8CF1A5F-ECF2-4B70-B017-A0AC6B42A545}_is1") as key:
                self.install_dir = winreg.QueryValueEx(key, "InstallLocation")[0]
        except:
            # Default fallback location
            self.install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'AniData VPN')
            
        self.logger.info(f"Service initialized with install dir: {self.install_dir}")

    def SvcStop(self):
        self.logger.info("Stopping service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        
        # Ensure the VPN is disconnected when service stops
        try:
            self.disconnect_vpn()
        except Exception as e:
            self.logger.error(f"Error disconnecting VPN: {e}")

    def SvcDoRun(self):
        self.logger.info("Starting service...")
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ""))
        self.is_running = True
        self.main()

    def register_network_adapter(self):
        try:
            self.logger.info("Registering VPN network adapter...")
            # This would typically involve configuring the TAP-Windows adapter
            # for use with your VPN protocol
            adapter_config = {
                "name": "AniData VPN Adapter",
                "device_type": "TAP-Windows",
            }
            
            # In a real implementation, this would involve configuring the network adapter
            # through WMI or Windows networking APIs
            return True
        except Exception as e:
            self.logger.error(f"Error registering network adapter: {e}")
            return False

    def disconnect_vpn(self):
        """Disconnect the VPN connection"""
        self.logger.info("Disconnecting VPN...")
        # Implementation would depend on the VPN protocol being used
        # This is just a placeholder
        try:
            # For example, if using WireGuard:
            # subprocess.run(["wg-quick", "down", "anidata"], check=True)
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting VPN: {e}")
            return False
    
    def check_vpn_status(self):
        """Check if VPN is connected and working properly"""
        try:
            # This would be replaced with actual VPN status checking logic
            # Perhaps checking if the VPN interface exists and has an IP
            return True
        except Exception as e:
            self.logger.error(f"Error checking VPN status: {e}")
            return False

    def main(self):
        """Main service loop"""
        self.logger.info("Service main loop started")
        
        # Register VPN network adapter on startup
        self.register_network_adapter()
        
        # Main service loop
        check_interval = 30  # seconds
        while self.is_running:
            # Check if we should exit
            if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                break
                
            # Monitor VPN status
            if not self.check_vpn_status():
                self.logger.warning("VPN connection check failed")
                # Could implement auto-reconnect logic here
            
            # Wait for the next interval
            for _ in range(check_interval):
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    self.is_running = False
                    break
                    
        self.logger.info("Service main loop ended")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AniDataVPNService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AniDataVPNService)
"""
    service_path = os.path.join("dist", "vpn_service.py")
    os.makedirs("dist", exist_ok=True)
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(service_code.strip())
    return service_path

def create_vpn_integration_module():
    """Create module for VPN system integration"""
    vpn_integration_code = r"""
import os
import sys
import ctypes
import winreg
import socket
import logging
import subprocess
import json
from pathlib import Path

def is_admin():
    """Check if the script is running with admin privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def register_vpn_with_windows():
    """Register the VPN as a recognized network connection in Windows"""
    if not is_admin():
        logging.error("Admin privileges required to register VPN")
        return False
        
    try:
        # Register as a network provider
        key_path = r"SYSTEM\CurrentControlSet\Control\NetworkProvider\Order"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
            providers = winreg.QueryValueEx(key, "ProviderOrder")[0]
            if "AniDataVPN" not in providers:
                providers = providers + ",AniDataVPN"
                winreg.SetValueEx(key, "ProviderOrder", 0, winreg.REG_SZ, providers)
                
        # Create network provider key
        provider_key = r"SYSTEM\CurrentControlSet\Services\AniDataVPN\NetworkProvider"
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, provider_key, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "Name", 0, winreg.REG_SZ, "AniData VPN")
            winreg.SetValueEx(key, "Class", 0, winreg.REG_DWORD, 2)  # VPN class
            
        # Register with network connections UI
        connection_key = r"SYSTEM\CurrentControlSet\Control\Network\{4D36E972-E325-11CE-BFC1-08002BE10318}"
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, connection_key, 0, winreg.KEY_WRITE) as key:
            pass  # The real implementation would create the necessary structure
            
        return True
    except Exception as e:
        logging.error(f"Error registering VPN with Windows: {e}")
        return False

def install_tap_driver():
    """Install the TAP virtual network adapter driver"""
    if not is_admin():
        logging.error("Admin privileges required to install TAP driver")
        return False
        
    try:
        # Get the path to the TAP installer
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        tap_installer = os.path.join(app_dir, "drivers", "tap-windows.exe")
        
        if not os.path.exists(tap_installer):
            logging.error(f"TAP installer not found at {tap_installer}")
            return False
            
        # Install the TAP driver silently
        subprocess.run([tap_installer, "/S"], check=True)
        return True
    except Exception as e:
        logging.error(f"Error installing TAP driver: {e}")
        return False

def create_vpn_connection(name="AniData VPN", server="auto"):
    """Create a VPN connection in Windows"""
    try:
        # In a real implementation, this would use the Windows networking APIs
        # to create a recognized VPN connection
        
        # For now, we'll just create a settings file
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        connections_dir = os.path.join(os.environ.get('APPDATA', ''), 'AniData VPN', 'Connections')
        os.makedirs(connections_dir, exist_ok=True)
        
        connection = {
            "name": name,
            "server": server,
            "protocol": "wireguard",
            "auto_connect": False,
            "created_at": "2023-04-01T12:00:00Z"
        }
        
        with open(os.path.join(connections_dir, f"{name}.json"), 'w') as f:
            json.dump(connection, f, indent=2)
            
        return True
    except Exception as e:
        logging.error(f"Error creating VPN connection: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--register-vpn":
        if is_admin():
            success = register_vpn_with_windows()
            sys.exit(0 if success else 1)
        else:
            # Re-run the script with admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
    elif len(sys.argv) > 1 and sys.argv[1] == "--install-tap":
        if is_admin():
            success = install_tap_driver()
            sys.exit(0 if success else 1)
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )

def create_windows_installer(dist_dir):
    print("Creating Windows installer...")
    app_info = get_app_info()
    icon_path = get_icon_path()
    script_path = generate_inno_setup_script(app_info, dist_dir, icon_path)

    inno_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(inno_path):
        print("Inno Setup compiler not found. Please install it or check the path.")
        print(f"Inno Setup script generated: {script_path}")
        return

    try:
        subprocess.run([inno_path, script_path], check=True)
        print(f"Installer created: "1.0.0",
    except Exception as e:
        print(f"Error creating installer: {e}")

def main():
    if platform.system() != "Windows":
        print("This packaging script is intended for Windows only.")
        return

    check_requirements()
    app_info = get_app_info()
    icon_path = get_icon_path()
    create_service_stub()
    dist_dir = build_windows_executable(app_info, icon_path)
    print(f"Executable built at: {dist_dir}")
    create_windows_installer(dist_dir)

if __name__ == "__main__":
    main()
