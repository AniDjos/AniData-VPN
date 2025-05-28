Summary: Ultra-secure next-generation VPN with global coverage
Name: anidata-vpn
Version: 1.0.0
Release: 1%{?dist}
License: Proprietary
URL: https://anidata-vpn.com
BuildArch: x86_64
Requires: NetworkManager, python3, gtk3

%description
AniData VPN is an ultra-secure next-generation VPN with global coverage.
This VPN offers multi-hop routing, AI-driven security, and access to
over 150 countries with automatic server rotation.

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps
mkdir -p %{buildroot}/usr/lib/anidata-vpn
mkdir -p %{buildroot}/etc/NetworkManager/dispatcher.d

# Copy files
cp dist/anidata-vpn %{buildroot}/usr/bin/anidata-vpn
chmod 755 %{buildroot}/usr/bin/anidata-vpn

cp /home/anicet/Documents/VPN_anicet/ui/assets/icon.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/anidata-vpn.png

cat > %{buildroot}/usr/share/applications/anidata-vpn.desktop << EOF
[Desktop Entry]
Name=AniData VPN
GenericName=VPN Client
Comment=Ultra-secure next-generation VPN with global coverage
Exec=/usr/bin/anidata-vpn
Icon=anidata-vpn
Terminal=false
Type=Application
Categories=Network;Security;VPN;
StartupNotify=true
Keywords=VPN;Security;Privacy;Network;
EOF

%files
/usr/bin/anidata-vpn
/usr/share/applications/anidata-vpn.desktop
/usr/share/icons/hicolor/256x256/apps/anidata-vpn.png
/usr/lib/anidata-vpn
/etc/NetworkManager/dispatcher.d/99-anidata-vpn

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
