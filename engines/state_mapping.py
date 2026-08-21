"""
🗺️ US State Mapping Module
============================
Mapeo de estados de EE.UU. con datos relevantes para OSINT:
- SSN Area Numbers (históricos pre-2011)
- Código de área NANP por estado
- Zonas horarias
- Población aproximada

Fuente: SSA Pub. No. 05-10633 / NANP
"""

# ─── Historical SSN Area Numbers by State (pre-2011) ────────────────────────
# Formato: { "state_code": [ (start, end), ... ] }
STATE_SSN_AREAS = {
    "AL": [(416, 424)],                          # Alabama
    "AK": [(574, 574)],                          # Alaska
    "AZ": [(526, 527), (600, 601)],              # Arizona
    "AR": [(429, 432)],                          # Arkansas
    "CA": [(545, 573), (602, 626)],              # California
    "CO": [(521, 524)],                          # Colorado
    "CT": [(40, 49)],                            # Connecticut
    "DE": [(221, 222)],                          # Delaware
    "DC": [(577, 579)],                          # District of Columbia
    "FL": [(261, 267), (589, 595), (766, 772)],  # Florida
    "GA": [(252, 260), (667, 675)],              # Georgia
    "HI": [(575, 576)],                          # Hawaii
    "ID": [(518, 519)],                          # Idaho
    "IL": [(318, 361)],                          # Illinois
    "IN": [(303, 317)],                          # Indiana
    "IA": [(478, 485)],                          # Iowa
    "KS": [(509, 515)],                          # Kansas
    "KY": [(400, 402)],                          # Kentucky
    "LA": [(433, 439)],                          # Louisiana
    "ME": [(4, 7)],                              # Maine
    "MD": [(212, 220)],                          # Maryland
    "MA": [(10, 34)],                            # Massachusetts
    "MI": [(362, 386)],                          # Michigan
    "MN": [(468, 477)],                          # Minnesota
    "MS": [(425, 428), (587, 588)],              # Mississippi
    "MO": [(486, 500)],                          # Missouri
    "MT": [(516, 517)],                          # Montana
    "NE": [(505, 508)],                          # Nebraska
    "NV": [(530, 530)],                          # Nevada
    "NH": [(1, 3)],                              # New Hampshire
    "NJ": [(135, 158)],                          # New Jersey
    "NM": [(525, 525), (585, 585)],              # New Mexico
    "NY": [(1, 3), (50, 134)],                   # New York
    "NC": [(237, 246), (681, 690)],              # North Carolina
    "ND": [(501, 502)],                          # North Dakota
    "OH": [(268, 302)],                          # Ohio
    "OK": [(440, 448)],                          # Oklahoma
    "OR": [(540, 544)],                          # Oregon
    "PA": [(159, 211)],                          # Pennsylvania
    "RI": [(35, 39)],                            # Rhode Island
    "SC": [(247, 251), (654, 658)],              # South Carolina
    "SD": [(503, 504)],                          # South Dakota
    "TN": [(408, 415), (756, 765)],              # Tennessee
    "TX": [(449, 467), (627, 645)],              # Texas
    "UT": [(528, 529)],                          # Utah
    "VT": [(8, 9)],                              # Vermont
    "VA": [(223, 231), (691, 699)],              # Virginia
    "WA": [(531, 539)],                          # Washington
    "WV": [(232, 236)],                          # West Virginia
    "WI": [(387, 399)],                          # Wisconsin
    "WY": [(520, 520)],                          # Wyoming
    "PR": [(580, 584), (596, 599)],              # Puerto Rico
    "GU": [(586, 586)],                          # Guam
    "VI": [(580, 581)],                          # US Virgin Islands
    "AS": [(586, 586)],                          # American Samoa
    "MP": [(586, 586)],                          # Northern Mariana Islands
    "MIL": [(700, 728)],                         # Military (overseas)
}

# ─── State Names ─────────────────────────────────────────────────────────────
STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "DC": "District of Columbia", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii",
    "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine",
    "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska",
    "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
    "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island",
    "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
    "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
    "PR": "Puerto Rico", "GU": "Guam", "VI": "US Virgin Islands",
    "AS": "American Samoa", "MP": "Northern Mariana Islands",
}

# ─── NANP Area Codes by State ───────────────────────────────────────────────
# Main area codes for each state (simplified)
STATE_AREA_CODES = {
    "AL": ["205", "251", "256", "334"],
    "AK": ["907"],
    "AZ": ["480", "520", "602", "623", "928"],
    "AR": ["479", "501", "870"],
    "CA": ["209", "213", "310", "323", "408", "415", "424", "442", "510", "530",
           "559", "562", "619", "626", "628", "650", "657", "661", "669", "707",
           "714", "747", "760", "805", "818", "831", "858", "909", "916", "925",
           "949", "951"],
    "CO": ["303", "719", "720", "970"],
    "CT": ["203", "475", "860", "959"],
    "DE": ["302"],
    "DC": ["202"],
    "FL": ["239", "305", "321", "352", "386", "407", "561", "689", "727", "754",
           "772", "786", "813", "850", "863", "904", "941", "954"],
    "GA": ["229", "404", "470", "678", "706", "770", "912"],
    "HI": ["808"],
    "ID": ["208", "986"],
    "IL": ["217", "224", "309", "312", "331", "618", "630", "708", "773", "779",
           "815", "847", "872"],
    "IN": ["219", "260", "317", "463", "574", "765", "812", "930"],
    "IA": ["319", "515", "563", "641", "712"],
    "KS": ["316", "620", "785", "913"],
    "KY": ["270", "364", "502", "606", "859"],
    "LA": ["225", "318", "337", "504", "985"],
    "ME": ["207"],
    "MD": ["227", "240", "301", "410", "443", "667"],
    "MA": ["339", "351", "413", "508", "617", "774", "781", "857", "978"],
    "MI": ["231", "248", "269", "313", "517", "586", "616", "734", "810", "906",
           "989"],
    "MN": ["218", "320", "507", "612", "651", "763", "952"],
    "MS": ["228", "601", "662"],
    "MO": ["314", "417", "573", "636", "660", "816"],
    "MT": ["406"],
    "NE": ["308", "402", "531"],
    "NV": ["702", "725", "775"],
    "NH": ["603"],
    "NJ": ["201", "551", "609", "732", "848", "856", "862", "908", "973"],
    "NM": ["505", "575"],
    "NY": ["212", "315", "332", "347", "516", "518", "585", "607", "631", "646",
           "680", "716", "718", "838", "845", "914", "917", "929"],
    "NC": ["252", "336", "704", "743", "828", "910", "919", "980", "984"],
    "ND": ["701"],
    "OH": ["216", "220", "234", "283", "326", "330", "380", "419", "440", "513",
           "567", "614", "740", "937"],
    "OK": ["405", "539", "580", "918"],
    "OR": ["458", "503", "541", "971"],
    "PA": ["215", "223", "267", "272", "412", "445", "484", "570", "610", "717",
           "724", "814", "878"],
    "RI": ["401"],
    "SC": ["803", "843", "864"],
    "SD": ["605"],
    "TN": ["423", "615", "629", "731", "865", "901", "931"],
    "TX": ["210", "214", "254", "281", "325", "361", "409", "432", "469", "512",
           "682", "713", "737", "806", "817", "832", "903", "915", "936", "940",
           "956", "972", "979"],
    "UT": ["385", "435", "801"],
    "VT": ["802"],
    "VA": ["276", "434", "540", "571", "703", "757", "804"],
    "WA": ["206", "253", "360", "425", "509", "564"],
    "WV": ["304", "681"],
    "WI": ["262", "414", "534", "608", "715", "920"],
    "WY": ["307"],
}

# ─── Time Zones ──────────────────────────────────────────────────────────────
STATE_TIMEZONES = {
    "AL": "CST", "AK": "AKST", "AZ": "MST", "AR": "CST",
    "CA": "PST", "CO": "MST", "CT": "EST", "DE": "EST",
    "DC": "EST", "FL": "EST", "GA": "EST", "HI": "HST",
    "ID": "MST", "IL": "CST", "IN": "EST", "IA": "CST",
    "KS": "CST", "KY": "EST", "LA": "CST", "ME": "EST",
    "MD": "EST", "MA": "EST", "MI": "EST", "MN": "CST",
    "MS": "CST", "MO": "CST", "MT": "MST", "NE": "CST",
    "NV": "PST", "NH": "EST", "NJ": "EST", "NM": "MST",
    "NY": "EST", "NC": "EST", "ND": "CST", "OH": "EST",
    "OK": "CST", "OR": "PST", "PA": "EST", "RI": "EST",
    "SC": "EST", "SD": "CST", "TN": "CST", "TX": "CST",
    "UT": "MST", "VT": "EST", "VA": "EST", "WA": "PST",
    "WV": "EST", "WI": "CST", "WY": "MST",
}


def get_state_from_ssn_area(area: int) -> str:
    """Get state code from SSN area number (historical pre-2011)"""
    for state, ranges in STATE_SSN_AREAS.items():
        for start, end in ranges:
            if start <= area <= end:
                return state
    return "UNKNOWN"


def get_state_from_area_code(area_code: str) -> str:
    """Get state code from NANP area code"""
    for state, codes in STATE_AREA_CODES.items():
        if area_code in codes:
            return state
    return "UNKNOWN"


def get_all_states():
    """Return list of all state codes"""
    return list(STATE_NAMES.keys())


def get_state_info(state_code: str) -> dict:
    """Get complete info for a state"""
    return {
        "code": state_code,
        "name": STATE_NAMES.get(state_code, "Unknown"),
        "area_codes": STATE_AREA_CODES.get(state_code, []),
        "timezone": STATE_TIMEZONES.get(state_code, "Unknown"),
        "ssn_areas": STATE_SSN_AREAS.get(state_code, []),
    }
