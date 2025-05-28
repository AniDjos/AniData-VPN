#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Linux Packaging Script
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import shutil
import subprocess
import platform
import json
import glob
from pathlib import Path
import argparse

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

    # Check for Linux packaging tools
    required_tools = {
        "deb": ["dpkg", "fakeroot", "dh-python"],
        "rpm": ["rpmbuild"],
        "appimage": ["appimagetool"]
    }
    
    distro = get_linux_distro()
    if distro.get("ID") in ["ubuntu", "debian"]:
        install_cmd = ["apt-get", "install", "-y"]
        package_type = "deb"
    elif distro.get("ID") in ["fedora", "centos", "rhel"]:
        install_cmd = ["dnf", "install", "-y"]
        package_type = "rpm"
    else:
        install_cmd = None
        package_type = "appimage"  # Default to AppImage for unknown distros
    
    if install_cmd and package_type in required_tools:
        for tool in required_tools[package_type]:
            if not check_tool_installed(tool):
                print(f"Installing {tool}...")
                cmd = install_cmd + [tool]
                try:
                    subprocess.check_call(cmd)
                except subprocess.CalledProcessError:
                    print(f"Warning: Failed to install {tool}. You may need to install it manually.")

    # Check for AppImage tool in any case (as fallback)
    if not check_tool_installed("appimagetool") and not os.path.exists("./appimagetool"):
        print("AppImageTool not found. Attempting to download...")
        try:
            subprocess.check_call([
                "wget", "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage",
                "-O", "./appimagetool"
            ])
            subprocess.check_call(["chmod", "+x", "./appimagetool"])
        except subprocess.CalledProcessError:
            print("Warning: Failed to download AppImageTool. You may need to install it manually.")

def check_tool_installed(tool_name):
    """Check if a command-line tool is installed"""
    try:
        subprocess.check_call(["which", tool_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def get_linux_distro():
    """Get Linux distribution information"""
    distro_info = {}
    
    if os.path.exists("/etc/os-release"):
        with open("/etc/os-release", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    distro_info[key] = value.strip('"')
    
    return distro_info

def get_app_info():
    return {
        "name": "AniData VPN",
        "package_name": "anidata-vpn",
        "version": "1.0.0",
        "entry_point": "scripts/simple_vpn.py",
        "description": "Ultra-secure next-generation VPN with global coverage",
        "author": "AniData",
        "author_email": "contact@anidata-vpn.com",
        "company": "AniData Inc.",
        "copyright": "© 2023-2024 AniData",
        "website": "https://anidata-vpn.com",
        "license": "Proprietary",
        "categories": ["Network", "Security", "VPN"],
    }

def get_icon_path(size=256):
    """Get or generate app icon"""
    project_root = Path(__file__).resolve().parent.parent.parent
    icon_path = project_root / "ui" / "assets" / "icon.png"
    
    # If we don't have the icon, create it
    if not icon_path.exists():
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (size, size), color=(0, 127, 255, 255))  # Bleu Azur
            draw = ImageDraw.Draw(img)
            
            # Draw a simple VPN shield logo
            draw.rectangle((size//5, size//5, size*4//5, size*4//5), fill=(255, 255, 255, 200))
            draw.polygon([(size//2, size//8), (size//8, size//2), (size//2, size*7//8), (size*7//8, size//2)], 
                         fill=(0, 127, 255, 255))
            
            icon_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(icon_path)
            print(f"Created icon at {icon_path}")
        except Exception as e:
            print(f"Failed to create icon: {e}")
            # Return a dummy path
            return "/tmp/icon.png"
    
    return str(icon_path)

def create_desktop_file(app_info, executable_path):
    """Create a .desktop file for Linux desktop integration"""
    desktop_content = f"""[Desktop Entry]
Name={app_info['name']}
GenericName=VPN Client
Comment={app_info['description']}
Exec={executable_path}
Icon={app_info['package_name']}
Terminal=false
Type=Application
Categories={';'.join(app_info['categories'])};
StartupNotify=true
Keywords=VPN;Security;Privacy;Network;
"""
    desktop_file = f"{app_info['package_name']}.desktop"
    with open(desktop_file, "w") as f:
        f.write(desktop_content)
    return desktop_file

def create_vpn_network_integration():
    """Create scripts for VPN network integration on Linux"""
    # NetworkManager integration
    nm_dispatcher_script = """#!/bin/bash
# AniData VPN Network Manager Integration Script
# Handles network events for VPN integration

export LC_ALL=C

if [ "$2" = "vpn-up" ] || [ "$2" = "vpn-down" ]; then
    logger -t "AniDataVPN" "NetworkManager VPN connection status: $2"
    
    if [ "$2" = "vpn-up" ]; then
        # Update the routing table to ensure traffic goes through VPN
        ip route add default dev "$1" table 200 || true
        ip rule add fwmark 200 table 200 || true
    fi
    
    # Notify the AniData VPN app about VPN status change
    if pgrep -f "AniDataVPN" > /dev/null; then
        # Find the user running the VPN app
        user=$(ps -o user= -p $(pgrep -f "AniDataVPN"))
        if [ -n "$user" ]; then
            su - "$user" -c "dbus-send --session --dest=com.anidata.vpn --type=method_call \
                /com/anidata/vpn com.anidata.vpn.statusUpdate string:$2"
        fi
    fi
fi
"""
    
    os.makedirs("dist/network", exist_ok=True)
    with open("dist/network/nm-dispatcher", "w") as f:
        f.write(nm_dispatcher_script)
    os.chmod("dist/network/nm-dispatcher", 0o755)
    
    # NetworkManager VPN plugin config
    nm_vpn_config = """[VPN Connection]
name=AniData VPN Connection
service=anidata-vpn
program=/usr/lib/anidata-vpn/nm-anidata-service

[VPN Service]
name=AniData VPN
service=anidata-vpn
program=/usr/lib/anidata-vpn/nm-anidata-service

[GNOME]
auth-dialog=/usr/lib/anidata-vpn/nm-anidata-auth-dialog
properties=/usr/lib/anidata-vpn/libnm-anidata-properties
supports-external-ui-mode=true
"""
    
    with open("dist/network/nm-anidata.name", "w") as f:
        f.write(nm_vpn_config)
    
    # Service stub
    service_stub = """#!/bin/bash
# AniData VPN NetworkManager service stub
# This is a placeholder for actual VPN functionality

case "$1" in
    start)
        echo "Starting VPN connection..."
        exit 0
        ;;
    stop)
        echo "Stopping VPN connection..."
        exit 0
        ;;
    status)
        echo "VPN status check..."
        exit 0
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
"""
    
    with open("dist/network/nm-anidata-service", "w") as f:
        f.write(service_stub)
    os.chmod("dist/network/nm-anidata-service", 0o755)
    
    return "dist/network"

def build_linux_executable(app_info, icon_path):
    """Build Linux executable using PyInstaller"""
    entry_point = app_info["entry_point"]
    app_name = app_info["name"].replace(" ", "")
    project_root = Path(__file__).resolve().parent.parent.parent
    
    dist_dir = project_root / "dist"
    build_dir = project_root / "build"
    spec_file = project_root / f"{app_name}.spec"
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if spec_file.exists():
        os.remove(spec_file)
    
    # Ensure entry point is a full path
    entry_point_path = project_root / entry_point
    if not entry_point_path.exists():
        print(f"Error: Entry point {entry_point_path} not found")
        sys.exit(1)
    
    # Create PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--icon={icon_path}",
        f"--name={app_info['package_name']}",
        f"--add-data={project_root}/ui/assets:ui/assets",
        f"--add-data={project_root}/infrastructure:infrastructure",
        str(entry_point_path)
    ]
    
    subprocess.run(cmd, check=True)
    
    # Create a symlink with space in name for better display
    os.symlink(
        f"{app_info['package_name']}", 
        os.path.join("dist", app_info['name'].replace(" ", "\\ "))
    )
    
    return "dist"

def create_deb_package(app_info, executable_path, icon_path):
    """Create a Debian package (.deb)"""
    package_name = app_info["package_name"]
    version = app_info["version"]
    
    # Create directory structure
    deb_root = f"dist/{package_name}-{version}"
    os.makedirs(f"{deb_root}/DEBIAN", exist_ok=True)
    os.makedirs(f"{deb_root}/usr/bin", exist_ok=True)
    os.makedirs(f"{deb_root}/usr/share/applications", exist_ok=True)
    os.makedirs(f"{deb_root}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
    os.makedirs(f"{deb_root}/usr/lib/{package_name}", exist_ok=True)
    os.makedirs(f"{deb_root}/etc/NetworkManager/dispatcher.d", exist_ok=True)
    
    # Copy executable
    shutil.copy2(executable_path, f"{deb_root}/usr/bin/{package_name}")
    os.chmod(f"{deb_root}/usr/bin/{package_name}", 0o755)
    
    # Copy icon
    shutil.copy2(icon_path, f"{deb_root}/usr/share/icons/hicolor/256x256/apps/{package_name}.png")
    
    # Create desktop file
    desktop_file = create_desktop_file(app_info, f"/usr/bin/{package_name}")
    shutil.copy2(desktop_file, f"{deb_root}/usr/share/applications/{package_name}.desktop")
    
    # Create network integration files
    network_files = create_vpn_network_integration()
    for file in glob.glob(f"{network_files}/*"):
        if "nm-dispatcher" in file:
            shutil.copy2(file, f"{deb_root}/etc/NetworkManager/dispatcher.d/99-{package_name}")
            os.chmod(f"{deb_root}/etc/NetworkManager/dispatcher.d/99-{package_name}", 0o755)
        else:
            shutil.copy2(file, f"{deb_root}/usr/lib/{package_name}/{os.path.basename(file)}")
            if os.access(file, os.X_OK):
                os.chmod(f"{deb_root}/usr/lib/{package_name}/{os.path.basename(file)}", 0o755)
    
    # Create control file
    control_content = f"""Package: {package_name}
Version: {version}
Section: net
Priority: optional
Architecture: amd64
Depends: network-manager, python3, libgtk-3-0
Maintainer: {app_info['author']} <{app_info.get('author_email', 'contact@anidata-vpn.com')}>
Description: {app_info['description']}
 AniData VPN is an ultra-secure next-generation VPN with global coverage.
 This VPN offers multi-hop routing, AI-driven security, and access to
 over 150 countries with automatic server rotation.
"""
    
    with open(f"{deb_root}/DEBIAN/control", "w") as f:
        f.write(control_content)
    
    # Create postinst script
    postinst_content = """#!/bin/bash
set -e

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

# Update application database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Reload NetworkManager configuration
if command -v systemctl >/dev/null 2>&1; then
    systemctl reload NetworkManager || true
fi

exit 0
"""
    
    with open(f"{deb_root}/DEBIAN/postinst", "w") as f:
        f.write(postinst_content)
    os.chmod(f"{deb_root}/DEBIAN/postinst", 0o755)
    
    # Create postrm script
    postrm_content = """#!/bin/bash
set -e

if [ "$1" = "remove" ] || [ "$1" = "purge" ]; then
    # Clean up user data if purging
    if [ "$1" = "purge" ]; then
        rm -rf /etc/anidata-vpn
        rm -rf /var/lib/anidata-vpn
    fi
    
    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor
    fi
    
    # Update application database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications
    fi
fi

exit 0
"""
    
    with open(f"{deb_root}/DEBIAN/postrm", "w") as f:
        f.write(postrm_content)
    os.chmod(f"{deb_root}/DEBIAN/postrm", 0o755)
    
    # Build the package
    subprocess.run(["dpkg-deb", "--build", deb_root])
    
    # Move the .deb file to a better location
    deb_file = f"{package_name}-{version}.deb"
    shutil.move(f"dist/{deb_file}", deb_file)
    
    print(f"Created Debian package: {deb_file}")
    return deb_file

def create_rpm_package(app_info, executable_path, icon_path):
    """Create an RPM package"""
    package_name = app_info["package_name"]
    version = app_info["version"]
    
    # Create RPM spec file
    spec_content = f"""Summary: {app_info['description']}
Name: {package_name}
Version: {version}
Release: 1%{{?dist}}
License: {app_info['license']}
URL: {app_info['website']}
BuildArch: x86_64
Requires: NetworkManager, python3, gtk3

%description
AniData VPN is an ultra-secure next-generation VPN with global coverage.
This VPN offers multi-hop routing, AI-driven security, and access to
over 150 countries with automatic server rotation.

%install
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor/256x256/apps
mkdir -p %{{buildroot}}/usr/lib/{package_name}
mkdir -p %{{buildroot}}/etc/NetworkManager/dispatcher.d

# Copy files
cp {executable_path} %{{buildroot}}/usr/bin/{package_name}
chmod 755 %{{buildroot}}/usr/bin/{package_name}

cp {icon_path} %{{buildroot}}/usr/share/icons/hicolor/256x256/apps/{package_name}.png

cat > %{{buildroot}}/usr/share/applications/{package_name}.desktop << EOF
[Desktop Entry]
Name={app_info['name']}
GenericName=VPN Client
Comment={app_info['description']}
Exec=/usr/bin/{package_name}
Icon={package_name}
Terminal=false
Type=Application
Categories={';'.join(app_info['categories'])};
StartupNotify=true
Keywords=VPN;Security;Privacy;Network;
EOF

%files
/usr/bin/{package_name}
/usr/share/applications/{package_name}.desktop
/usr/share/icons/hicolor/256x256/apps/{package_name}.png
/usr/lib/{package_name}
/etc/NetworkManager/dispatcher.d/99-{package_name}

%post
# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor
fi

# Update application database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Reload NetworkManager configuration
if command -v systemctl >/dev/null 2>&1; then
    systemctl reload NetworkManager || true
fi

%postun
if [ "$1" = 0 ]; then
    # Update icon cache
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -f -t /usr/share/icons/hicolor
    fi
    
    # Update application database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications
    fi
fi
"""
    
    with open(f"{package_name}.spec", "w") as f:
        f.write(spec_content)
    
    # Prepare RPM build directories
    for dir in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        os.makedirs(f"rpmbuild/{dir}", exist_ok=True)
    
    # Copy spec file
    shutil.copy2(f"{package_name}.spec", f"rpmbuild/SPECS/{package_name}.spec")
    
    # Build the RPM
    subprocess.run([
        "rpmbuild", "-bb",
        "--define", f"_topdir {os.path.abspath('rpmbuild')}",
        f"rpmbuild/SPECS/{package_name}.spec"
    ])
    
    # Find and copy the RPM
    rpm_files = glob.glob(f"rpmbuild/RPMS/x86_64/{package_name}-{version}*.rpm")
    if rpm_files:
        rpm_file = os.path.basename(rpm_files[0])
        shutil.copy2(rpm_files[0], rpm_file)
        print(f"Created RPM package: {rpm_file}")
        return rpm_file
    else:
        print("Failed to find built RPM package")
        return None

def create_appimage(app_info, executable_path, icon_path):
    """Create an AppImage package"""
    package_name = app_info["package_name"]
    version = app_info["version"]
    
    # Create AppDir structure
    appdir = f"dist/AppDir"
    os.makedirs(f"{appdir}/usr/bin", exist_ok=True)
    os.makedirs(f"{appdir}/usr/share/applications", exist_ok=True)
    os.makedirs(f"{appdir}/usr/share/icons/hicolor/256x256/apps", exist_ok=True)
    os.makedirs(f"{appdir}/usr/lib/{package_name}", exist_ok=True)
    
    # Copy executable
    shutil.copy2(executable_path, f"{appdir}/usr/bin/{package_name}")
    os.chmod(f"{appdir}/usr/bin/{package_name}", 0o755)
    
    # Create AppRun script
    apprun_content = f"""#!/bin/bash
# Get the directory where this AppImage is located
APPDIR="$(dirname "$(readlink -f "$0")")"

# Export environment variables
export PATH="$APPDIR/usr/bin:$PATH"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
export XDG_DATA_DIRS="$APPDIR/usr/share:$XDG_DATA_DIRS"

# Run the app
exec "$APPDIR/usr/bin/{package_name}" "$@"
"""
    
    with open(f"{appdir}/AppRun", "w") as f:
        f.write(apprun_content)
    os.chmod(f"{appdir}/AppRun", 0o755)
    
    # Copy icon
    shutil.copy2(icon_path, f"{appdir}/usr/share/icons/hicolor/256x256/apps/{package_name}.png")
    shutil.copy2(icon_path, f"{appdir}/{package_name}.png")  # Root icon for AppImage
    
    # Create desktop file
    desktop_file = create_desktop_file(app_info, f"/usr/bin/{package_name}")
    shutil.copy2(desktop_file, f"{appdir}/usr/share/applications/{package_name}.desktop")
    shutil.copy2(desktop_file, f"{appdir}/{package_name}.desktop")  # Root desktop file for AppImage
    
    # Create network integration files
    network_files = create_vpn_network_integration()
    for file in glob.glob(f"{network_files}/*"):
        if not "nm-dispatcher" in file:  # Skip system files that need root installation
            shutil.copy2(file, f"{appdir}/usr/lib/{package_name}/{os.path.basename(file)}")
            if os.access(file, os.X_OK):
                os.chmod(f"{appdir}/usr/lib/{package_name}/{os.path.basename(file)}", 0o755)
    
    # Build AppImage
    appimage_name = f"{app_info['name'].replace(' ', '_')}-{version}-x86_64.AppImage"
    
    # Look for appimagetool
    appimagetool = "./appimagetool"
    if not os.path.exists(appimagetool):
        appimagetool = "appimagetool"
    
    subprocess.run([appimagetool, appdir, appimage_name])
    
    os.chmod(appimage_name, 0o755)
    print(f"Created AppImage: {appimage_name}")
    return appimage_name

def create_network_manager_vpn_plugin(app_info):
    """Create additional files for NetworkManager VPN plugin integration"""
    # This would create the necessary files for a full VPN plugin integration
    # For a real implementation, this would involve creating C or Python
    # extensions that implement the NetworkManager VPN plugin API
    
    # For now, we'll just create placeholder files to demonstrate the concept
    nm_plugin_dir = "dist/nm-plugin"
    os.makedirs(nm_plugin_dir, exist_ok=True)
    
    # Create README with instructions
    readme_content = f"""# AniData VPN NetworkManager Plugin

This directory contains files for integrating AniData VPN with NetworkManager.

## Installation

To fully integrate with NetworkManager as a VPN provider:

1. Copy the .name file to /usr/share/NetworkManager/VPN/
2. Copy the service and auth dialog executables to /usr/lib/{app_info['package_name']}/
3. Restart NetworkManager: systemctl restart NetworkManager

## Manual Configuration

If the automatic installation didn't work, you can manually add AniData VPN
to NetworkManager by editing /etc/NetworkManager/system-connections/ and adding
a new connection with the following content:

```
[connection]
id=AniData VPN
uuid=<generate-a-uuid>
type=vpn
autoconnect=false

[vpn]
service-type=anidata-vpn
```

Save this file and restart NetworkManager.
"""
    
    with open(f"{nm_plugin_dir}/README.md", "w") as f:
        f.write(readme_content)
    
    return nm_plugin_dir

def main():
    parser = argparse.ArgumentParser(description="AniData VPN Linux Packaging Tool")
    parser.add_argument("--type", choices=["deb", "rpm", "appimage", "all"], default="all",
                        help="Type of package to build (default: all)")
    args = parser.parse_args()
    
    if platform.system() != "Linux":
        print("This packaging script is intended for Linux only.")
        return
    
    check_requirements()
    app_info = get_app_info()
    icon_path = get_icon_path()
    
    # Create network integration files
    create_network_manager_vpn_plugin(app_info)
    
    # Build executable
    dist_dir = build_linux_executable(app_info, icon_path)
    executable_path = f"{dist_dir}/{app_info['package_name']}"
    print(f"Executable built at: {executable_path}")
    
    # Build packages based on type argument
    if args.type in ["deb", "all"]:
        try:
            create_deb_package(app_info, executable_path, icon_path)
        except Exception as e:
            print(f"Failed to create DEB package: {e}")
    
    if args.type in ["rpm", "all"]:
        try:
            create_rpm_package(app_info, executable_path, icon_path)
        except Exception as e:
            print(f"Failed to create RPM package: {e}")
    
    if args.type in ["appimage", "all"]:
        try:
            create_appimage(app_info, executable_path, icon_path)
        except Exception as e:
            print(f"Failed to create AppImage: {e}")
    
    print("Packaging complete!")

if __name__ == "__main__":
    main()