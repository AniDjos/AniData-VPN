#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Server Configuration Update Script
# © 2023-2024 AniData - All Rights Reserved

import os
import sys
import json
import random
import string
import ipaddress
from pathlib import Path
import argparse

# Constantes pour les régions géographiques
REGIONS = {
    "Europe": [
        {"country": "Albania", "city": "Tirana", "latitude": 41.3275, "longitude": 19.8187},
        {"country": "Andorra", "city": "Andorra la Vella", "latitude": 42.5063, "longitude": 1.5218},
        {"country": "Armenia", "city": "Yerevan", "latitude": 40.1792, "longitude": 44.4991},
        {"country": "Belarus", "city": "Minsk", "latitude": 53.9045, "longitude": 27.5615},
        {"country": "Bosnia and Herzegovina", "city": "Sarajevo", "latitude": 43.8563, "longitude": 18.4131},
        {"country": "Cyprus", "city": "Nicosia", "latitude": 35.1856, "longitude": 33.3823},
        {"country": "Estonia", "city": "Tallinn", "latitude": 59.4370, "longitude": 24.7536},
        {"country": "Georgia", "city": "Tbilisi", "latitude": 41.7151, "longitude": 44.8271},
        {"country": "Iceland", "city": "Reykjavik", "latitude": 64.1466, "longitude": -21.9426},
        {"country": "Latvia", "city": "Riga", "latitude": 56.9496, "longitude": 24.1052},
        {"country": "Liechtenstein", "city": "Vaduz", "latitude": 47.1410, "longitude": 9.5209},
        {"country": "Lithuania", "city": "Vilnius", "latitude": 54.6872, "longitude": 25.2797},
        {"country": "Luxembourg", "city": "Luxembourg City", "latitude": 49.6116, "longitude": 6.1319},
        {"country": "Malta", "city": "Valletta", "latitude": 35.8989, "longitude": 14.5146},
        {"country": "Moldova", "city": "Chisinau", "latitude": 47.0105, "longitude": 28.8638},
        {"country": "Monaco", "city": "Monaco", "latitude": 43.7384, "longitude": 7.4246},
        {"country": "Montenegro", "city": "Podgorica", "latitude": 42.4304, "longitude": 19.2594},
        {"country": "North Macedonia", "city": "Skopje", "latitude": 41.9973, "longitude": 21.4280},
        {"country": "San Marino", "city": "San Marino", "latitude": 43.9424, "longitude": 12.4578},
        {"country": "Slovenia", "city": "Ljubljana", "latitude": 46.0569, "longitude": 14.5058}
    ],
    "Asia": [
        {"country": "Afghanistan", "city": "Kabul", "latitude": 34.5553, "longitude": 69.2075},
        {"country": "Azerbaijan", "city": "Baku", "latitude": 40.4093, "longitude": 49.8671},
        {"country": "Bahrain", "city": "Manama", "latitude": 26.2285, "longitude": 50.5860},
        {"country": "Bangladesh", "city": "Dhaka", "latitude": 23.8103, "longitude": 90.4125},
        {"country": "Bhutan", "city": "Thimphu", "latitude": 27.4728, "longitude": 89.6390},
        {"country": "Brunei", "city": "Bandar Seri Begawan", "latitude": 4.9031, "longitude": 114.9398},
        {"country": "Cambodia", "city": "Phnom Penh", "latitude": 11.5564, "longitude": 104.9282},
        {"country": "China", "city": "Beijing", "latitude": 39.9042, "longitude": 116.4074},
        {"country": "Hong Kong", "city": "Hong Kong", "latitude": 22.3193, "longitude": 114.1694},
        {"country": "India", "city": "New Delhi", "latitude": 28.6139, "longitude": 77.2090},
        {"country": "Indonesia", "city": "Jakarta", "latitude": -6.2088, "longitude": 106.8456},
        {"country": "Iran", "city": "Tehran", "latitude": 35.6892, "longitude": 51.3890},
        {"country": "Iraq", "city": "Baghdad", "latitude": 33.3152, "longitude": 44.3661},
        {"country": "Israel", "city": "Jerusalem", "latitude": 31.7683, "longitude": 35.2137},
        {"country": "Jordan", "city": "Amman", "latitude": 31.9454, "longitude": 35.9284},
        {"country": "Kazakhstan", "city": "Nur-Sultan", "latitude": 51.1694, "longitude": 71.4491},
        {"country": "Kuwait", "city": "Kuwait City", "latitude": 29.3759, "longitude": 47.9774},
        {"country": "Kyrgyzstan", "city": "Bishkek", "latitude": 42.8746, "longitude": 74.5698},
        {"country": "Laos", "city": "Vientiane", "latitude": 17.9757, "longitude": 102.6331},
        {"country": "Lebanon", "city": "Beirut", "latitude": 33.8938, "longitude": 35.5018},
        {"country": "Macau", "city": "Macau", "latitude": 22.1987, "longitude": 113.5439},
        {"country": "Malaysia", "city": "Kuala Lumpur", "latitude": 3.1390, "longitude": 101.6869},
        {"country": "Maldives", "city": "Male", "latitude": 4.1755, "longitude": 73.5093},
        {"country": "Mongolia", "city": "Ulaanbaatar", "latitude": 47.8864, "longitude": 106.9057},
        {"country": "Myanmar", "city": "Naypyidaw", "latitude": 19.7633, "longitude": 96.0785},
        {"country": "Nepal", "city": "Kathmandu", "latitude": 27.7172, "longitude": 85.3240},
        {"country": "North Korea", "city": "Pyongyang", "latitude": 39.0392, "longitude": 125.7625},
        {"country": "Oman", "city": "Muscat", "latitude": 23.5880, "longitude": 58.3829},
        {"country": "Pakistan", "city": "Islamabad", "latitude": 33.6844, "longitude": 73.0479},
        {"country": "Palestine", "city": "Ramallah", "latitude": 31.9038, "longitude": 35.2034},
        {"country": "Philippines", "city": "Manila", "latitude": 14.5995, "longitude": 120.9842},
        {"country": "Qatar", "city": "Doha", "latitude": 25.2854, "longitude": 51.5310},
        {"country": "Saudi Arabia", "city": "Riyadh", "latitude": 24.7136, "longitude": 46.6753},
        {"country": "South Korea", "city": "Seoul", "latitude": 37.5665, "longitude": 126.9780},
        {"country": "Sri Lanka", "city": "Colombo", "latitude": 6.9271, "longitude": 79.8612},
        {"country": "Syria", "city": "Damascus", "latitude": 33.5138, "longitude": 36.2765},
        {"country": "Taiwan", "city": "Taipei", "latitude": 25.0330, "longitude": 121.5654},
        {"country": "Tajikistan", "city": "Dushanbe", "latitude": 38.5598, "longitude": 68.7870},
        {"country": "Thailand", "city": "Bangkok", "latitude": 13.7563, "longitude": 100.5018},
        {"country": "Timor-Leste", "city": "Dili", "latitude": -8.5586, "longitude": 125.5736},
        {"country": "Turkey", "city": "Ankara", "latitude": 39.9334, "longitude": 32.8597},
        {"country": "Turkmenistan", "city": "Ashgabat", "latitude": 37.9601, "longitude": 58.3260},
        {"country": "United Arab Emirates", "city": "Abu Dhabi", "latitude": 24.4539, "longitude": 54.3773},
        {"country": "Uzbekistan", "city": "Tashkent", "latitude": 41.2995, "longitude": 69.2401},
        {"country": "Vietnam", "city": "Hanoi", "latitude": 21.0285, "longitude": 105.8542},
        {"country": "Yemen", "city": "Sanaa", "latitude": 15.3694, "longitude": 44.1910}
    ],
    "Africa": [
        {"country": "Algeria", "city": "Algiers", "latitude": 36.7538, "longitude": 3.0588},
        {"country": "Angola", "city": "Luanda", "latitude": -8.8383, "longitude": 13.2344},
        {"country": "Benin", "city": "Porto-Novo", "latitude": 6.4969, "longitude": 2.6283},
        {"country": "Botswana", "city": "Gaborone", "latitude": -24.6282, "longitude": 25.9231},
        {"country": "Burkina Faso", "city": "Ouagadougou", "latitude": 12.3714, "longitude": -1.5197},
        {"country": "Burundi", "city": "Gitega", "latitude": -3.4271, "longitude": 29.9267},
        {"country": "Cabo Verde", "city": "Praia", "latitude": 14.9333, "longitude": -23.5133},
        {"country": "Cameroon", "city": "Yaoundé", "latitude": 3.8480, "longitude": 11.5021},
        {"country": "Central African Republic", "city": "Bangui", "latitude": 4.3947, "longitude": 18.5582},
        {"country": "Chad", "city": "N'Djamena", "latitude": 12.1348, "longitude": 15.0557},
        {"country": "Comoros", "city": "Moroni", "latitude": -11.7172, "longitude": 43.2473},
        {"country": "Congo", "city": "Brazzaville", "latitude": -4.2634, "longitude": 15.2429},
        {"country": "Côte d'Ivoire", "city": "Yamoussoukro", "latitude": 6.8276, "longitude": -5.2893},
        {"country": "Djibouti", "city": "Djibouti", "latitude": 11.8251, "longitude": 42.5903},
        {"country": "Egypt", "city": "Cairo", "latitude": 30.0444, "longitude": 31.2357},
        {"country": "Equatorial Guinea", "city": "Malabo", "latitude": 3.7504, "longitude": 8.7371},
        {"country": "Eritrea", "city": "Asmara", "latitude": 15.3229, "longitude": 38.9251},
        {"country": "Eswatini", "city": "Mbabane", "latitude": -26.3054, "longitude": 31.1367},
        {"country": "Ethiopia", "city": "Addis Ababa", "latitude": 9.0084, "longitude": 38.7575},
        {"country": "Gabon", "city": "Libreville", "latitude": 0.4162, "longitude": 9.4673},
        {"country": "Gambia", "city": "Banjul", "latitude": 13.4549, "longitude": -16.5790},
        {"country": "Ghana", "city": "Accra", "latitude": 5.6037, "longitude": -0.1870},
        {"country": "Guinea", "city": "Conakry", "latitude": 9.6412, "longitude": -13.5784},
        {"country": "Guinea-Bissau", "city": "Bissau", "latitude": 11.8816, "longitude": -15.6178},
        {"country": "Kenya", "city": "Nairobi", "latitude": -1.2921, "longitude": 36.8219},
        {"country": "Lesotho", "city": "Maseru", "latitude": -29.3142, "longitude": 27.4833},
        {"country": "Liberia", "city": "Monrovia", "latitude": 6.3004, "longitude": -10.7969},
        {"country": "Libya", "city": "Tripoli", "latitude": 32.8872, "longitude": 13.1913},
        {"country": "Madagascar", "city": "Antananarivo", "latitude": -18.8792, "longitude": 47.5079},
        {"country": "Malawi", "city": "Lilongwe", "latitude": -13.9626, "longitude": 33.7741},
        {"country": "Mali", "city": "Bamako", "latitude": 12.6392, "longitude": -8.0029},
        {"country": "Mauritania", "city": "Nouakchott", "latitude": 18.0735, "longitude": -15.9582},
        {"country": "Mauritius", "city": "Port Louis", "latitude": -20.1609, "longitude": 57.5012},
        {"country": "Morocco", "city": "Rabat", "latitude": 33.9716, "longitude": -6.8498},
        {"country": "Mozambique", "city": "Maputo", "latitude": -25.9655, "longitude": 32.5832},
        {"country": "Namibia", "city": "Windhoek", "latitude": -22.5609, "longitude": 17.0658},
        {"country": "Niger", "city": "Niamey", "latitude": 13.5137, "longitude": 2.1098},
        {"country": "Nigeria", "city": "Abuja", "latitude": 9.0765, "longitude": 7.3986},
        {"country": "Rwanda", "city": "Kigali", "latitude": -1.9706, "longitude": 30.1044},
        {"country": "Sao Tome and Principe", "city": "São Tomé", "latitude": 0.3302, "longitude": 6.7333},
        {"country": "Senegal", "city": "Dakar", "latitude": 14.7167, "longitude": -17.4677},
        {"country": "Seychelles", "city": "Victoria", "latitude": -4.6191, "longitude": 55.4513},
        {"country": "Sierra Leone", "city": "Freetown", "latitude": 8.4657, "longitude": -13.2317},
        {"country": "Somalia", "city": "Mogadishu", "latitude": 2.0469, "longitude": 45.3182},
        {"country": "South Sudan", "city": "Juba", "latitude": 4.8594, "longitude": 31.5713},
        {"country": "Sudan", "city": "Khartoum", "latitude": 15.5007, "longitude": 32.5599},
        {"country": "Tanzania", "city": "Dodoma", "latitude": -6.1630, "longitude": 35.7516},
        {"country": "Togo", "city": "Lomé", "latitude": 6.1285, "longitude": 1.2255},
        {"country": "Tunisia", "city": "Tunis", "latitude": 36.8065, "longitude": 10.1815},
        {"country": "Uganda", "city": "Kampala", "latitude": 0.3476, "longitude": 32.5825},
        {"country": "Zambia", "city": "Lusaka", "latitude": -15.3875, "longitude": 28.3228},
        {"country": "Zimbabwe", "city": "Harare", "latitude": -17.8252, "longitude": 31.0335}
    ],
    "North America": [
        {"country": "Antigua and Barbuda", "city": "Saint John's", "latitude": 17.1175, "longitude": -61.8456},
        {"country": "Bahamas", "city": "Nassau", "latitude": 25.0343, "longitude": -77.3963},
        {"country": "Barbados", "city": "Bridgetown", "latitude": 13.1132, "longitude": -59.5988},
        {"country": "Belize", "city": "Belmopan", "latitude": 17.2514, "longitude": -88.7690},
        {"country": "Costa Rica", "city": "San José", "latitude": 9.9281, "longitude": -84.0907},
        {"country": "Cuba", "city": "Havana", "latitude": 23.1136, "longitude": -82.3666},
        {"country": "Dominica", "city": "Roseau", "latitude": 15.3010, "longitude": -61.3881},
        {"country": "Dominican Republic", "city": "Santo Domingo", "latitude": 18.4861, "longitude": -69.9312},
        {"country": "El Salvador", "city": "San Salvador", "latitude": 13.6929, "longitude": -89.2182},
        {"country": "Grenada", "city": "St. George's", "latitude": 12.0564, "longitude": -61.7485},
        {"country": "Guatemala", "city": "Guatemala City", "latitude": 14.6349, "longitude": -90.5069},
        {"country": "Haiti", "city": "Port-au-Prince", "latitude": 18.5944, "longitude": -72.3074},
        {"country": "Honduras", "city": "Tegucigalpa", "latitude": 14.0723, "longitude": -87.1921},
        {"country": "Jamaica", "city": "Kingston", "latitude": 18.0179, "longitude": -76.8099},
        {"country": "Nicaragua", "city": "Managua", "latitude": 12.1149, "longitude": -86.2362},
        {"country": "Panama", "city": "Panama City", "latitude": 8.9943, "longitude": -79.5188},
        {"country": "Saint Kitts and Nevis", "city": "Basseterre", "latitude": 17.3026, "longitude": -62.7177},
        {"country": "Saint Lucia", "city": "Castries", "latitude": 14.0101, "longitude": -60.9875},
        {"country": "Saint Vincent and the Grenadines", "city": "Kingstown", "latitude": 13.1587, "longitude": -61.2248},
        {"country": "Trinidad and Tobago", "city": "Port of Spain", "latitude": 10.6418, "longitude": -61.5199}
    ],
    "Oceania": [
        {"country": "Fiji", "city": "Suva", "latitude": -18.1416, "longitude": 178.4419},
        {"country": "Kiribati", "city": "Tarawa", "latitude": 1.3290, "longitude": 172.9790},
        {"country": "Marshall Islands", "city": "Majuro", "latitude": 7.1164, "longitude": 171.1909},
        {"country": "Micronesia", "city": "Palikir", "latitude": 6.9248, "longitude": 158.1618},
        {"country": "Nauru", "city": "Yaren", "latitude": -0.5477, "longitude": 166.9209},
        {"country": "New Zealand", "city": "Wellington", "latitude": -41.2866, "longitude": 174.7756},
        {"country": "Palau", "city": "Ngerulmud", "latitude": 7.5000, "longitude": 134.6243},
        {"country": "Papua New Guinea", "city": "Port Moresby", "latitude": -9.4438, "longitude": 147.1803},
        {"country": "Samoa", "city": "Apia", "latitude": -13.8506, "longitude": -171.7513},
        {"country": "Solomon Islands", "city": "Honiara", "latitude": -9.4456, "longitude": 159.9728},
        {"country": "Tonga", "city": "Nuku'alofa", "latitude": -21.1394, "longitude": -175.2046},
        {"country": "Tuvalu", "city": "Funafuti", "latitude": -8.5211, "longitude": 179.1961},
        {"country": "Vanuatu", "city": "Port Vila", "latitude": -17.7334, "longitude": 168.3220}
    ],
    "South America": [
        {"country": "Guyana", "city": "Georgetown", "latitude": 6.8013, "longitude": -58.1553},
        {"country": "Suriname", "city": "Paramaribo", "latitude": 5.8520, "longitude": -55.2038}
    ]
}

# Liste des protocoles disponibles
PROTOCOLS = [
    ["wireguard", "openvpn"],
    ["wireguard", "openvpn", "ikev2"],
    ["wireguard", "openvpn", "ikev2", "stealth"]
]

# Niveaux de bande passante par région
BANDWIDTH_RANGES = {
    "Europe": (5000, 10000),
    "North America": (5000, 10000),
    "Asia": (3000, 8000),
    "Oceania": (2000, 5000),
    "South America": (2000, 5000),
    "Africa": (1500, 4000),
}

def generate_random_ip():
    """Génère une adresse IP aléatoire qui semble réaliste"""
    # Éviter les plages privées et réservées
    first_octet = random.choice([5, 23, 31, 37, 45, 51, 63, 64, 65, 72, 80, 85, 86, 89, 93, 94, 95, 104, 107, 
                                 129, 130, 131, 132, 134, 138, 139, 143, 144, 146, 147, 158, 159, 160, 161, 162, 
                                 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 176, 178, 179, 180, 181, 185, 
                                 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 
                                 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217])
    rest = [random.randint(1, 254) for _ in range(3)]
    return f"{first_octet}.{rest[0]}.{rest[1]}.{rest[2]}"

def generate_server_id(country_code):
    """Génère un ID de serveur basé sur le code pays"""
    if not country_code:
        country_code = "".join(random.choices(string.ascii_lowercase, k=2))
    
    # Formater l'ID de serveur: [code-pays]-[nombre aléatoire à 2 chiffres]
    return f"{country_code.lower()}-{random.randint(1, 99):02d}"

def get_country_code(country_name):
    """Obtient un code pays à partir du nom du pays (simplification)"""
    # Cette implémentation est simplifiée - dans une vraie application,
    # vous utiliseriez une bibliothèque ou un dictionnaire complet
    country_codes = {
        "Albania": "al", "Andorra": "ad", "Armenia": "am", "Belarus": "by", "Bosnia and Herzegovina": "ba",
        "Cyprus": "cy", "Estonia": "ee", "Georgia": "ge", "Iceland": "is", "Latvia": "lv",
        "Liechtenstein": "li", "Lithuania": "lt", "Luxembourg": "lu", "Malta": "mt", "Moldova": "md",
        "Monaco": "mc", "Montenegro": "me", "North Macedonia": "mk", "San Marino": "sm", "Slovenia": "si",
        "Afghanistan": "af", "Azerbaijan": "az", "Bahrain": "bh", "Bangladesh": "bd", "Bhutan": "bt",
        "Brunei": "bn", "Cambodia": "kh", "China": "cn", "Hong Kong": "hk", "India": "in",
        "Indonesia": "id", "Iran": "ir", "Iraq": "iq", "Israel": "il", "Jordan": "jo",
        "Kazakhstan": "kz", "Kuwait": "kw", "Kyrgyzstan": "kg", "Laos": "la", "Lebanon": "lb",
        "Macau": "mo", "Malaysia": "my", "Maldives": "mv", "Mongolia": "mn", "Myanmar": "mm",
        "Nepal": "np", "North Korea": "kp", "Oman": "om", "Pakistan": "pk", "Palestine": "ps",
        "Philippines": "ph", "Qatar": "qa", "Saudi Arabia": "sa", "South Korea": "kr", "Sri Lanka": "lk",
        "Syria": "sy", "Taiwan": "tw", "Tajikistan": "tj", "Thailand": "th", "Timor-Leste": "tl",
        "Turkey": "tr", "Turkmenistan": "tm", "United Arab Emirates": "ae", "Uzbekistan": "uz", "Vietnam": "vn",
        "Yemen": "ye", "Algeria": "dz", "Angola": "ao", "Benin": "bj", "Botswana": "bw",
        "Burkina Faso": "bf", "Burundi": "bi", "Cabo Verde": "cv", "Cameroon": "cm", "Central African Republic": "cf",
        "Chad": "td", "Comoros": "km", "Congo": "cg", "Côte d'Ivoire": "ci", "Djibouti": "dj",
        "Egypt": "eg", "Equatorial Guinea": "gq", "Eritrea": "er", "Eswatini": "sz", "Ethiopia": "et",
        "Gabon": "ga", "Gambia": "gm", "Ghana": "gh", "Guinea": "gn", "Guinea-Bissau": "gw",
        "Kenya": "ke", "Lesotho": "ls", "Liberia": "lr", "Libya": "ly", "Madagascar": "mg",
        "Malawi": "mw", "Mali": "ml", "Mauritania": "mr", "Mauritius": "mu", "Morocco": "ma",
        "Mozambique": "mz", "Namibia": "na", "Niger": "ne", "Nigeria": "ng", "Rwanda": "rw",
        "Sao Tome and Principe": "st", "Senegal": "sn", "Seychelles": "sc", "Sierra Leone": "sl", "Somalia": "so",
        "South Sudan": "ss", "Sudan": "sd", "Tanzania": "tz", "Togo": "tg", "Tunisia": "tn",
        "Uganda": "ug", "Zambia": "zm", "Zimbabwe": "zw", "Antigua and Barbuda": "ag", "Bahamas": "bs",
        "Barbados": "bb", "Belize": "bz", "Costa Rica": "cr", "Cuba": "cu", "Dominica": "dm",
        "Dominican Republic": "do", "El Salvador": "sv", "Grenada": "gd", "Guatemala": "gt", "Haiti": "ht",
        "Honduras": "hn", "Jamaica": "jm", "Nicaragua": "ni", "Panama": "pa", "Saint Kitts and Nevis": "kn",
        "Saint Lucia": "lc", "Saint Vincent and the Grenadines": "vc", "Trinidad and Tobago": "tt",
        "Fiji": "fj", "Kiribati": "ki", "Marshall Islands": "mh", "Micronesia": "fm", "Nauru": "nr",
        "New Zealand": "nz", "Palau": "pw", "Papua New Guinea": "pg", "Samoa": "ws", "Solomon Islands": "sb",
        "Tonga": "to", "Tuvalu": "tv", "Vanuatu": "vu", "Guyana": "gy", "Suriname": "sr",
        "Australia": "au", "Brazil": "br", "Canada": "ca", "Chile": "cl", "Colombia": "co",
        "Ecuador": "ec", "France": "fr", "Germany": "de", "Italy": "it", "Japan": "jp",
        "Mexico": "mx", "Netherlands": "nl", "Peru": "pe", "Poland": "pl", "Russia": "ru",
        "Singapore": "sg", "South Africa": "za", "Spain": "es", "Sweden": "se", "Switzerland": "ch",
        "United Kingdom": "uk", "United States": "us", "Uruguay": "uy", "Venezuela": "ve"
    }
    
    return country_codes.get(country_name, "")

def create_server_entry(region, country_data):
    """Crée une entrée pour un serveur VPN"""
    country = country_data["country"]
    city = country_data["city"]
    latitude = country_data["latitude"]
    longitude = country_data["longitude"]
    
    country_code = get_country_code(country)
    server_id = generate_server_id(country_code)
    
    # Attribuer une bande passante selon la région
    min_bw, max_bw = BANDWIDTH_RANGES.get(region, (2000, 6000))
    bandwidth = random.randint(min_bw, max_bw)
    
    # Sélectionner des protocoles aléatoirement
    protocols = random.choice(PROTOCOLS)
    
    # Définir les capacités en fonction de la bande passante
    capabilities = {
        "multi_hop": bandwidth > 5000,
        "obfuscation": random.choice([True, False]),
        "streaming": random.choice([True, True, True, False]),  # 75% de chances d'être True
        "p2p": random.choice([True, False])
    }
    
    # Créer l'entrée du serveur
    server = {
        "id": server_id,
        "region": region,
        "country": country,
        "city": city,
        "ip": generate_random_ip(),
        "protocols": protocols,
        "bandwidth": bandwidth,
        "status": "active",
        "coordinates": {
            "latitude": latitude,
            "longitude": longitude
        },
        "capabilities": capabilities,
        "ssl_certificate": f"certs/{server_id}.crt",
        "private_key": f"keys/{server_id}.key"
    }
    
    return server

def generate_expanded_config(existing_config_path, output_path=None):
    """
    Génère une configuration étendue à partir de la configuration existante
    en ajoutant de nouveaux serveurs pour chaque pays dans REGIONS
    """
    # Charger la configuration existante
    with open(existing_config_path, 'r', encoding='utf-8') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            print("Erreur: Le fichier de configuration n'est pas un JSON valide")
            return None
    
    # Vérifier la structure de la configuration
    if 'servers' not in config:
        print("Erreur: La configuration n'a pas de liste 'servers'")
        return None
        
    # Obtenir les pays déjà présents
    existing_countries = set(server['country'] for server in config['servers'])
    
    # Générer de nouveaux serveurs
    new_servers = []
    
    # Parcourir toutes les régions et pays
    for region, countries in REGIONS.items():
        for country_data in countries:
            if country_data['country'] not in existing_countries:
                server = create_server_entry(region, country_data)
                new_servers.append(server)
                existing_countries.add(country_data['country'])
    
    # Ajouter les nouveaux serveurs à la configuration
    config['servers'].extend(new_servers)
    
    # Mettre à jour les paramètres de rotation
    if 'settings' in config and 'rotation_interval' in config['settings']:
        # Ajuster l'intervalle de rotation en fonction du nombre de serveurs
        num_servers = len(config['servers'])
        if num_servers > 100:
            config['settings']['rotation_interval'] = 1800  # 30 minutes pour beaucoup de serveurs
    
    # Enregistrer la configuration mise à jour
    if output_path is None:
        output_path = existing_config_path.replace('.json', '_expanded.json')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Configuration mise à jour avec {len(new_servers)} nouveaux serveurs VPN")
    print(f"Enregistrée dans: {output_path}")
    
    return output_path

def main():
    """Point d'entrée principal du script"""
    parser = argparse.ArgumentParser(description='Mise à jour de la configuration des serveurs VPN AniData')
    parser.add_argument('--input', '-i', default='../infrastructure/servers/config.json',
                        help='Chemin vers le fichier de configuration existant')
    parser.add_argument('--output', '-o', default=None,
                        help='Chemin de sortie pour la configuration mise à jour (par défaut: [input]_expanded.json)')
    
    args = parser.parse_args()
    
    # Résoudre les chemins relatifs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    input_path = args.input
    if not os.path.isabs(input_path):
        input_path = os.path.join(project_root, input_path)
    
    output_path = args.output
    if output_path and not os.path.isabs(output_path):
        output_path = os.path.join(project_root, output_path)
    
    # Générer la configuration mise à jour
    if os.path.exists(input_path):
        generate_expanded_config(input_path, output_path)
    else:
        print(f"Erreur: Le fichier de configuration '{input_path}' n'existe pas")

if __name__ == "__main__":
    main()