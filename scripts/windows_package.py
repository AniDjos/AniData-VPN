#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Windows Packaging Script (163 Countries Edition)
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import shutil
import subprocess
import platform
import winreg
import json
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

def get_app_info():
    return {
        "name": "AniData VPN",
        "version": "1.0.0",
        "entry_point": "scripts/simple_vpn.py",
        "description": "Ultra-secure next-generation VPN with global coverage of 163 countries",
        "author": "AniData",
        "company": "AniData Inc.",
        "copyright": "© 2023-2024 AniData",
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
    app_version = app_info["version"]
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

def prepare_extended_server_config(project_root):
    """Ensure we have the extended server configuration with 163 countries"""
    print("Preparing extended server configuration with 163 countries...")
    
    config_dir = project_root / "infrastructure" / "servers"
    expanded_config = config_dir / "new_expanded_config.json"
    
    if not expanded_config.exists():
        print("Extended configuration not found, generating it...")
        try:
            # Run the update_servers.py script to generate the extended configuration
            update_script = project_root / "scripts" / "update_servers.py"
            config_file = config_dir / "config.json"
            
            if update_script.exists() and config_file.exists():
                cmd = [
                    sys.executable,
                    str(update_script),
                    "-i", str(config_file),
                    "-o", str(expanded_config)
                ]
                subprocess.run(cmd, check=True)
                print("Extended server configuration generated successfully.")
            else:
                print("Update script or original config not found.")
                # Create a fallback expanded config by modifying the original
                if config_file.exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        
                        # Add a note that this is the extended version
                        if 'settings' in config:
                            config['settings']['extended_version'] = True
                            config['settings']['countries_count'] = len(config.get('servers', []))
                        
                        with open(expanded_config, 'w', encoding='utf-8') as f:
                            json.dump(config, f, indent=2)
                        
                        print(f"Created fallback expanded config at {expanded_config}")
                    except Exception as e:
                        print(f"Error creating fallback config: {e}")
        except Exception as e:
            print(f"Error generating extended configuration: {e}")
    else:
        print("Extended server configuration already exists.")
    
    # Ensure the simple_vpn.py script uses the extended config
    try:
        vpn_script = project_root / "scripts" / "simple_vpn.py"
        if vpn_script.exists():
            with open(vpn_script, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if we need to modify the script
            if 'SERVERS_FILE = os.path.join(HOME_DIR, "servers/config.json")' in content:
                content = content.replace(
                    'SERVERS_FILE = os.path.join(HOME_DIR, "servers/config.json")',
                    'SERVERS_FILE = os.path.join(HOME_DIR, "servers/expanded_config.json")'
                )
                content = content.replace(
                    'self.root.title("AniData VPN")',
                    'self.root.title("AniData VPN - Édition 163 Pays")'
                )
                
                with open(vpn_script, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("Updated simple_vpn.py to use extended configuration.")
    except Exception as e:
        print(f"Error updating VPN script: {e}")

def create_service_stub():
    """Create a Windows service stub for VPN background operation"""
    service_code = """
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
                               r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{E8CF1A5F-ECF2-4B70-B017-A0AC6B42A545}_is1") as key:
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

def build_windows_executable(app_info, icon_path):
    """Build Windows executable using PyInstaller"""
    entry_point = app_info["entry_point"]
    app_name = app_info["name"].replace(" ", "")
    project_root = Path(__file__).resolve().parent.parent

    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / f"{app_name}.spec"

    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if spec_file.exists():
        os.remove(spec_file)

    # Ensure we use the extended server configuration
    prepare_extended_server_config(project_root)

    # Ensure entry point is a full path
    entry_point_path = project_root / entry_point
    if not entry_point_path.exists():
        print(f"Error: Entry point {entry_point_path} not found")
        sys.exit(1)

    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--icon={icon_path}",
        "--name", app_name,
        f"--add-data={project_root}\\ui\\assets;ui/assets",
        f"--add-data={project_root}\\infrastructure;infrastructure",
        str(entry_point_path)
    ]

    subprocess.run(cmd, check=True)

    return dist_dir

def create_windows_installer(dist_dir):
    """Create Windows installer using Inno Setup"""
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
        print(f"Installer created: {app_info['name'].replace(' ', '')}_{app_info['version']}_Setup.exe")
    except Exception as e:
        print(f"Error creating installer: {e}")

def main():
    """Main function for the Windows packaging script"""
    print("AniData VPN - Windows Packaging Script (163 Countries Edition)")
    
    if platform.system() != "Windows":
        print("This packaging script is intended for Windows only.")
        print("However, we'll prepare the files for Windows packaging.")
        
    check_requirements()
    app_info = get_app_info()
    icon_path = get_icon_path()
    create_service_stub()
    
    if platform.system() == "Windows":
        dist_dir = build_windows_executable(app_info, icon_path)
        print(f"Executable built at: {dist_dir}")
        create_windows_installer(dist_dir)
    else:
        # Just prepare the configuration files for Windows
        project_root = Path(__file__).resolve().parent.parent
        prepare_extended_server_config(project_root)
        print("Files prepared for Windows packaging.")
        print("To create the Windows installer, run this script on a Windows machine.")

if __name__ == "__main__":
    main()