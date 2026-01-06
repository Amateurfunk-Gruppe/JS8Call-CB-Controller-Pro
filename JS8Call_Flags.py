import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import time
import sys
import os
import subprocess
import socket
import json
import re
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import logging
import configparser
from pathlib import Path

print("CB JS8Call Controller PRO mit PNG-Flaggen wird gestartet...")

# ===== WINDOWS ENCODING FIX =====
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except:
        pass

# ===== SICHERES LOGGING =====
def safe_string(text):
    """Ersetzt Unicode-Zeichen die Probleme verursachen"""
    if not isinstance(text, str):
        text = str(text)
    
    replacements = {
        '✓': '[OK]', '✗': '[ERR]', '⚠': '[WARN]', 'ℹ': '[INFO]',
        '●': '[•]', '➤': '->', '←': '<-', '→': '->',
        '↑': 'UP', '↓': 'DOWN', '…': '...', ''': "'", ''': "'",
        '"': '"', '"': '"', '—': '-', '–': '-'
    }
    
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    
    return text

class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            msg = safe_string(msg)
            stream = self.stream
            stream.write(msg + self.terminator)
            self.flush()
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                msg = self.format(record)
                msg = msg.encode('ascii', 'replace').decode('ascii')
                stream = self.stream
                stream.write(msg + self.terminator)
                self.flush()
            except:
                pass
        except Exception:
            self.handleError(record)

# Logging Setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.handlers.clear()

file_handler = logging.FileHandler('js8call_controller.log', encoding='utf-8')
file_handler.setLevel(logging.INFO)
console_handler = SafeStreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# CB Prefixe (ohne Unicode Flags)
cb_prefixes = {
    1: {"DE": "ITALIEN", "CODE": "IT"},
    2: {"DE": "USA", "CODE": "US"},
    3: {"DE": "BRASILIEN", "CODE": "BR"},
    4: {"DE": "ARGENTINIEN", "CODE": "AR"},
    5: {"DE": "VENEZUELA", "CODE": "VE"},
    6: {"DE": "KOLUMBIEN", "CODE": "CO"},
    7: {"DE": "NIEDERLÄNDISCHE ANTILLEN", "CODE": "AN"},
    8: {"DE": "PERU", "CODE": "PE"},
    9: {"DE": "KANADA", "CODE": "CA"},
    10: {"DE": "MEXIKO", "CODE": "MX"},
    11: {"DE": "PUERTO RICO", "CODE": "PR"},
    12: {"DE": "URUGUAY", "CODE": "UY"},
    13: {"DE": "DEUTSCHLAND", "CODE": "DE"},
    14: {"DE": "FRANKREICH", "CODE": "FR"},
    15: {"DE": "SCHWEIZ", "CODE": "CH"},
    16: {"DE": "BELGIEN", "CODE": "BE"},
    17: {"DE": "HAWAII", "CODE": "HI"},
    18: {"DE": "GRIECHENLAND", "CODE": "GR"},
    19: {"DE": "NIEDERLANDE", "CODE": "NL"},
    20: {"DE": "NORWEGEN", "CODE": "NO"},
    21: {"DE": "SCHWEDEN", "CODE": "SE"},
    22: {"DE": "FRANZÖSISCH-GUIANA", "CODE": "GF"},
    23: {"DE": "JAMAIKA", "CODE": "JM"},
    24: {"DE": "PANAMA", "CODE": "PA"},
    25: {"DE": "JAPAN", "CODE": "JP"},
    26: {"DE": "GROSSBRITANNIEN", "CODE": "GB"},
    27: {"DE": "ISLAND", "CODE": "IS"},
    28: {"DE": "HONDURAS", "CODE": "HN"},
    29: {"DE": "IRLAND", "CODE": "IE"},
    30: {"DE": "SPANIEN", "CODE": "ES"},
    31: {"DE": "PORTUGAL", "CODE": "PT"},
    32: {"DE": "CHILE", "CODE": "CL"},
    33: {"DE": "ALASKA", "CODE": "AK"},
    34: {"DE": "KANARISCHE INSELN", "CODE": "IC"},
    35: {"DE": "ÖSTERREICH", "CODE": "AT"},
    36: {"DE": "SAN MARINO", "CODE": "SM"},
    37: {"DE": "DOMINIKANISCHE REPUBLIK", "CODE": "DO"},
    38: {"DE": "GRÖNLAND", "CODE": "GL"},
    39: {"DE": "ANGOLA", "CODE": "AO"},
    40: {"DE": "LIECHTENSTEIN", "CODE": "LI"},
    41: {"DE": "NEUSEELAND", "CODE": "NZ"},
    42: {"DE": "LIBERIA", "CODE": "LR"},
    43: {"DE": "AUSTRALIEN", "CODE": "AU"},
    44: {"DE": "SÜDAFRIKA", "CODE": "ZA"},
    45: {"DE": "SERBIEN", "CODE": "RS"},
    46: {"DE": "OST-DEUTSCHLAND", "CODE": "DD"},
    47: {"DE": "DÄNEMARK", "CODE": "DK"},
    48: {"DE": "SAUDI-ARABIEN", "CODE": "SA"},
    49: {"DE": "BALEAREN", "CODE": "IB"},
    50: {"DE": "EUROPÄISCHES RUSSLAND", "CODE": "RU"},
    51: {"DE": "ANDORRA", "CODE": "AD"},
    52: {"DE": "FÄRÖER-INSELN", "CODE": "FO"},
    53: {"DE": "EL SALVADOR", "CODE": "SV"},
    54: {"DE": "LUXEMBURG", "CODE": "LU"},
    55: {"DE": "GIBRALTAR", "CODE": "GI"},
    56: {"DE": "FINNLAND", "CODE": "FI"},
    57: {"DE": "INDIEN", "CODE": "IN"},
    58: {"DE": "OST-MALAYSIA", "CODE": "MY"},
    59: {"DE": "DODEKANES", "CODE": "GR"},
    60: {"DE": "HONGKONG", "CODE": "HK"},
    61: {"DE": "ECUADOR", "CODE": "EC"},
    62: {"DE": "GUAM", "CODE": "GU"},
    63: {"DE": "ST. HELENA", "CODE": "SH"},
    64: {"DE": "SENEGAL", "CODE": "SN"},
    65: {"DE": "SIERRA LEONE", "CODE": "SL"},
    66: {"DE": "MAURETANIEN", "CODE": "MR"},
    67: {"DE": "PARAGUAY", "CODE": "PY"},
    68: {"DE": "NORDIRLAND", "CODE": "GB"},
    69: {"DE": "COSTA RICA", "CODE": "CR"},
    70: {"DE": "AMERIKANISCH-SAMOA", "CODE": "AS"},
    71: {"DE": "MIDWAY-INSELN", "CODE": "UM"},
    72: {"DE": "GUATEMALA", "CODE": "GT"},
    73: {"DE": "SURINAME", "CODE": "SR"},
    74: {"DE": "NAMIBIA", "CODE": "NA"},
    75: {"DE": "AZOREN", "CODE": "PT"},
    76: {"DE": "MAROKKO", "CODE": "MA"},
    77: {"DE": "GHANA", "CODE": "GH"},
    78: {"DE": "SAMBIA", "CODE": "ZM"},
    79: {"DE": "PHILIPPINEN", "CODE": "PH"},
    80: {"DE": "BOLIVIEN", "CODE": "BO"},
    81: {"DE": "SAN ANDRÉS", "CODE": "CO"},
    82: {"DE": "GUANTÁNAMO BAY", "CODE": "CU"},
    83: {"DE": "TANSANIA", "CODE": "TZ"},
    84: {"DE": "ELFENBEINKÜSTE", "CODE": "CI"},
    85: {"DE": "SIMBABWE", "CODE": "ZW"},
    86: {"DE": "NEPAL", "CODE": "NP"},
    87: {"DE": "NORD-JEMEN", "CODE": "YE"},
    88: {"DE": "KUBA", "CODE": "CU"},
    89: {"DE": "NIGERIA", "CODE": "NG"},
    90: {"DE": "KRETA", "CODE": "GR"},
    91: {"DE": "INDONESIEN", "CODE": "ID"},
    92: {"DE": "LIBYEN", "CODE": "LY"},
    93: {"DE": "MALTA", "CODE": "MT"},
    94: {"DE": "VAE", "CODE": "AE"},
    95: {"DE": "MONGOLEI", "CODE": "MN"},
    96: {"DE": "TONGA", "CODE": "TO"},
    97: {"DE": "ISRAEL", "CODE": "IL"},
    98: {"DE": "SINGAPUR", "CODE": "SG"},
    99: {"DE": "FIDSCHI", "CODE": "FJ"},
    100: {"DE": "SÜDKOREA", "CODE": "KR"},
    101: {"DE": "PAPUA-NEUGUINEA", "CODE": "PG"},
    102: {"DE": "KUWAIT", "CODE": "KW"},
    103: {"DE": "HAITI", "CODE": "HT"},
    104: {"DE": "KORSIKA", "CODE": "FR"},
    105: {"DE": "BOTSWANA", "CODE": "BW"},
    106: {"DE": "CEUTA & MELILLA", "CODE": "ES"},
    107: {"DE": "MONACO", "CODE": "MC"},
    108: {"DE": "SCHOTTLAND", "CODE": "GB"},
    109: {"DE": "UNGARN", "CODE": "HU"},
    110: {"DE": "ZYPERN", "CODE": "CY"},
    111: {"DE": "JORDANIEN", "CODE": "JO"},
    112: {"DE": "LIBANON", "CODE": "LB"},
    113: {"DE": "WEST-MALAYSIA", "CODE": "MY"},
    114: {"DE": "PAKISTAN", "CODE": "PK"},
    115: {"DE": "KATAR", "CODE": "QA"},
    116: {"DE": "TÜRKEI", "CODE": "TR"},
    117: {"DE": "ÄGYPTEN", "CODE": "EG"},
    118: {"DE": "GAMBIA", "CODE": "GM"},
    119: {"DE": "MADEIRA", "CODE": "PT"},
    120: {"DE": "ANTIGUA & BARBUDA", "CODE": "AG"},
    121: {"DE": "BAHAMAS", "CODE": "BS"},
    122: {"DE": "BARBADOS", "CODE": "BB"},
    123: {"DE": "BERMUDA", "CODE": "BM"},
    124: {"DE": "AMSTERDAM & ST. PAUL", "CODE": "TF"},
    125: {"DE": "KAYMAN-INSELN", "CODE": "KY"},
    126: {"DE": "NICARAGUA", "CODE": "NI"},
    127: {"DE": "JUNGFERNINSELN", "CODE": "VI"},
    128: {"DE": "BRITISCHE JUNGFERNINSELN", "CODE": "VG"},
    129: {"DE": "MACQUARIE-INSEL", "CODE": "AU"},
    130: {"DE": "NORFOLK-INSEL", "CODE": "NF"},
    131: {"DE": "GUYANA", "CODE": "GY"},
    132: {"DE": "MARSHALLINSELN", "CODE": "MH"},
    133: {"DE": "NÖRDLICHE MARIANEN", "CODE": "MP"},
    134: {"DE": "PALAU", "CODE": "PW"},
    135: {"DE": "SALOMONEN", "CODE": "SB"},
    136: {"DE": "MARTINIQUE", "CODE": "MQ"},
    137: {"DE": "INSEL MAN", "CODE": "IM"},
    138: {"DE": "VATIKANSTADT", "CODE": "VA"},
    139: {"DE": "SÜD-JEMEN", "CODE": "YD"},
    140: {"DE": "ANTARKTIS", "CODE": "AQ"},
    141: {"DE": "ST. PIERRE & MIQUELON", "CODE": "PM"},
    142: {"DE": "LESOTHO", "CODE": "LS"},
    143: {"DE": "ST. LUCIA", "CODE": "LC"},
    144: {"DE": "OSTERINSEL", "CODE": "CL"},
    145: {"DE": "GALÁPAGOS-INSELN", "CODE": "EC"},
    146: {"DE": "ALGERIEN", "CODE": "DZ"},
    147: {"DE": "Tunesien", "CODE": "TN"},
    148: {"DE": "ASCENSION", "CODE": "SH"},
    149: {"DE": "LAKKADIVEN", "CODE": "IN"},
    150: {"DE": "BAHRAIN", "CODE": "BH"},
    151: {"DE": "IRAK", "CODE": "IQ"},
    152: {"DE": "MALEDIVEN", "CODE": "MV"},
    153: {"DE": "THAILAND", "CODE": "TH"},
    154: {"DE": "IRAN", "CODE": "IR"},
    155: {"DE": "TAIWAN", "CODE": "TW"},
    156: {"DE": "KAMERUN", "CODE": "CM"},
    157: {"DE": "MONTSERRAT", "CODE": "MS"},
    158: {"DE": "TRINIDAD & TOBAGO", "CODE": "TT"},
    159: {"DE": "SOMALIA", "CODE": "SO"},
    160: {"DE": "SUDAN", "CODE": "SD"},
    161: {"DE": "POLEN", "CODE": "PL"},
    162: {"DE": "KONGO (DR)", "CODE": "CD"},
    163: {"DE": "WALES", "CODE": "GB"},
    164: {"DE": "TOGO", "CODE": "TG"},
    165: {"DE": "SARDINIEN", "CODE": "IT"},
    166: {"DE": "ST. MAARTEN, SABA & ST. EUSTATIUS", "CODE": "BQ"},
    167: {"DE": "JERSEY", "CODE": "JE"},
    168: {"DE": "MAURITIUS", "CODE": "MU"},
    169: {"DE": "GUERNSEY", "CODE": "GG"},
    170: {"DE": "BURKINA FASO", "CODE": "BF"},
    171: {"DE": "SVALBARD", "CODE": "SJ"},
    172: {"DE": "NEUKALEDONIEN", "CODE": "NC"},
    173: {"DE": "RÉUNION", "CODE": "RE"},
    174: {"DE": "UGANDA", "CODE": "UG"},
    175: {"DE": "TSCHAD", "CODE": "TD"},
    176: {"DE": "ZENTRALAFRIKANISCHE REPUBLIK", "CODE": "CF"},
    177: {"DE": "SRI LANKA", "CODE": "LK"},
    178: {"DE": "BULGARIEN", "CODE": "BG"},
    179: {"DE": "TSCHECHOSLOWAKEI", "CODE": "CS"},
    180: {"DE": "OMAN", "CODE": "OM"},
    181: {"DE": "SYRIEN", "CODE": "SY"},
    182: {"DE": "GUINEA", "CODE": "GN"},
    183: {"DE": "BENIN", "CODE": "BJ"},
    184: {"DE": "BURUNDI", "CODE": "BI"},
    185: {"DE": "KOMOREN", "CODE": "KM"},
    186: {"DE": "DSCHIBUTI", "CODE": "DJ"},
    187: {"DE": "KENIA", "CODE": "KE"},
    188: {"DE": "MADAGASKAR", "CODE": "MG"},
    189: {"DE": "MAYOTTE", "CODE": "YT"},
    190: {"DE": "SEYCHELLEN", "CODE": "SC"},
    191: {"DE": "ESWATINI", "CODE": "SZ"},
    192: {"DE": "COCOS-INSELN", "CODE": "CC"},
    193: {"DE": "COCOS-KEELING-INSELN", "CODE": "CX"},
    194: {"DE": "DOMINICA", "CODE": "DM"},
    195: {"DE": "GRENADA", "CODE": "GD"},
    196: {"DE": "GUADELOUPE", "CODE": "GP"},
    197: {"DE": "VANUATU", "CODE": "VU"},
    198: {"DE": "FALKLANDINSELN", "CODE": "FK"},
    199: {"DE": "ÄQUATORIALGUINEA", "CODE": "GQ"},
    200: {"DE": "SHETLANDINSELN", "CODE": "GB"},
    201: {"DE": "FRANZÖSISCH-POLYNESIEN", "CODE": "PF"},
    202: {"DE": "BHUTAN", "CODE": "BT"},
    203: {"DE": "CHINA", "CODE": "CN"},
    204: {"DE": "MOSAMBIK", "CODE": "MZ"},
    205: {"DE": "KAP VERDE", "CODE": "CV"},
    206: {"DE": "ÄTHIOPIEN", "CODE": "ET"},
    207: {"DE": "ST. MARTIN", "CODE": "MF"},
    208: {"DE": "GLORIEUSEN-INSELN", "CODE": "TF"},
    209: {"DE": "JUAN DE NOVA", "CODE": "TF"},
    210: {"DE": "WALLIS & FUTUNA", "CODE": "WF"},
    211: {"DE": "JAN MAYEN", "CODE": "SJ"},
    212: {"DE": "ÅLAND", "CODE": "AX"},
    213: {"DE": "MARKET REEF", "CODE": "FI"},
    214: {"DE": "KONGO (REP)", "CODE": "CG"},
    215: {"DE": "GABUN", "CODE": "GA"},
    216: {"DE": "MALI", "CODE": "ML"},
    217: {"DE": "WEIHNACHTSINSEL", "CODE": "CX"},
    218: {"DE": "BELIZE", "CODE": "BZ"},
    219: {"DE": "ANGUILLA", "CODE": "AI"},
    220: {"DE": "ST. VINCENT", "CODE": "VC"},
    221: {"DE": "SÜDORKNEYINSELN", "CODE": "GS"},
    222: {"DE": "SÜDSANDWICHINSELN", "CODE": "GS"},
    223: {"DE": "WEST-SAMOA", "CODE": "WS"},
    224: {"DE": "WEST-KIRIBATI", "CODE": "KI"},
    225: {"DE": "BRUNEI", "CODE": "BN"},
    226: {"DE": "MALAWI", "CODE": "MW"},
    227: {"DE": "RUANDA", "CODE": "RW"},
    228: {"DE": "CHAGOS-ARCHIPEL", "CODE": "IO"},
    229: {"DE": "HEARD-INSEL", "CODE": "HM"},
    230: {"DE": "MIKRONESIEN", "CODE": "FM"},
    231: {"DE": "ST. PETER & ST. PAUL", "CODE": "BR"},
    232: {"DE": "ARUBA", "CODE": "AW"},
    233: {"DE": "RUMÄNIEN", "CODE": "RO"},
    234: {"DE": "AFGHANISTAN", "CODE": "AF"},
    235: {"DE": "ITU GENF", "CODE": "CH"},
    236: {"DE": "BANGLADESCH", "CODE": "BD"},
    237: {"DE": "MYANMAR", "CODE": "MM"},
    238: {"DE": "KAMBODSCHA", "CODE": "KH"},
    239: {"DE": "LAOS", "CODE": "LA"},
    240: {"DE": "MACAO", "CODE": "MO"},
    241: {"DE": "SPRATLY-INSELN", "CODE": "XS"},
    242: {"DE": "VIETNAM", "CODE": "VN"},
    243: {"DE": "AGALEGA", "CODE": "MU"},
    244: {"DE": "PAGALU-INSELN", "CODE": "GQ"},
    245: {"DE": "NIGER", "CODE": "NE"},
    246: {"DE": "SÃO TOMÉ & PRÍNCIPE", "CODE": "ST"},
    247: {"DE": "NAVASSA-INSEL", "CODE": "UM"},
    248: {"DE": "TURKS- & CAICOSINSELN", "CODE": "TC"},
    249: {"DE": "NÖRDLICHE COOKINSELN", "CODE": "CK"},
    250: {"DE": "SÜDLICHE COOKINSELN", "CODE": "CK"},
    251: {"DE": "ALBANIEN", "CODE": "AL"},
    252: {"DE": "REVILLAGIGEDO", "CODE": "MX"},
    253: {"DE": "ANDAMANEN & NIKOBAREN", "CODE": "IN"},
    254: {"DE": "ATHOS", "CODE": "GR"},
    255: {"DE": "KERGUELEN", "CODE": "TF"},
    256: {"DE": "PRINZ-EDWARD-INSELN", "CODE": "ZA"},
    257: {"DE": "RODRIGUES", "CODE": "MU"},
    258: {"DE": "TRISTAN DA CUNHA", "CODE": "SH"},
    259: {"DE": "TROMELIN", "CODE": "TF"},
    260: {"DE": "BAKER & HOWLAND", "CODE": "UM"},
    261: {"DE": "CHATHAM-INSELN", "CODE": "NZ"},
    262: {"DE": "JOHNSTON-INSEL", "CODE": "UM"},
    263: {"DE": "KERMADEC-INSELN", "CODE": "NZ"},
    264: {"DE": "KINGMAN-RIFF", "CODE": "UM"},
    265: {"DE": "ZENTRAL-KIRIBATI", "CODE": "KI"},
    266: {"DE": "OST-KIRIBATI", "CODE": "KI"},
    267: {"DE": "KURE-INSEL", "CODE": "UM"},
    268: {"DE": "LORD-HOWE-INSEL", "CODE": "AU"},
    269: {"DE": "MELLISH-RIFF", "CODE": "AU"},
    270: {"DE": "MINAMITORI-SHIMA", "CODE": "JP"},
    271: {"DE": "NAURU", "CODE": "NR"},
    272: {"DE": "NIUE", "CODE": "NU"},
    273: {"DE": "JARVIS & PALMYRA", "CODE": "UM"},
    274: {"DE": "PITCAIRNINSELN", "CODE": "PN"},
    275: {"DE": "TOKELAU", "CODE": "TK"},
    276: {"DE": "TUVALU", "CODE": "TV"},
    277: {"DE": "SABLE-INSEL", "CODE": "CA"},
    278: {"DE": "WAKE-INSEL", "CODE": "UM"},
    279: {"DE": "WILLIS-INSELN", "CODE": "AU"},
    280: {"DE": "AVES-INSEL", "CODE": "VE"},
    281: {"DE": "OGASAWARA-INSELN", "CODE": "JP"},
    282: {"DE": "AUCKLAND & CAMPBELL", "CODE": "NZ"},
    283: {"DE": "ST. KITTS & NEVIS", "CODE": "KN"},
    284: {"DE": "ST. PAUL-INSEL", "CODE": "CA"},
    285: {"DE": "FERNANDO DE NORONHA", "CODE": "BR"},
    286: {"DE": "JUAN FERNÁNDEZ-INSELN", "CODE": "CL"},
    287: {"DE": "MALPELO", "CODE": "CO"},
    288: {"DE": "SAN FÉLIX", "CODE": "CL"},
    289: {"DE": "SÜDGEORGIEN", "CODE": "GS"},
    290: {"DE": "TRINDADE & MARTIM VAZ", "CODE": "BR"},
    291: {"DE": "DHEKELIA & AKROTIRI", "CODE": "GB"},
    292: {"DE": "ABU AIL-INSEL", "CODE": "YE"},
    293: {"DE": "GUINEA-BISSAU", "CODE": "GW"},
    294: {"DE": "PETER-I.-INSEL", "CODE": "AQ"},
    295: {"DE": "SÜDSUDAN", "CODE": "SS"},
    296: {"DE": "CLIPPERTON-INSEL", "CODE": "FR"},
    297: {"DE": "BOUVETINSEL", "CODE": "BV"},
    298: {"DE": "CROZET-INSELN", "CODE": "TF"},
    299: {"DE": "DESECHEO", "CODE": "PR"},
    300: {"DE": "WESTSAHARA", "CODE": "EH"},
    301: {"DE": "ARMENIEN", "CODE": "AM"},
    302: {"DE": "ASIATISCHES RUSSLAND", "CODE": "RU"},
    303: {"DE": "ASERBAIDSCHAN", "CODE": "AZ"},
    304: {"DE": "ESTLAND", "CODE": "EE"},
    305: {"DE": "FRANZ-JOSEF-LAND", "CODE": "RU"},
    306: {"DE": "GEORGIEN", "CODE": "GE"},
    307: {"DE": "KALININGRAD", "CODE": "RU"},
    308: {"DE": "KASACHSTAN", "CODE": "KZ"},
    309: {"DE": "KIRGISISTAN", "CODE": "KG"},
    310: {"DE": "LETTLAND", "CODE": "LV"},
    311: {"DE": "LITAUEN", "CODE": "LT"},
    312: {"DE": "MOLDAWIEN", "CODE": "MD"},
    313: {"DE": "TADSCHIKISTAN", "CODE": "TJ"},
    314: {"DE": "TURKMENISTAN", "CODE": "TM"},
    315: {"DE": "UKRAINE", "CODE": "UA"},
    316: {"DE": "USBEKISTAN", "CODE": "UZ"},
    317: {"DE": "WEISSRUSSLAND", "CODE": "BY"},
    318: {"DE": "S.M.O.M.", "CODE": "SM"},
    319: {"DE": "UNO NEW YORK", "CODE": "UN"},
    320: {"DE": "BANABA", "CODE": "KI"},
    321: {"DE": "CONWAY REEF", "CODE": "FJ"},
    322: {"DE": "WALVIS BAY", "CODE": "NA"},
    323: {"DE": "JEMEN", "CODE": "YE"},
    324: {"DE": "PINGUININSEL", "CODE": "AQ"},
    325: {"DE": "ROTUMA", "CODE": "FJ"},
    326: {"DE": "MALYJ VYSOTSKIJ", "CODE": "RU"},
    327: {"DE": "SLOWENIEN", "CODE": "SI"},
    328: {"DE": "KROATIEN", "CODE": "HR"},
    329: {"DE": "TSCHECHIEN", "CODE": "CZ"},
    330: {"DE": "SLOWAKEI", "CODE": "SK"},
    331: {"DE": "BOSNIEN-HERZEGOWINA", "CODE": "BA"},
    332: {"DE": "NORDPAZIFIK", "CODE": "MP"},
    333: {"DE": "ERITREA", "CODE": "ER"},
    334: {"DE": "NORDKOREA", "CODE": "KP"},
    335: {"DE": "SCARBOROUGH RIFF", "CODE": "PH"},
    336: {"DE": "PRATAS-INSELN", "CODE": "TW"},
    337: {"DE": "AUSTRAL-INSELN", "CODE": "PF"},
    338: {"DE": "MARQUESAS", "CODE": "PF"},
    339: {"DE": "TEMOTU", "CODE": "SB"},
    340: {"DE": "PALÄSTINA", "CODE": "PS"},
    341: {"DE": "OSTTIMOR", "CODE": "TL"},
    342: {"DE": "CHESTERFIELD-INSELN", "CODE": "NC"},
    343: {"DE": "DUCIE", "CODE": "PN"},
    344: {"DE": "MONTENEGRO", "CODE": "ME"},
    345: {"DE": "SWAINS-INSEL", "CODE": "AS"},
    346: {"DE": "ST. BARTHÉLEMY", "CODE": "BL"},
    347: {"DE": "CURAÇAO", "CODE": "CW"},
    348: {"DE": "SINT MAARTEN", "CODE": "SX"},
    349: {"DE": "SABA & ST. EUSTATIUS", "CODE": "BQ"},
    350: {"DE": "BONAIRE", "CODE": "BQ"},
    351: {"DE": "SÜDSUDAN", "CODE": "SS"},
    352: {"DE": "KOSOVO", "CODE": "XK"}
}

class FlagManager:
    """Verwaltet PNG-Flaggen mit Caching"""
    
    def __init__(self, flags_dir='flags', size=(24, 16)):
        self.flags_dir = Path(flags_dir)
        self.size = size
        self.flag_cache = {}  # Cache für geladene Flaggen
        self.default_flag = None
        
        self.load_flags()
    
    def load_flags(self):
        """Lädt alle PNG-Flaggen in den Cache"""
        if not self.flags_dir.exists():
            logger.warning(f"[WARN] Flaggen-Ordner nicht gefunden: {self.flags_dir}")
            return
        
        # Standard-Flagge (unbekannt)
        unknown_path = self.flags_dir / "unknown.png"
        if unknown_path.exists():
            self.default_flag = self._load_flag_image(unknown_path)
        else:
            # Erstelle leere Standard-Flagge
            self.default_flag = self._create_empty_flag()
        
        # Lade alle Länder-Flaggen
        loaded_count = 0
        for png_file in self.flags_dir.glob("*.png"):
            country_code = png_file.stem.upper()
            if country_code != "UNKNOWN":
                try:
                    self.flag_cache[country_code] = self._load_flag_image(png_file)
                    loaded_count += 1
                except Exception as e:
                    logger.error(f"[ERR] Fehler beim Laden von {png_file}: {e}")
        
        logger.info(f"[OK] {loaded_count} PNG-Flaggen geladen aus {self.flags_dir}")
    
    def _load_flag_image(self, path):
        """Lädt ein einzelnes PNG und skaliert es"""
        try:
            img = Image.open(path)
            img = img.resize(self.size, Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            logger.error(f"[ERR] Fehler beim Laden von {path}: {e}")
            return self._create_empty_flag()
    
    def _create_empty_flag(self):
        """Erstellt eine leere Platzhalter-Flagge"""
        img = Image.new('RGB', self.size, color='gray')
        return ImageTk.PhotoImage(img)
    
    def get_flag(self, country_code):
        """Gibt PhotoImage für Ländercode zurück"""
        if not country_code:
            return self.default_flag
        
        country_code = country_code.upper()
        return self.flag_cache.get(country_code, self.default_flag)
    
    def has_flag(self, country_code):
        """Prüft ob Flagge verfügbar ist"""
        return country_code.upper() in self.flag_cache

class ModernWindowsInput:
    """Moderne Windows API für Eingaben"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        
    def press_enter(self):
        """Sendet Enter-Taste"""
        try:
            class KEYBDINPUT(ctypes.Structure):
                _fields_ = [
                    ("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                ]
            
            class INPUT_UNION(ctypes.Union):
                _fields_ = [
                    ("ki", KEYBDINPUT),
                    ("mi", ctypes.c_ulong * 8),
                    ("hi", ctypes.c_ulong * 8)
                ]
            
            class INPUT(ctypes.Structure):
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("union", INPUT_UNION)
                ]
            
            INPUT_KEYBOARD = 1
            KEYEVENTF_KEYDOWN = 0x0000
            KEYEVENTF_KEYUP = 0x0002
            VK_RETURN = 0x0D
            
            extra = ctypes.c_ulong(0)
            
            ii_down = INPUT()
            ii_down.type = INPUT_KEYBOARD
            ii_down.union.ki = KEYBDINPUT(VK_RETURN, 0, KEYEVENTF_KEYDOWN, 0, ctypes.pointer(extra))
            
            ii_up = INPUT()
            ii_up.type = INPUT_KEYBOARD
            ii_up.union.ki = KEYBDINPUT(VK_RETURN, 0, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
            
            inputs = (INPUT * 2)(ii_down, ii_up)
            result = self.user32.SendInput(2, ctypes.pointer(inputs), ctypes.sizeof(INPUT))
            
            if result == 2:
                logger.info("[OK] Enter-Taste gesendet")
                return True
            else:
                return self.press_enter_fallback()
                
        except Exception as e:
            logger.error(f"[ERR] SendInput Fehler: {e}")
            return self.press_enter_fallback()
    
    def press_enter_fallback(self):
        """Fallback auf keybd_event"""
        try:
            self.user32.keybd_event(0x0D, 0, 0, 0)
            time.sleep(0.05)
            self.user32.keybd_event(0x0D, 0, 0x0002, 0)
            logger.info("[OK] Enter-Taste mit Fallback gesendet")
            return True
        except Exception as e:
            logger.error(f"[ERR] Fallback Fehler: {e}")
            return False

class ConfigManager:
    """Verwaltet Konfigurationseinstellungen"""
    
    def __init__(self, config_file='js8call_controller.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.defaults = {
            'STATION': {
                'callsign': '13FB006',
                'grid': 'JN59'
            },
            'PATHS': {
                'js8call': r'C:\Program Files\JS8Call\js8call.exe',
                'log_dir': 'logs',
                'flags_dir': 'flags'
            },
            'SETTINGS': {
                'host': '127.0.0.1',
                'port': '2442',
                'auto_log': 'False',
                'flag_mode': 'png',  # Standard auf PNG
                'auto_cq_interval': '600',
                'auto_heartbeat_interval': '900'
            }
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                self.config.read(self.config_file, encoding='utf-8')
                logger.info(f"Konfiguration geladen: {self.config_file}")
            except Exception as e:
                logger.error(f"[ERR] Konfigurationsfehler: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        self.config.read_dict(self.defaults)
        self.save_config()
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            logger.info(f"Konfiguration gespeichert: {self.config_file}")
        except Exception as e:
            logger.error(f"[ERR] Speichern fehlgeschlagen: {e}")
    
    def get(self, section, key, default=None):
        try:
            return self.config.get(section, key)
        except:
            return default
    
    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))

class Validator:
    """Validiert verschiedene Eingaben"""
    
    @staticmethod
    def validate_callsign(callsign):
        if not callsign or not isinstance(callsign, str):
            return False
        callsign = callsign.strip().upper()
        pattern = r'^[0-9]+[A-Z]+[0-9]*[A-Z]*$'
        return bool(re.match(pattern, callsign))
    
    @staticmethod
    def validate_grid(grid):
        if not grid or not isinstance(grid, str):
            return False
        grid = grid.strip().upper()
        pattern = r'^[A-R]{2}[0-9]{2}([A-X]{2})?$'
        return bool(re.match(pattern, grid))
    
    @staticmethod
    def validate_frequency(freq):
        try:
            freq = float(freq)
            return 1.0 <= freq <= 999999999.0
        except:
            return False
    
    @staticmethod
    def validate_snr(snr):
        try:
            snr = float(snr)
            return -50.0 <= snr <= 50.0
        except:
            return False

class JS8CallTCPConnection:
    """TCP-basierte Verbindung zu JS8Call"""
    
    def __init__(self, config):
        self.socket = None
        self.connected = False
        self.host = config.get('SETTINGS', 'host')
        self.port = int(config.get('SETTINGS', 'port'))
        self.buffer = ""
        self.auto_enter = ModernWindowsInput()
        self.last_send_time = 0
        self.min_send_interval = 2.0
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10.0)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(1.0)
            self.connected = True
            logger.info(f"[OK] TCP Verbindung zu JS8Call hergestellt ({self.host}:{self.port})")
            return True
        except socket.timeout:
            logger.error("[ERR] Verbindungstimeout")
            return False
        except ConnectionRefusedError:
            logger.error("[ERR] Verbindung abgelehnt")
            return False
        except Exception as e:
            logger.error(f"[ERR] TCP Verbindungsfehler: {e}")
            return False
    
    def _send_json(self, message):
        try:
            current_time = time.time()
            if current_time - self.last_send_time < self.min_send_interval:
                wait_time = self.min_send_interval - (current_time - self.last_send_time)
                time.sleep(wait_time)
            
            json_str = json.dumps(message) + '\n'
            logger.debug(f"SENDING: {json_str.strip()}")
            self.socket.send(json_str.encode('utf-8'))
            self.last_send_time = time.time()
            return True
        except Exception as e:
            logger.error(f"[ERR] Sendefehler: {e}")
            return False
    
    def get_messages(self):
        if not self.connected or not self.socket:
            return []
            
        messages = []
        try:
            self.socket.settimeout(0.1)
            data = self.socket.recv(4096)
            if data:
                try:
                    chunk = data.decode('utf-8', errors='replace')
                except:
                    chunk = data.decode('latin-1', errors='replace')
                
                self.buffer += chunk
                
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        try:
                            message = json.loads(line)
                            messages.append(message)
                        except json.JSONDecodeError as e:
                            logger.warning(f"[WARN] JSON Parse Fehler: {e}")
                            continue
        except socket.timeout:
            pass
        except socket.error as e:
            logger.error(f"[ERR] Socket Fehler: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"[ERR] Empfangsfehler: {e}")
            
        return messages
    
    def send_message_with_auto_enter(self, text):
        if not self.connected or not self.socket:
            logger.error("[ERR] Nicht verbunden")
            return False
            
        try:
            set_text_msg = {"type": "TX.SET_TEXT", "value": text}
            
            if not self._send_json(set_text_msg):
                return False
            
            logger.info("[OK] Text in JS8Call gesetzt")
            time.sleep(1.0)
            
            enter_success = self.auto_enter.press_enter()
            
            if enter_success:
                logger.info("[OK] Auto-Enter erfolgreich")
                return True
            else:
                logger.warning("[WARN] Auto-Enter fehlgeschlagen")
                return False
                
        except Exception as e:
            logger.error(f"[ERR] Sendefehler: {e}")
            return False
    
    def disconnect(self):
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        logger.info("[OK] Verbindung getrennt")

class JS8CallApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JS8Call CB Controller PRO")
        self.root.geometry("1000x800")
        self.root.configure(bg='#2b2b2b')
        
        # Konfiguration laden
        self.config = ConfigManager()
        
        # WICHTIG: Flag Manager initialisieren
        flags_dir = self.config.get('PATHS', 'flags_dir', 'flags')
        self.flag_manager = FlagManager(flags_dir=flags_dir, size=(24, 16))
        
        # Fonts
        self.default_font = ("Segoe UI", 9)
        
        # Verbindung
        self.js8 = JS8CallTCPConnection(self.config)
        self.connected = False
        
        # Station Settings
        self.my_call = self.config.get('STATION', 'callsign')
        self.my_grid = self.config.get('STATION', 'grid')
        
        # Bot System
        self.bot_enabled = False
        self.auto_cq_enabled = False
        self.auto_heartbeat_enabled = False
        self.eqsl_conversations = {}
        self.last_bot_response_time = {}
        self.bot_response_interval = 10.0
        
        # Settings
        self.manual_mode = False
        self.auto_log_enabled = bool(self.config.get('SETTINGS', 'auto_log', 'False'))
        self.flag_display_mode = self.config.get('SETTINGS', 'flag_mode', 'png')
        
        # Connection
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        
        # UI Variables
        self.stations_expanded = True
        self.messages_expanded = False
        
        self.setup_ui()
        self.update_ui_from_config()
        self.check_js8call_installation()
    
    def setup_ui(self):
        # Hauptlayout
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg='#2b2b2b', sashwidth=5)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Linke Seite
        left_frame = tk.Frame(main_paned, bg='#2b2b2b')
        main_paned.add(left_frame, width=300)
        
        # Rechte Seite
        right_paned = tk.PanedWindow(main_paned, orient=tk.VERTICAL, bg='#2b2b2b', sashwidth=5)
        main_paned.add(right_paned, width=700)
        
        # Settings Frame (Links)
        settings_frame = tk.LabelFrame(left_frame, text="EINSTELLUNGEN", 
                                      fg="#fffff4", bg="#2b2b2b",
                                      font=(self.default_font[0], 10, "bold"))
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Station Settings
        station_frame = tk.LabelFrame(settings_frame, text="STATION", 
                                     fg="#fffff4", bg="#2b2b2b",
                                     font=self.default_font)
        station_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(station_frame, text="Callsign:", 
                fg="white", bg="#2b2b2b", font=self.default_font).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.callsign_var = tk.StringVar(value=self.my_call)
        tk.Entry(station_frame, textvariable=self.callsign_var,
                bg="#444444", fg="white", width=15, font=self.default_font).grid(row=0, column=1, padx=5, pady=2)
        
        tk.Label(station_frame, text="Grid Locator:", 
                fg="white", bg="#2b2b2b", font=self.default_font).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.grid_var = tk.StringVar(value=self.my_grid)
        tk.Entry(station_frame, textvariable=self.grid_var,
                bg="#444444", fg="white", width=15, font=self.default_font).grid(row=1, column=1, padx=5, pady=2)
        
        tk.Button(station_frame, text="Speichern", 
                 command=self.save_station_settings,
                 bg="#555555", fg="white", width=12, font=self.default_font).grid(row=2, column=0, columnspan=2, pady=5)
        
        # Pfadeinstellungen
        path_frame = tk.LabelFrame(settings_frame, text="PFADE", 
                                  fg="#fffff4", bg="#2b2b2b",
                                  font=self.default_font)
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(path_frame, text="JS8Call Pfad:", 
                fg="white", bg="#2b2b2b", font=self.default_font).pack(anchor=tk.W, padx=5, pady=2)
        path_btn_frame = tk.Frame(path_frame, bg="#2b2b2b")
        path_btn_frame.pack(fill=tk.X, padx=5, pady=2)
        
        self.js8call_path_var = tk.StringVar(value=self.config.get('PATHS', 'js8call'))
        tk.Entry(path_btn_frame, textvariable=self.js8call_path_var,
                bg="#444444", fg="white", width=25, font=self.default_font).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(path_btn_frame, text="...", 
                 command=self.browse_js8call_path,
                 bg="#555555", fg="white", width=3, font=self.default_font).pack(side=tk.LEFT)
        
        # Control Buttons
        control_frame = tk.LabelFrame(settings_frame, text="KONTROLLE", 
                                     fg="#fffff4", bg="#2b2b2b",
                                     font=self.default_font)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        buttons = [
            ("START JS8CALL", self.start_js8call),
            ("CONNECT", self.connect_js8call),
            ("DISCONNECT", self.disconnect_js8call),
            ("SEND CQ", self.send_cq),
            ("TEST ENTER", self.test_auto_enter),
            ("MANUAL MODE", self.toggle_manual_mode),
            ("FLAG MODE", self.toggle_flag_mode)
        ]
        
        for i, (text, command) in enumerate(buttons):
            tk.Button(control_frame, text=text, command=command,
                     bg="#444444", fg="white", height=2, font=self.default_font).grid(
                row=i//2, column=i%2, padx=5, pady=3, sticky=tk.NSEW)
        
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        
        # Auto-Log Option
        log_frame = tk.Frame(settings_frame, bg="#2b2b2b")
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.auto_log_var = tk.BooleanVar(value=self.auto_log_enabled)
        tk.Checkbutton(log_frame, 
                      text="Automatischer Log",
                      variable=self.auto_log_var,
                      command=self.toggle_auto_log,
                      fg="white", bg="#2b2b2b",
                      selectcolor="#444444",
                      font=self.default_font).pack(anchor=tk.W, padx=5)
        
        # Status
        status_frame = tk.LabelFrame(settings_frame, text="STATUS", 
                                    fg="#fffff4", bg="#2b2b2b",
                                    font=self.default_font)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.connection_status = tk.Label(status_frame, 
                                         text="● DISCONNECTED",
                                         fg="red", bg="#2b2b2b",
                                         font=(self.default_font[0], 10, "bold"))
        self.connection_status.pack(pady=5)
        
        self.mode_status = tk.Label(status_frame,
                                   text="Mode: Auto-Enter",
                                   fg="yellow", bg="#2b2b2b",
                                   font=self.default_font)
        self.mode_status.pack()
        
        # ===== RECHTE SEITE: STATIONS & MESSAGES =====
        
        # Stations Frame
        self.stations_container = tk.Frame(right_paned, bg='#2b2b2b')
        right_paned.add(self.stations_container, height=400)
        
        stations_header = tk.Frame(self.stations_container, bg='#2b2b2b')
        stations_header.pack(fill=tk.X)
        
        tk.Label(stations_header, text="AKTIVE STATIONEN", 
                fg="#fffff4", bg="#2b2b2b",
                font=(self.default_font[0], 10, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.toggle_stations_btn = tk.Button(stations_header, text="▼",
                                           command=self.toggle_stations,
                                           bg="#444444", fg="white",
                                           width=2, font=self.default_font)
        self.toggle_stations_btn.pack(side=tk.RIGHT, padx=5)
        
        self.stations_content = tk.Frame(self.stations_container, bg='#2b2b2b')
        self.stations_content.pack(fill=tk.BOTH, expand=True)
        
        # Treeview für Stationen mit Bild-Support
        self.stations_tree = ttk.Treeview(self.stations_content, 
                                         columns=('Callsign', 'Country', 'SNR', 'Time'),
                                         show='tree headings',
                                         height=12)
        
        # Style
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       rowheight=24,  # Höhe für Flaggen
                       font=self.default_font)
        style.configure("Treeview.Heading",
                       background="#444444",
                       foreground="white",
                       font=(self.default_font[0], 9, "bold"))
        
        # Spaltenbreiten - erstes Element ist das Bild
        self.stations_tree.column('#0', width=30, stretch=False)
        self.stations_tree.heading('#0', text='')
        
        # Andere Spalten
        column_widths = {'Callsign': 100, 'Country': 120, 'SNR': 60, 'Time': 80}
        columns = ['Callsign', 'Country', 'SNR', 'Time']
        
        for i, col in enumerate(columns):
            self.stations_tree.heading(col, text=col)
            self.stations_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.stations_content, 
                                 orient=tk.VERTICAL, 
                                 command=self.stations_tree.yview)
        self.stations_tree.configure(yscrollcommand=scrollbar.set)
        
        self.stations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Messages Frame
        self.messages_container = tk.Frame(right_paned, bg='#2b2b2b')
        right_paned.add(self.messages_container, height=300)
        
        messages_header = tk.Frame(self.messages_container, bg='#2b2b2b')
        messages_header.pack(fill=tk.X)
        
        tk.Label(messages_header, text="NACHRICHTEN", 
                fg="#fffff4", bg="#2b2b2b",
                font=(self.default_font[0], 10, "bold")).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.toggle_messages_btn = tk.Button(messages_header, text="▲",
                                           command=self.toggle_messages,
                                           bg="#444444", fg="white",
                                           width=2, font=self.default_font)
        self.toggle_messages_btn.pack(side=tk.RIGHT, padx=5)
        
        self.messages_content = tk.Frame(self.messages_container, bg='#2b2b2b')
        self.messages_content.pack(fill=tk.BOTH, expand=True)
        
        self.message_text = scrolledtext.ScrolledText(self.messages_content, 
                                                     height=8,
                                                     bg="#2b2b2b",
                                                     fg="white",
                                                     font=self.default_font)
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Tags
        self.message_text.tag_configure("incoming", foreground="#ff00ff")
        self.message_text.tag_configure("outgoing", foreground="#00ff00")
        self.message_text.tag_configure("system", foreground="#ffffff")
        self.message_text.tag_configure("error", foreground="#ff0000")
        self.message_text.tag_configure("success", foreground="#00ff00")
        self.message_text.tag_configure("autoenter", foreground="#ff9900")
        self.message_text.tag_configure("bot", foreground="#ff69b4")
        self.message_text.tag_configure("heartbeat", foreground="#ffa500")
        
        # Bot Control Frame
        bot_frame = tk.LabelFrame(right_paned, text="BOT KONTROLLE", 
                                 fg="#fffff4", bg="#2b2b2b",
                                 font=(self.default_font[0], 9, "bold"))
        right_paned.add(bot_frame, height=100)
        
        # Checkbuttons nebeneinander
        check_frame = tk.Frame(bot_frame, bg="#2b2b2b")
        check_frame.pack(fill=tk.X, pady=5)
        
        self.bot_var = tk.BooleanVar()
        tk.Checkbutton(check_frame, 
                      text="Auto-Respond Bot",
                      variable=self.bot_var,
                      command=self.toggle_bot,
                      fg="white", bg="#2b2b2b",
                      selectcolor="#444444",
                      font=self.default_font).pack(side=tk.LEFT, padx=15)
        
        self.cq_var = tk.BooleanVar()
        tk.Checkbutton(check_frame, 
                      text="Auto-CQ (10min)",
                      variable=self.cq_var,
                      command=self.toggle_auto_cq,
                      fg="white", bg="#2b2b2b",
                      selectcolor="#444444",
                      font=self.default_font).pack(side=tk.LEFT, padx=15)
        
        self.heartbeat_var = tk.BooleanVar()
        tk.Checkbutton(check_frame, 
                      text="Auto-Heartbeat (15min)",
                      variable=self.heartbeat_var,
                      command=self.toggle_auto_heartbeat,
                      fg="white", bg="#2b2b2b",
                      selectcolor="#444444",
                      font=self.default_font).pack(side=tk.LEFT, padx=15)
        
        # Bot Status
        self.bot_status_label = tk.Label(bot_frame,
                                       text="Bot Status: Bereit",
                                       font=self.default_font,
                                       fg="#00ff00", bg="#2b2b2b")
        self.bot_status_label.pack(pady=5)
    
    def toggle_stations(self):
        """Klappt Stationsliste ein/aus"""
        if self.stations_expanded:
            self.stations_content.pack_forget()
            self.toggle_stations_btn.config(text="►")
            self.stations_expanded = False
        else:
            self.stations_content.pack(fill=tk.BOTH, expand=True)
            self.toggle_stations_btn.config(text="▼")
            self.stations_expanded = True
    
    def toggle_messages(self):
        """Klappt Nachrichten ein/aus"""
        if self.messages_expanded:
            self.messages_content.pack_forget()
            self.toggle_messages_btn.config(text="▼")
            self.messages_expanded = False
        else:
            self.messages_content.pack(fill=tk.BOTH, expand=True)
            self.toggle_messages_btn.config(text="▲")
            self.messages_expanded = True
    
    def update_ui_from_config(self):
        """Aktualisiert UI von Konfiguration"""
        self.callsign_var.set(self.my_call)
        self.grid_var.set(self.my_grid)
        self.js8call_path_var.set(self.config.get('PATHS', 'js8call'))
        self.auto_log_var.set(self.auto_log_enabled)
        
        # Update Titel
        self.root.title(f"JS8Call CB Controller PRO - {self.my_call} - {self.my_grid}")
        
    def save_station_settings(self):
        """Speichert Stationseinstellungen"""
        new_call = self.callsign_var.get().strip().upper()
        new_grid = self.grid_var.get().strip().upper()
        
        # Validierung
        if not Validator.validate_callsign(new_call):
            messagebox.showerror("Fehler", "Ungültiges Callsign!")
            return
        
        self.my_call = new_call
        self.my_grid = new_grid
        
        # In Konfiguration speichern
        self.config.set('STATION', 'callsign', self.my_call)
        self.config.set('STATION', 'grid', self.my_grid)
        self.config.save_config()
        
        self.log_message(f"Station gespeichert: {self.my_call} @ {self.my_grid}", "success")
        
    def browse_js8call_path(self):
        """Öffnet Dateidialog für JS8Call Pfad"""
        path = filedialog.askopenfilename(
            title="Wähle JS8Call.exe",
            filetypes=[("Executable", "*.exe"), ("Alle Dateien", "*.*")]
        )
        if path:
            self.js8call_path_var.set(path)
            self.config.set('PATHS', 'js8call', path)
            self.config.save_config()
    
    def toggle_auto_log(self):
        """Schaltet automatischen Log ein/aus"""
        self.auto_log_enabled = self.auto_log_var.get()
        self.config.set('SETTINGS', 'auto_log', str(self.auto_log_enabled))
        self.config.save_config()
        
        status = "aktiviert" if self.auto_log_enabled else "deaktiviert"
        self.log_message(f"Auto-Log {status}", "system")
    
    def check_js8call_installation(self):
        """Überprüft JS8Call Installation"""
        js8_path = self.js8call_path_var.get()
        
        if os.path.exists(js8_path):
            self.log_message(f"[OK] JS8Call gefunden: {js8_path}", "success")
        else:
            self.log_message(f"[ERR] JS8Call nicht gefunden: {js8_path}", "error")
            self.log_message("Bitte Pfad in den Einstellungen korrigieren", "system")
        
        self.log_message(f"[OK] {len(cb_prefixes)} CB Länder geladen", "success")
    
    def start_js8call(self):
        """Startet JS8Call"""
        js8_path = self.js8call_path_var.get()
        
        if not os.path.exists(js8_path):
            self.log_message("[ERR] JS8Call Pfad existiert nicht", "error")
            return
        
        try:
            self.log_message("Starte JS8Call...", "system")
            subprocess.Popen([js8_path])
            self.log_message("[OK] JS8Call wurde gestartet", "success")
            self.log_message("Warte 15 Sekunden bis JS8Call geladen ist...", "system")
            self.root.after(15000, self.connect_js8call)
        except Exception as e:
            self.log_message(f"[ERR] Fehler beim Starten: {e}", "error")
    
    def connect_js8call(self):
        """Stellt Verbindung zu JS8Call her"""
        if self.connection_attempts >= self.max_connection_attempts:
            self.log_message("[ERR] Maximale Verbindungsversuche erreicht", "error")
            self.show_connection_help()
            return
        
        self.connection_attempts += 1
        
        if self.connected:
            self.log_message("Bereits verbunden", "system")
            return
        
        self.log_message(f"Verbindungsversuch {self.connection_attempts}/{self.max_connection_attempts}...", "system")
        
        def connect_thread():
            if self.js8.connect():
                self.connected = True
                self.connection_attempts = 0
                
                self.root.after(0, lambda: self.connection_status.config(
                    text="● CONNECTED", fg="green"))
                self.root.after(0, lambda: self.log_message(
                    "[OK] TCP Verbindung zu JS8Call hergestellt!", "success"))
                self.root.after(0, lambda: self.log_message(
                    f"[OK] Bereit für CB Band 27.245 MHz als {self.my_call}", "success"))
                
                threading.Thread(target=self.message_listener, daemon=True).start()
                
                if self.cq_var.get():
                    threading.Thread(target=self.auto_cq_loop, daemon=True).start()
                
                if self.heartbeat_var.get():
                    threading.Thread(target=self.auto_heartbeat_loop, daemon=True).start()
                    
            else:
                self.root.after(0, lambda: self.log_message(
                    f"[ERR] Verbindung fehlgeschlagen (Versuch {self.connection_attempts})", "error"))
                
                if self.connection_attempts < self.max_connection_attempts:
                    retry_delay = 5 * self.connection_attempts
                    self.root.after(0, lambda: self.log_message(
                        f"[INFO] Nächster Versuch in {retry_delay} Sekunden...", "system"))
                    self.root.after(retry_delay * 1000, self.connect_js8call)
                else:
                    self.root.after(0, self.show_connection_help)
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def show_connection_help(self):
        """Zeigt Verbindungshilfe an"""
        help_text = """
=== JS8Call Verbindungsproblem - Lösungen ===

1. JS8Call muss gestartet sein
2. API muss aktiviert sein in JS8Call:
   - Settings → Advanced → TCP Server Protocol
   - Port: 2442
   - Allow TCP Server Connections: AKTIVIERT
   - Allow TCP Server Control: AKTIVIERT

3. Firewall-Einstellungen prüfen
4. JS8Call manuell starten und dann CONNECT drücken
5. Alternativ Port in Einstellungen prüfen

=== TROUBLESHOOTING ===
- JS8Call neu starten
- App als Administrator ausführen
- Port in JS8Call ändern (2443) und hier anpassen
"""
        self.log_message(help_text, "system")
    
    def disconnect_js8call(self):
        """Trennt Verbindung zu JS8Call"""
        self.connected = False
        self.js8.disconnect()
        
        self.connection_status.config(text="● DISCONNECTED", fg="red")
        self.log_message("[OK] Verbindung zu JS8Call getrennt", "system")
    
    def send_cq(self):
        """Sendet CQ Aufruf"""
        if not self.connected:
            self.log_message("[ERR] Nicht verbunden", "error")
            return
        
        cq_message = f"@ALLCALL CQ CQ CQ {self.my_call} {self.my_call} {self.my_grid} K"
        
        if self.manual_mode:
            if self.send_js8_text_only(cq_message):
                self.log_message("[OK] CQ Text gesetzt (Manual Mode) - ENTER manuell drücken", "system")
        else:
            if self.js8.send_message_with_auto_enter(cq_message):
                self.log_message("[OK] CQ Aufruf gesendet - AUTO-ENTER aktiv!", "autoenter")
    
    def send_js8_text_only(self, message):
        """Sendet nur Text ohne Auto-Enter"""
        try:
            if not message or not message.strip():
                return False
            
            set_text_msg = {
                "type": "TX.SET_TEXT",
                "value": message
            }
            
            if self.js8._send_json(set_text_msg):
                self.log_message(f"[OK] TEXT GESETZT (Manual): {message[:50]}...", "system")
                return True
            return False
        except Exception as e:
            self.log_message(f"[ERR] Fehler beim Text setzen: {e}", "error")
            return False
    
    def test_auto_enter(self):
        """Testet Auto-Enter Funktion"""
        if not self.connected:
            self.log_message("[ERR] Nicht verbunden", "error")
            return
        
        test_message = f"TEST AUTO ENTER FROM {self.my_call}"
        
        if self.manual_mode:
            if self.send_js8_text_only(test_message):
                self.log_message("[OK] Text gesetzt (Manual Mode) - manuell ENTER drücken", "system")
        else:
            if self.js8.send_message_with_auto_enter(test_message):
                self.log_message("[OK] Auto-Enter Test gestartet!", "autoenter")
    
    def toggle_manual_mode(self):
        """Schaltet zwischen Manual und Auto-Enter Mode"""
        self.manual_mode = not self.manual_mode
        
        if self.manual_mode:
            self.mode_status.config(text="Mode: Manual (ENTER manuell)", fg="orange")
            self.log_message("[OK] Manual Mode aktiviert - Enter manuell drücken", "system")
        else:
            self.mode_status.config(text="Mode: Auto-Enter", fg="yellow")
            self.log_message("[OK] Auto-Enter Mode aktiviert", "success")
    
    def toggle_flag_mode(self):
        """Wechselt Flaggen-Anzeigemodus"""
        modes = ['png', 'unicode', 'code', 'text']  # PNG als erstes
        current_index = modes.index(self.flag_display_mode) if self.flag_display_mode in modes else 0
        next_index = (current_index + 1) % len(modes)
        self.flag_display_mode = modes[next_index]
        
        self.config.set('SETTINGS', 'flag_mode', self.flag_display_mode)
        self.config.save_config()
        
        mode_names = {
            'png': 'PNG-Bilder', 
            'unicode': 'Unicode', 
            'code': 'Länderkürzel', 
            'text': 'Text'
        }
        current_mode = mode_names[self.flag_display_mode]
        self.log_message(f"Flaggen-Modus: {current_mode}", "system")
        
        self.refresh_station_list()
    
    def refresh_station_list(self):
        """Aktualisiert alle Stationen im Treeview"""
        items = self.stations_tree.get_children()
        
        for item in items:
            values = self.stations_tree.item(item)['values']
            if values:
                callsign = values[0]
                snr = values[2] if len(values) > 2 else 0
                
                self.update_station_in_treeview(item, callsign, snr)
    
    def update_station_in_treeview(self, item, callsign, snr):
        """Aktualisiert eine einzelne Station im Treeview"""
        cb_number = self.extract_cb_number(callsign)
        
        if cb_number is None:
            country_info = {"DE": "UNBEKANNT", "CODE": "??"}
        else:
            country_info = cb_prefixes.get(cb_number, 
                                          {"DE": "UNBEKANNT", "CODE": "??"})
        
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        # PNG-Flagge
        if self.flag_display_mode == 'png':
            country_code = country_info.get("CODE", "")
            flag_image = self.flag_manager.get_flag(country_code)
            self.stations_tree.item(item, image=flag_image)
            self.stations_tree.item(item, values=(
                callsign, country_info["DE"], snr, utc_time
            ))
        else:
            # Andere Modi
            flag_display = self.get_flag_display(country_info)
            self.stations_tree.item(item, image='')  # Kein Bild
            self.stations_tree.item(item, values=(
                callsign, country_info["DE"], snr, utc_time
            ))
    
    def get_flag_display(self, country_info):
        """Gibt Flagge im gewählten Anzeigemodus zurück"""
        if self.flag_display_mode == 'unicode':
            # Unicode Flaggen - kannst du später hinzufügen wenn gewünscht
            return ""
        elif self.flag_display_mode == 'code':
            return country_info.get("CODE", "??")
        elif self.flag_display_mode == 'text':
            name = country_info.get("DE", "UNBEKANNT")
            if len(name) > 8:
                return name[:8] + "."
            return name
        return ""
    
    def toggle_bot(self):
        """Aktiviert/Deaktiviert Auto-Bot"""
        self.bot_enabled = self.bot_var.get()
        
        if self.bot_enabled:
            self.bot_status_label.config(text="Bot Status: Aktiv", fg="#00ff00")
            self.log_message("Auto-Bot aktiviert", "bot")
        else:
            self.bot_status_label.config(text="Bot Status: Inaktiv", fg="red")
            self.log_message("Auto-Bot deaktiviert", "system")
    
    def toggle_auto_cq(self):
        """Aktiviert/Deaktiviert Auto-CQ"""
        self.auto_cq_enabled = self.cq_var.get()
        
        if self.auto_cq_enabled and self.connected:
            self.log_message("Auto-CQ aktiviert (alle 10 Minuten)", "system")
            threading.Thread(target=self.auto_cq_loop, daemon=True).start()
        else:
            self.log_message("Auto-CQ deaktiviert", "system")
    
    def toggle_auto_heartbeat(self):
        """Aktiviert/Deaktiviert Auto-Heartbeat"""
        self.auto_heartbeat_enabled = self.heartbeat_var.get()
        
        if self.auto_heartbeat_enabled and self.connected:
            self.log_message("Auto-Heartbeat aktiviert (alle 15 Minuten)", "system")
            threading.Thread(target=self.auto_heartbeat_loop, daemon=True).start()
        else:
            self.log_message("Auto-Heartbeat deaktiviert", "system")
    
    def message_listener(self):
        """Hört auf Nachrichten von JS8Call"""
        while self.connected:
            try:
                messages = self.js8.get_messages()
                for msg in messages:
                    self.process_js8call_message(msg)
                time.sleep(0.2)
            except Exception as e:
                self.log_message(f"[ERR] Listener Fehler: {e}", "error")
                time.sleep(2)
    
    def process_js8call_message(self, message):
        """Verarbeitet JS8Call Nachrichten"""
        try:
            if isinstance(message, dict):
                mtype = message.get('type', '')
                params = message.get('params', {})
                value = message.get('value', '')
                
                if mtype.startswith('RX.') or 'CALLSIGN' in params or 'callsign' in params:
                    callsign = params.get('CALLSIGN', '') or params.get('callsign', '')
                    grid = params.get('GRID', '') or params.get('grid', '')
                    
                    snr = 0
                    if 'SNR' in params:
                        try:
                            snr = int(params.get('SNR', 0))
                        except:
                            snr = 0
                    elif 'snr' in params:
                        try:
                            snr = int(params.get('snr', 0))
                        except:
                            snr = 0
                    
                    text = str(value)
                    
                    # SNR aus Text extrahieren
                    snr_match = re.search(r'SNR[:\s]*([-\d]+)', text, re.IGNORECASE)
                    if snr_match:
                        try:
                            snr = int(snr_match.group(1))
                        except:
                            pass
                    
                    if not callsign and text:
                        parts = text.strip().split()
                        if parts:
                            potential_call = parts[0]
                            if Validator.validate_callsign(potential_call):
                                callsign = potential_call
                    
                    if callsign and Validator.validate_callsign(callsign):
                        if not Validator.validate_snr(snr):
                            snr = 0
                        
                        log_msg = f"{callsign}: {text}"
                        if snr != 0:
                            log_msg += f" [SNR:{snr}Hz]"
                        
                        self.log_message(f"IN: {log_msg}", "incoming")
                        
                        self.update_station_list(callsign, snr)
                        
                        if self.auto_log_enabled:
                            self.log_to_file(callsign, text, snr, grid)
                        
                        if self.bot_enabled and self.my_call in text.upper():
                            self.auto_respond_to_message(callsign, text.upper(), snr, 27245000)
                    
                elif mtype == 'TX.SENT':
                    text = params.get('TEXT', '') or value
                    if text:
                        self.log_message(f"[OK] TX GESENDET: {text}", "autoenter")
                
                elif mtype == 'STATION.LOGGED':
                    callsign = params.get('CALLSIGN', '') or params.get('callsign', '')
                    if callsign and Validator.validate_callsign(callsign):
                        self.update_station_list(callsign, 0)
                        
        except Exception as e:
            logger.error(f"[ERR] Error processing message: {e}")
    
    def auto_respond_to_message(self, callsign, text, snr, freq):
        """Automatische Antwort auf Nachrichten"""
        if callsign == self.my_call:
            return
        
        current_time = time.time()
        last_response = self.last_bot_response_time.get(callsign, 0)
        
        if current_time - last_response < self.bot_response_interval:
            return
        
        text_clean = text.replace(f"@{self.my_call}", "").strip().upper()
        
        is_heartbeat = "HEARTBEAT" in text_clean or "HB" in text_clean
        is_cq = text_clean.startswith("CQ") or "@ALLCALL" in text_clean
        is_query = f"@{self.my_call}" in text
        
        if (is_heartbeat or is_cq or is_query) and callsign not in self.eqsl_conversations:
            if is_heartbeat:
                response = f"@{callsign} {self.my_call} HB ACK SNR {snr}"
            elif is_cq:
                response = f"@{callsign} {self.my_call} SNR?"
            else:
                response = f"@{callsign} {self.my_call} ROGER"
            
            if self.js8.send_message_with_auto_enter(response):
                self.last_bot_response_time[callsign] = current_time
                self.bot_status_label.config(
                    text=f"Bot: Antwort an {callsign}", fg="yellow")
                self.log_message(f"BOT: Antwort an {callsign}: {response}", "bot")
                
                self.root.after(5000, lambda: self.bot_status_label.config(
                    text="Bot Status: Aktiv", fg="#00ff00"))
    
    def auto_cq_loop(self):
        """Auto-CQ Schleife"""
        while self.connected and self.auto_cq_enabled:
            self.send_cq()
            time.sleep(600)
    
    def auto_heartbeat_loop(self):
        """Auto-Heartbeat Schleife"""
        while self.connected and self.auto_heartbeat_enabled:
            self.send_heartbeat()
            time.sleep(900)
    
    def send_heartbeat(self):
        """Sendet Heartbeat"""
        if not self.connected:
            return False
        
        try:
            heartbeat_message = f"@HB HEARTBEAT {self.my_call} {self.my_grid}"
            
            if self.manual_mode:
                if self.send_js8_text_only(heartbeat_message):
                    self.log_message("[OK] Heartbeat Text gesetzt (Manual Mode)", "system")
                    return True
            else:
                if self.js8.send_message_with_auto_enter(heartbeat_message):
                    self.log_message(f"[OK] HEARTBEAT gesendet", "heartbeat")
                    return True
            return False
        except Exception as e:
            self.log_message(f"[ERR] Heartbeat Fehler: {e}", "error")
            return False
    
    def update_station_list(self, callsign, snr):
        """Fügt Station zur Liste hinzu"""
        # Prüfe ob Station bereits existiert
        for item in self.stations_tree.get_children():
            if self.stations_tree.item(item)['values'][0] == callsign:
                self.update_station_in_treeview(item, callsign, snr)
                self.stations_tree.move(item, '', 0)  # Nach oben bewegen
                return
        
        # NEUE Station hinzufügen
        cb_number = self.extract_cb_number(callsign)
        
        if cb_number is None:
            country_info = {"DE": "UNBEKANNT", "CODE": "??"}
        else:
            country_info = cb_prefixes.get(cb_number, 
                                          {"DE": "UNBEKANNT", "CODE": "??"})
        
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        # PNG-Flagge
        if self.flag_display_mode == 'png':
            country_code = country_info.get("CODE", "")
            flag_image = self.flag_manager.get_flag(country_code)
            item = self.stations_tree.insert('', 0, image=flag_image, values=(
                callsign, country_info["DE"], snr, utc_time
            ))
        else:
            # Andere Modi
            flag_display = self.get_flag_display(country_info)
            item = self.stations_tree.insert('', 0, values=(
                callsign, country_info["DE"], snr, utc_time
            ))
        
        # Liste auf 50 Einträge begrenzen
        items = self.stations_tree.get_children()
        if len(items) > 50:
            for item in items[50:]:
                self.stations_tree.delete(item)
    
    def extract_cb_number(self, callsign):
        """Extrahiert CB Nummer aus Callsign"""
        try:
            callsign = callsign.strip().upper()
            match = re.match(r'^(\d{1,3})[A-Z]+', callsign)
            if match:
                cb_number = int(match.group(1))
                return cb_number
            return None
        except Exception as e:
            logger.debug(f"[DEBUG] CB-Nummer Extraktionsfehler für {callsign}: {e}")
            return None
    
    def log_to_file(self, callsign, text, snr, grid):
        """Loggt Nachrichten in Datei"""
        try:
            log_dir = self.config.get('PATHS', 'log_dir', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            log_file = os.path.join(log_dir, f"js8call_{datetime.now().strftime('%Y%m')}.log")
            
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} | {callsign} | SNR:{snr} | GRID:{grid} | {text}\n")
            
        except Exception as e:
            logger.error(f"[ERR] Log file error: {e}")
    
    def log_message(self, message, msg_type="system"):
        """Loggt Nachricht in UI"""
        message = safe_string(message)
        
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        
        # In Text Widget
        self.message_text.insert(tk.END, f"[{timestamp}] {message}\n", msg_type)
        self.message_text.see(tk.END)
        
        # Auch in Datei wenn aktiviert
        if self.auto_log_enabled and msg_type in ["incoming", "outgoing", "heartbeat"]:
            logger.info(f"{msg_type.upper()}: {message}")

def main():
    """Hauptfunktion"""
    try:
        root = tk.Tk()
        app = JS8CallApp(root)
        
        def on_closing():
            if app.connected:
                app.disconnect_js8call()
            app.config.save_config()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"[CRITICAL] Kritischer Fehler: {e}", exc_info=True)
        messagebox.showerror("Fehler", f"Kritischer Fehler:\n{str(e)}")

if __name__ == "__main__":
    main()