import streamlit as st
import re

# =====================================================================
# COUNTRY / STATE / CITY DATA
# =====================================================================

COUNTRY_STATE_DATA = {
    "AE": {"name": "United Arab Emirates", "states": [("AJ","Ajman"),("AZ","Abu Dhabi"),("DU","Dubai"),("FU","Fujairah"),("RK","Ras al-Khaimah"),("SH","Sharjah"),("UQ","Umm Al Quwain")]},
    "BH": {"name": "Bahrain", "states": [("13","Al 'Asimah"),("14","Al Janubiyah"),("15","Al Muharraq"),("17","Ash Shamaliyah")]},
    "IN": {"name": "India", "states": [
        ("AN","Andaman & Nicobar Islands"),("AP","Andhra Pradesh (Old)"),("AD","Andhra Pradesh"),
        ("AR","Arunachal Pradesh"),("AS","Assam"),("BR","Bihar"),("CH","Chandigarh"),
        ("CT","Chhattisgarh"),("DN","Dadra and Nagar Haveli and Daman and Diu"),
        ("DD","Daman & Diu"),("DL","Delhi"),("GA","Goa"),("GJ","Gujarat"),
        ("HR","Haryana"),("HP","Himachal Pradesh"),("JK","Jammu & Kashmir"),
        ("JH","Jharkhand"),("KA","Karnataka"),("KL","Kerala"),("LA","Ladakh"),
        ("LD","Lakshadweep"),("MP","Madhya Pradesh"),("MH","Maharashtra"),
        ("MN","Manipur"),("ML","Meghalaya"),("MZ","Mizoram"),("NL","Nagaland"),
        ("OR","Odisha"),("PB","Punjab"),("PY","Puducherry"),("RJ","Rajasthan"),
        ("SK","Sikkim"),("TN","Tamil Nadu"),("TL","Telangana"),("TR","Tripura"),
        ("UP","Uttar Pradesh"),("UT","Uttarakhand"),("WB","West Bengal"),
    ]},
    "KW": {"name": "Kuwait", "states": [("AH","Al Ahmadi"),("FA","Al Farwaniyah"),("JA","Al Jahra"),("KU","Al Kuwayt"),("HA","Hawalli"),("MU","Mubarak Al-Kabeer")]},
    "LK": {"name": "Sri Lanka", "states": [
        ("11","Colombo"),("12","Gampaha"),("13","Kalutara"),("21","Kandy"),
        ("22","Matale"),("23","Nuwara Eliya"),("31","Galle"),("32","Matara"),
        ("33","Hambantota"),("41","Jaffna"),("42","Kilinochchi"),("43","Mannar"),
        ("44","Mullaitivu"),("45","Vavuniya"),("51","Batticaloa"),("52","Ampara"),
        ("53","Trincomalee"),("61","Kurunegala"),("62","Puttalam"),("71","Anuradhapura"),
        ("72","Polonnaruwa"),("81","Badulla"),("82","Monaragala"),("91","Ratnapura"),("92","Kegalle"),
    ]},
    "OM": {"name": "Oman", "states": [("BA","Al Batinah North"),("BJ","Janub al Batinah"),("BS","Shamal al Batinah"),("BU","Al Buraymi"),("DA","Ad Dakhiliyah"),("MA","Masqat"),("MU","Musandam"),("SH","Ash Sharqiyah North"),("SS","Ash Sharqiyah South"),("WU","Al Wusta"),("ZA","Az Zahirah")]},
    "QA": {"name": "Qatar", "states": [("DA","Ad Dawhah"),("KH","Al Khawr"),("MS","Ash Shahaniyah"),("RA","Ar Rayyan"),("SH","Ash Shihaniyah"),("US","Umm Salal"),("WA","Al Wakrah"),("ZA","Az Za'ayin")]},
    "SA": {"name": "Saudi Arabia", "states": [("01","Ar Riyad"),("02","Makkah al Mukarramah"),("03","Al Madinah al Munawwarah"),("04","Ash Sharqiyah"),("05","Al Qasim"),("06","Ha'il"),("07","Tabuk"),("08","Al Hudud ash Shamaliyah"),("09","Jizan"),("10","Najran"),("11","Al Bahah"),("12","Al Jawf"),("14","Asir")]},
    "US": {"name": "United States", "states": [
        ("AL","Alabama"),("AK","Alaska"),("AZ","Arizona"),("AR","Arkansas"),("CA","California"),
        ("CO","Colorado"),("CT","Connecticut"),("DE","Delaware"),("FL","Florida"),("GA","Georgia"),
        ("HI","Hawaii"),("ID","Idaho"),("IL","Illinois"),("IN","Indiana"),("IA","Iowa"),
        ("KS","Kansas"),("KY","Kentucky"),("LA","Louisiana"),("ME","Maine"),("MD","Maryland"),
        ("MA","Massachusetts"),("MI","Michigan"),("MN","Minnesota"),("MS","Mississippi"),
        ("MO","Missouri"),("MT","Montana"),("NE","Nebraska"),("NV","Nevada"),("NH","New Hampshire"),
        ("NJ","New Jersey"),("NM","New Mexico"),("NY","New York"),("NC","North Carolina"),
        ("ND","North Dakota"),("OH","Ohio"),("OK","Oklahoma"),("OR","Oregon"),("PA","Pennsylvania"),
        ("RI","Rhode Island"),("SC","South Carolina"),("SD","South Dakota"),("TN","Tennessee"),
        ("TX","Texas"),("UT","Utah"),("VT","Vermont"),("VA","Virginia"),("WA","Washington"),
        ("WV","West Virginia"),("WI","Wisconsin"),("WY","Wyoming"),("DC","District of Columbia"),
        ("AS","American Samoa"),("GU","Guam"),("MP","Northern Mariana Islands"),
        ("PR","Puerto Rico"),("VI","U.S. Virgin Islands"),
    ]},
}

# Major Indian cities for multiselect
INDIA_CITIES = sorted([
    "Agra","Ahmedabad","Ajmer","Aligarh","Allahabad","Amritsar","Aurangabad",
    "Bangalore","Bareilly","Bhopal","Bhubaneswar","Chandigarh","Chennai","Coimbatore",
    "Delhi","Dehradun","Dhanbad","Durgapur","Faridabad","Ghaziabad","Gurgaon",
    "Guwahati","Gwalior","Hubli","Hyderabad","Indore","Jabalpur","Jaipur",
    "Jalandhar","Jammu","Jodhpur","Kanpur","Kochi","Kolkata","Kozhikode",
    "Lucknow","Ludhiana","Madurai","Mangalore","Meerut","Mumbai","Mysore",
    "Nagpur","Nashik","Noida","Patna","Pune","Raipur","Rajkot","Ranchi",
    "Srinagar","Surat","Thiruvananthapuram","Tiruchirappalli","Udaipur",
    "Vadodara","Varanasi","Vijayawada","Visakhapatnam",
])

COUNTRY_OPTIONS = {cc: f"{cc} — {data['name']}" for cc, data in COUNTRY_STATE_DATA.items()}
ALL_COUNTRY_OPTIONS = [""] + list(COUNTRY_OPTIONS.keys())

def get_state_options(country_code):
    if not country_code or country_code not in COUNTRY_STATE_DATA:
        return []
    return [f"{code} — {name}" for code, name in COUNTRY_STATE_DATA[country_code]["states"]]

def extract_state_codes(selected_states):
    return [s.split(" — ")[0].strip() for s in selected_states if s]

# =====================================================================
# PAGE CONFIG
# =====================================================================

st.set_page_config(
    page_title="Rule Engine · UniCommerce",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Premium UI Styling ────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit default chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}

/* ── App header ── */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid rgba(128,128,128,0.15);
    margin-bottom: 1.75rem;
}
.app-header .logo {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.app-header h1 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    color: inherit !important;
    margin: 0 !important;
    padding: 0 !important;
    letter-spacing: -0.01em;
}
.app-header .version {
    font-size: 11px;
    color: rgba(128,128,128,0.8);
    font-weight: 400;
    margin-top: 2px;
    letter-spacing: 0.02em;
}

/* ── Section headers (D2 groups) ── */
h4 {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    color: #6366f1 !important;
    margin-bottom: 0 !important;
    margin-top: 0 !important;
}

/* ── Section box wrapper ── */
.section-box {
    background: rgba(99,102,241,0.03);
    border: 1px solid rgba(99,102,241,0.10);
    border-radius: 12px;
    padding: 1.1rem 1.2rem 0.5rem;
    margin-bottom: 1.2rem;
}
.section-box-grey {
    background: rgba(128,128,128,0.03);
    border: 1px solid rgba(128,128,128,0.10);
    border-radius: 12px;
    padding: 1.1rem 1.2rem 0.5rem;
    margin-bottom: 1.2rem;
}

/* ── Reverse pickup toggle card ── */
.rp-card {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 16px;
    border-radius: 10px;
    border: 1.5px solid rgba(128,128,128,0.15);
    background: rgba(128,128,128,0.03);
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.15s ease;
}
.rp-card.active {
    border-color: #f59e0b;
    background: rgba(245,158,11,0.05);
}
.rp-card .rp-icon {
    font-size: 20px;
    flex-shrink: 0;
}
.rp-card .rp-text h5 {
    font-size: 0.82rem;
    font-weight: 600;
    margin: 0 0 2px;
    color: inherit;
}
.rp-card .rp-text p {
    font-size: 0.72rem;
    color: rgba(128,128,128,0.7);
    margin: 0;
}
.rp-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.rp-badge.forward { background: rgba(99,102,241,0.1); color: #6366f1; }
.rp-badge.reverse { background: rgba(245,158,11,0.15); color: #d97706; }

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(128,128,128,0.12) !important;
    margin: 0.4rem 0 1rem 0 !important;
}

/* ── Caption / subtitle ── */
.stCaption, [data-testid="stCaptionContainer"] p {
    font-size: 0.72rem !important;
    color: rgba(128,128,128,0.7) !important;
    margin-bottom: 0.5rem !important;
    font-weight: 400 !important;
}

/* ── Labels ── */
.stMarkdown p strong {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em;
}

/* ── Inputs ── */
input[type="text"], textarea {
    border-radius: 8px !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
    font-size: 0.82rem !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.15s ease !important;
}
input[type="text"]:focus, textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    border-radius: 8px !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
    font-size: 0.82rem !important;
}

/* ── Multiselect ── */
.stMultiSelect > div > div {
    border-radius: 8px !important;
    border: 1px solid rgba(128,128,128,0.2) !important;
    font-size: 0.82rem !important;
}
.stMultiSelect [data-baseweb="tag"] {
    border-radius: 6px !important;
    background: rgba(99,102,241,0.1) !important;
    color: #6366f1 !important;
    font-size: 0.75rem !important;
}

/* ── Checkbox ── */
.stCheckbox label {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    gap: 8px !important;
}
.stCheckbox label span {
    font-size: 0.82rem !important;
}

/* ── Radio ── */
.stRadio label {
    font-size: 0.8rem !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.8rem !important;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.4rem !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.25) !important;
    transition: all 0.15s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(99,102,241,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Secondary button ── */
.stButton > button:not([kind="primary"]) {
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

/* ── Code block ── */
.stCode, [data-testid="stCode"] {
    border-radius: 10px !important;
    border: 1px solid rgba(128,128,128,0.12) !important;
    font-size: 0.8rem !important;
}
[data-testid="stCode"] pre {
    border-radius: 10px !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    background: rgba(128,128,128,0.04) !important;
}
.streamlit-expanderContent {
    border-radius: 0 0 8px 8px !important;
    border: 1px solid rgba(128,128,128,0.1) !important;
    border-top: none !important;
}

/* ── Info / warning / success / error boxes ── */
.stAlert {
    border-radius: 10px !important;
    border: none !important;
    font-size: 0.8rem !important;
}
[data-testid="stNotification"] {
    border-radius: 10px !important;
    font-size: 0.8rem !important;
}

/* ── Success box ── */
.element-container [data-testid="stAlert"][data-baseweb="notification"] {
    border-radius: 10px !important;
}

/* ── Tab bar ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(128,128,128,0.06) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 6px 14px !important;
    color: rgba(128,128,128,0.8) !important;
    border: none !important;
    transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #6366f1 !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08) !important;
}

/* ── Module selectbox label ── */
.stSelectbox label {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
}

/* ── Metric ── */
[data-testid="metric-container"] {
    background: rgba(128,128,128,0.04) !important;
    border: 1px solid rgba(128,128,128,0.1) !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
}
[data-testid="metric-container"] label {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 10px !important;
    border: 1px solid rgba(128,128,128,0.12) !important;
    overflow: hidden !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border-radius: 10px !important;
}
[data-testid="stFileUploadDropzone"] {
    border-radius: 10px !important;
    border: 1.5px dashed rgba(128,128,128,0.25) !important;
    background: rgba(128,128,128,0.02) !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #6366f1 !important;
    background: rgba(99,102,241,0.03) !important;
}

/* ── Sidebar (collapsed state) ── */
section[data-testid="stSidebar"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── App Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div class="logo">⚡</div>
  <div>
    <h1>UniCommerce Rule Engine</h1>
    <div class="version">Version 8.0.0 &nbsp;·&nbsp; Facility &nbsp;·&nbsp; Shipping Provider &nbsp;·&nbsp; Inventory &nbsp;·&nbsp; Tools</div>
  </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# HELPER METHODS
# =====================================================================

def csv_items(raw_input):
    return [x.strip() for x in raw_input.split(",") if x.strip()]

def smart_format_string(raw_input, var_name, use_ignore_case=False, strip_spaces=False):
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    eff = f'{var_name}.replace(" ", "")' if strip_spaces else var_name
    if len(items) == 1:
        val = items[0]
        return f"{eff}.equalsIgnoreCase('{val}')" if use_ignore_case else f"{eff} == '{val}'"
    quoted = ", ".join(f"'{v}'" for v in items)
    func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
    return f"T(com.unifier.core.utils.StringUtils).{func}({eff}, {quoted})"

def format_multi_value_condition(raw_input, var_name):
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    if len(items) == 1:
        return f"{var_name} == '{items[0]}'"
    quoted = ", ".join(f"'{v}'" for v in items)
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {quoted})"

def format_not_equals_condition(raw_input, var_name):
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    if len(items) == 1:
        return f"{var_name} != '{items[0]}'"
    return " and ".join(f"{var_name} != '{v}'" for v in items)

def validate_inputs(warnings_list, field_label, raw_input, field_type="generic"):
    if not raw_input or not raw_input.strip():
        return
    items = [x.strip() for x in raw_input.split(",")]
    if any(i == "" for i in items):
        warnings_list.append(f"**{field_label}:** Contains an empty entry — check for a trailing or double comma.")
    clean = [i for i in items if i]
    seen, dups = set(), set()
    for i in clean:
        if i.lower() in seen: dups.add(i)
        seen.add(i.lower())
    if dups:
        warnings_list.append(f"**{field_label}:** Duplicate value(s) — `{'`, `'.join(dups)}`.")
    if field_type == "pincode":
        bad = [p for p in clean if not re.match(r'^\d{6}$', p)]
        if bad:
            warnings_list.append(f"**{field_label}:** `{'`, `'.join(bad)}` — pincodes must be exactly 6 digits.")
    elif field_type == "channel":
        for c in clean:
            if ' ' in c:
                warnings_list.append(f"**{field_label}:** `{c}` contains a space — channel codes should not have spaces.")
            elif c != c.upper():
                warnings_list.append(f"**{field_label}:** `{c}` has mixed casing — channel codes are typically uppercase.")
    elif field_type == "number":
        bad = [n for n in clean if not re.match(r'^\d+(\.\d+)?$', n)]
        if bad:
            warnings_list.append(f"**{field_label}:** `{'`, `'.join(bad)}` — must be a numeric value.")

# =====================================================================
# RULE CHECKS (shared by Validator + Audit)
# =====================================================================

def check_rule_for_issues(expr):
    issues = []
    s = str(expr)

    if re.search(r'(?<![#\w.])(shippingPackage|saleOrder|reversePickup|allocationCriteria|inventorySnapshot)\.', s):
        issues.append({"severity":"🔴 Critical","message":"Variable reference missing `#` prefix (e.g. `shippingPackage.x` instead of `#shippingPackage.x`). Causes `Property or field cannot be found on null` at runtime — crashes entire allocation.","fix":"Add `#` before every variable: `#shippingPackage`, `#saleOrder`, `#reversePickup`."})

    if 'equalsIngoreCase' in s:
        issues.append({"severity":"🔴 Critical","message":"`equalsIngoreCase` is a typo — correct method is `equalsIgnoreCase`. Rule silently never matches.","fix":"Replace `equalsIngoreCase` with `equalsIgnoreCase`."})

    if 'equalsIngoreCaseAny' in s:
        issues.append({"severity":"🔴 Critical","message":"`equalsIngoreCaseAny` is a typo — correct method is `equalsIgnoreCaseAny`.","fix":"Replace `equalsIngoreCaseAny` with `equalsIgnoreCaseAny`."})

    has_and = bool(re.search(r'\band\b', s, re.IGNORECASE))
    has_or  = bool(re.search(r'\bor\b',  s, re.IGNORECASE))
    if has_and and has_or:
        stripped = s
        prev = None
        while prev != stripped:
            prev = stripped
            stripped = re.sub(r'\([^()]*\)', '', stripped)
        if bool(re.search(r'\bor\b', stripped, re.IGNORECASE)):
            issues.append({"severity":"🟠 High","message":"Rule mixes `and` and `or` without enclosing the `or` in parentheses. In SpEL, `and` binds tighter than `or` — caused a real production incident (Zippee_Mumbai) where every tagged order was misrouted.","fix":"Wrap the `or` clause: `... and (conditionA or conditionB)`."})

    m = re.findall(r'equalsAny\([^,)]+,\s*\'[^\']+\'\s*\)', s)
    if m:
        issues.append({"severity":"🟡 Medium","message":f"`equalsAny()` used with only one value: `{m[0][:80]}`. Use `== 'VALUE'` for a single value.","fix":"Replace `equalsAny(field, 'VALUE')` with `field == 'VALUE'`."})

    if re.search(r'equalsAny\([^)]*,\s*\d+\s*[,)]', s):
        issues.append({"severity":"🔴 Critical","message":"Unquoted integer inside `equalsAny()` — type mismatch, will never match.","fix":"Quote all values: `equalsAny(field, '110001', '110002')`."})

    if re.search(r'#shippingPackage\.channel\.code', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "`#shippingPackage.channel.code` is missing `.saleOrder` in the path. This causes a `Property or field 'channel' cannot be found` error at runtime and crashes allocation.",
            "fix": "Change to `#shippingPackage.saleOrder.channel.code`."
        })

    if re.search(r'paymetmethod', s, re.IGNORECASE):
        issues.append({
            "severity": "🔴 Critical",
            "message": "`paymetmethod` is a typo — the correct field is `paymentMethod` (missing the letter 'n'). Rule will never evaluate correctly.",
            "fix": "Change `paymetmethod` to `paymentMethod`."
        })

    if re.search(r'#shippingPackage\.shippingMethod\.paymentMethod', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "`#shippingPackage.shippingMethod.paymentMethod.code` is the wrong path — `paymentMethod` is not on `shippingMethod`.",
            "fix": "Change to `#shippingPackage.saleOrder.paymentMethod.code`."
        })

    if re.search(r'#reversePickup\.SaleOrder', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "`#reversePickup.SaleOrder` has wrong casing — `SaleOrder` should be `saleOrder` (lowercase s). SpEL is case-sensitive.",
            "fix": "Change `SaleOrder` to `saleOrder`."
        })

    if re.search(r'#saleOrder\.shippingAddress', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "`#saleOrder.shippingAddress` is not a valid path — `shippingAddress` is not directly on `saleOrder`. This causes `Property or field 'shippingAddress' cannot be found` at runtime.",
            "fix": "Use `#saleOrderItem.shippingAddress.stateCode` / `.pincode` / `.city` / `.countryCode` instead."
        })

    if re.search(r'hasliveInventory', s):
        issues.append({
            "severity": "🟠 High",
            "message": "`hasliveInventory` has wrong casing — the correct method is `hasLiveInventory` (capital L). Rule may not match as expected.",
            "fix": "Change `hasliveInventory` to `hasLiveInventory`."
        })

    if re.search(r',\s*\)', s):
        issues.append({"severity":"🟠 High","message":"Trailing comma before `)` — causes a SpEL parse error.","fix":"Remove the trailing comma."})

    if '.contains(' in s and '!= null' not in s and 'CustomFieldUtils' in s:
        issues.append({"severity":"🟠 High","message":"`getCustomFieldValue(...).contains(...)` without a prior `!= null` check. If the field is absent, this throws NullPointerException.","fix":"Add: `getCustomFieldValue(...) != null and getCustomFieldValue(...).contains('value')`."})

    stripped2 = s.strip()
    if stripped2 and not stripped2.startswith('#{') and not stripped2.startswith('#'):
        issues.append({"severity":"🔴 Critical","message":"Expression does not start with `#{` — plain text, not SpEL. Throws type-conversion error.","fix":"Wrap in `#{...}`: e.g. `#{#shippingPackage.totalPrice <= 6000}`."})

    return issues

# =====================================================================
# REVERSE COMPILER HELPER
# =====================================================================

def decode_spel(expr):
    s = str(expr).strip()
    if s.startswith("#{") and s.endswith("}"):
        s = s[2:-1].strip()
    results = []

    def split_and(text):
        parts, depth, current = [], 0, []
        i = 0
        while i < len(text):
            c = text[i]
            if c == '(': depth += 1; current.append(c)
            elif c == ')': depth -= 1; current.append(c)
            elif depth == 0 and text[i:i+4].lower() == ' and':
                parts.append(''.join(current).strip())
                current = []; i += 4; continue
            else: current.append(c)
            i += 1
        if current: parts.append(''.join(current).strip())
        return [p for p in parts if p]

    VAR_MAP = {
        "#saleOrder.channel.code": "Channel Code (Facility)",
        "#shippingPackage.saleOrder.channel.code": "Channel Code (Shipping)",
        "#reversePickup.saleOrder.channel.code": "Return Channel Code",
        "#saleOrderItem.shippingAddress.stateCode": "State Code (Facility)",
        "#shippingPackage.shippingAddress.stateCode": "State Code (Shipping)",
        "#reversePickup.shippingAddress.stateCode": "State Code (Return)",
        "#saleOrderItem.shippingAddress.pincode": "Pincode (Facility)",
        "#shippingPackage.shippingAddress.pincode": "Pincode (Shipping)",
        "#saleOrderItem.shippingAddress.city": "City (Facility)",
        "#shippingPackage.shippingAddress.city": "City (Shipping)",
        "#saleOrderItem.shippingAddress.countryCode": "Country Code (Facility)",
        "#shippingPackage.shippingAddress.countryCode": "Country Code (Shipping)",
        "#saleOrder.paymentMethod.code": "Payment Method (Facility)",
        "#shippingPackage.saleOrder.paymentMethod.code": "Payment Method (Shipping)",
        "#reversePickup.saleOrder.paymentMethod.code": "Payment Method (Return)",
        "#saleOrderItem.skuCode": "SKU Code",
        "#shippingPackage.actualWeight": "Package Weight (g)",
        "#shippingPackage.totalPrice": "Total Price",
        "#reversePickup.boxWeight": "Box Weight (g)",
    }

    for cond in split_and(s):
        cond = cond.strip()
        m = re.match(r'T\(com\.unifier\.core\.utils\.StringUtils\)\.(equalsAny|equalsIgnoreCaseAny)\(([^,]+),\s*(.+)\)', cond)
        if m:
            func, var, vals_raw = m.group(1), m.group(2).strip(), m.group(3).strip()
            vals = re.findall(r"'([^']*)'", vals_raw)
            results.append((VAR_MAP.get(var, var), f"equals any of: {', '.join(vals)}" + (" (case-insensitive)" if "IgnoreCase" in func else ""))); continue
        m = re.match(r'(#[\w.]+)\.equalsIgnoreCase\(\'([^\']+)\'\)', cond)
        if m: results.append((VAR_MAP.get(m.group(1), m.group(1)), f"equals (case-insensitive): {m.group(2)}")); continue
        m = re.match(r"(#[\w.]+)\s*==\s*'([^']*)'", cond)
        if m: results.append((VAR_MAP.get(m.group(1), m.group(1)), f"equals: {m.group(2)}")); continue
        m = re.match(r"(#[\w.]+)\s*!=\s*'([^']*)'", cond)
        if m: results.append((VAR_MAP.get(m.group(1), m.group(1)), f"does NOT equal: {m.group(2)}")); continue
        m = re.match(r"(#[\w.]+)\s*!=\s*null", cond)
        if m: results.append((VAR_MAP.get(m.group(1), m.group(1)), "must exist (not null)")); continue
        m = re.match(r'(#[\w.]+)\s*([><=!]+)\s*(\d+(?:\.\d+)?)', cond)
        if m: results.append((VAR_MAP.get(m.group(1), m.group(1)), f"{m.group(2)} {m.group(3)}")); continue
        m = re.match(r'#allocationCriteria\.(\w+)\(\)', cond)
        if m: results.append(("Inventory Criteria", m.group(1))); continue
        m = re.search(r"hasAnyTag\('([^']+)'\)", cond)
        if m: results.append(("Item Tag", m.group(1))); continue
        m = re.search(r"brand\.contains\('([^']+)'\)", cond)
        if m: results.append(("Brand (contains)", m.group(1))); continue
        m = re.search(r'saleOrderItems\.size\(\)\s*([><=!]+)\s*(\d+)', cond)
        if m: results.append(("Item Count", f"{m.group(1)} {m.group(2)}")); continue
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)[^)]*\.contains\('([^']+)'\)", cond)
        if m: results.append((f"Custom Field '{m.group(1)}'", f"contains: {m.group(2)}")); continue
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)\.equalsIgnoreCase\('([^']+)'\)", cond)
        if m: results.append((f"Custom Field '{m.group(1)}'", f"equals (case-insensitive): {m.group(2)}")); continue
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)\s*!=\s*null", cond)
        if m: results.append((f"Custom Field '{m.group(1)}'", "must exist (not null)")); continue
        if "inventorySnapshot" in cond: results.append(("Inventory Formula", cond[:120])); continue
        results.append(("Condition", cond[:120]))
    return results

# =====================================================================
# CITY UI HELPER
# =====================================================================

def city_multiselect(key_prefix, label="City / Cities"):
    """
    Renders a multiselect for cities.
    Returns comma-separated city string for use in compiler.
    """
    st.markdown(f"**{label}**")
    use_city = st.checkbox("Apply City Filter", key=f"{key_prefix}_use_city",
        help="Select one or more cities from the dropdown (searchable).\n\nCity matching is exact — the value must match exactly what is stored in your Uniware tenant's order data.\n\nSingle city → `== 'Mumbai'` | Multiple → `equalsAny('Mumbai','Delhi')`")
    city_val = ""
    if use_city:
        selected = st.multiselect(
            "Select City / Cities",
            options=INDIA_CITIES,
            key=f"{key_prefix}_city_multi",
            help="Type to search. Select one or more cities. If your city is not in the list, tick 'Enter custom city' below."
        )
        use_custom = st.checkbox("Enter custom city not in list", key=f"{key_prefix}_city_custom_toggle",
            help="Use this if the city you need is not in the dropdown above.")
        custom_city = ""
        if use_custom:
            custom_city = st.text_input("Custom City / Cities (comma-separated)", key=f"{key_prefix}_city_custom_input",
                placeholder="e.g. Pathanamthitta, Alappuzha")
        all_cities = list(selected)
        if custom_city:
            all_cities += [c.strip() for c in custom_city.split(",") if c.strip()]
        city_val = ",".join(all_cities)
    return use_city, city_val

def country_selectbox(key_prefix, label="Country Code"):
    """
    Renders a searchable single-select for country code.
    Returns (use_country, country_val, country_mode).
    """
    st.markdown(f"**{label}**")
    use_country = st.checkbox("Apply Country Code Filter", key=f"{key_prefix}_use_country",
        help="Select a country from the dropdown.\n\n• Equals — order IS from this country\n• Not Equals — order is NOT from this country (e.g. all non-India orders)\n\nSingle country → `== 'IN'`")
    country_val = ""
    country_mode = "equals"
    if use_country:
        country_mode = st.radio("Match Type", ["equals", "not_equals"],
            format_func=lambda x: {"equals": "✅ Equals — order IS from this country", "not_equals": "🚫 Not Equals — order is NOT from this country"}[x],
            horizontal=True, key=f"{key_prefix}_country_mode",
            help="Equals: matches orders shipping TO this country.\nNot Equals: matches orders shipping ANYWHERE EXCEPT this country.")
        selected_cc = st.selectbox(
            "Select Country",
            options=ALL_COUNTRY_OPTIONS,
            format_func=lambda x: "— Select country —" if x == "" else COUNTRY_OPTIONS[x],
            key=f"{key_prefix}_country_select",
            help="Type to search. Select the destination country."
        )
        country_val = selected_cc
    return use_country, country_val, country_mode

# =====================================================================
# ⚙️ RULE COMPILER — FACILITY
# =====================================================================

def render_facility_compiler():
    st.caption("Fill in only the conditions your rule needs. Leave everything else blank — every filled condition is combined with AND.")
    st.write("")

    # ── ORDER DETAILS ─────────────────────────────────────────────
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### 📦 Order Details")
    st.caption("Channel, payment, inventory check, and third party shipping.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Channel Code**")
        fac_use_channel = st.checkbox("Apply Channel Code Filter", key="fac_use_channel",
            help="Single value → `== 'SHOPIFY'`\nMultiple (comma-separated) → `equalsAny('SHOPIFY','FLIPKART')`\n\nEnable case-insensitive if casing varies in your Uniware tenant.")
        fac_channel_val = ""
        fac_channel_icase = False
        fac_channel_strip = False
        if fac_use_channel:
            fac_channel_val = st.text_input("Channel Code(s)", key="fac_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
            fac_channel_icase = st.checkbox("Case-Insensitive Match", key="fac_channel_icase",
                help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple.")
            fac_channel_strip = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="fac_channel_strip",
                help="Removes all spaces from the channel code before comparing. Use if the source may contain accidental spaces.")
    with col2:
        st.markdown("**Inventory Criteria** &nbsp; *(Not sure which? hover ❓)*", help=(
            "NO FILTER — Don't check stock at all.\n\n"
            "SHORT TERM — At least 1 item has stock ready to ship now.\n\n"
            "COMPLETE SHORT TERM ⭐ — ALL items have stock ready to ship now. Most commonly used.\n\n"
            "COMPLETE MID TERM — ALL items have stock arriving soon (few days).\n\n"
            "COMPLETE LONG TERM — ALL items have reserved/planned stock.\n\n"
            "COMPLETE INVENTORY — ALL items have stock in any state.\n\n"
            "FULFILLABLE — ALL items have non-blocked, pickable stock.\n\n"
            "INVENTORY — Some stock exists. Very loose — use as fallback only.\n\n"
            "LIVE INVENTORY — Stock is live and synced to channels.\n\n"
            "LONG TERM — At least 1 item has reserve/long-term stock.\n\n"
            "MAX ORDER CAPACITY — Facility hasn't hit its daily order cap."
        ))
        fac_inv = st.radio("", [
            "NONE","hasShortTermInventory","hasCompleteShortTermInventory","hasCompleteLongTermInventory",
            "hasCompleteInventory","hasFulfillableInventory","hasInventory","hasLiveInventory",
            "hasLongTermInventory","hasCompleteMidTermInventory","hasAllocationWithinMaxOrderCapacity"],
            format_func=lambda x: {
                "NONE":                                "No Filter",
                "hasShortTermInventory":               "Short Term",
                "hasCompleteShortTermInventory":       "Complete Short Term ⭐",
                "hasCompleteLongTermInventory":        "Complete Long Term",
                "hasCompleteInventory":                "Complete Inventory",
                "hasFulfillableInventory":             "Fulfillable",
                "hasInventory":                        "Has Inventory",
                "hasLiveInventory":                    "Live Inventory",
                "hasLongTermInventory":                "Long Term",
                "hasCompleteMidTermInventory":         "Complete Mid Term",
                "hasAllocationWithinMaxOrderCapacity": "Max Order Capacity",
            }.get(x, x), key="fac_inv", index=0, label_visibility="collapsed"
        )



    st.markdown('</div>', unsafe_allow_html=True)

    # ── DELIVERY LOCATION ─────────────────────────────────────────
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### 📍 Delivery Location")
    st.caption("State, pincode, city, and country.")
    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("**State Code**")
        fac_use_state = st.checkbox("Apply State Code Filter", key="fac_use_state",
            help="Select a country to load its states, then pick one or more.\n\nSingle → `== 'MH'` | Multiple → `equalsAny('MH','GJ')`")
        fac_state_val = ""
        if fac_use_state:
            fac_sc = st.selectbox("Country (to load states)", options=ALL_COUNTRY_OPTIONS,
                format_func=lambda x: "— Select country —" if x == "" else COUNTRY_OPTIONS[x], key="fac_state_cc",
                help="Select the country whose state list you want to use.")
            fac_sel_states = []
            if fac_sc:
                fac_sel_states = st.multiselect("State(s)", options=get_state_options(fac_sc), key="fac_state_multi",
                    help="Type to search. Select one or multiple states.")
            fac_state_val = ",".join(extract_state_codes(fac_sel_states))
    with col4:
        st.markdown("**Pincode**")
        fac_use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode",
            help="What it is: Restricts this rule to orders being delivered to specific pincodes.\n\nHow it helps: Useful for hyper-local routing — e.g. send orders within certain pincodes to a nearby dark store or quick-commerce facility.\n\nYou can type pincodes manually or upload a file if you have many.")
        fac_pincode_val = ""
        fac_pincode_rules = []
        if fac_use_pincode:
            fac_pin_mode = st.radio("How do you want to enter pincodes?",
                ["Type manually", "Upload file (for large lists)"],
                horizontal=True, key="fac_pin_mode",
                help="Type manually: best for up to ~40 pincodes\nUpload file: for larger lists — the tool will automatically split them into multiple rules of 40 pincodes each, since a single rule can only handle around 40 pincodes reliably.")
            if fac_pin_mode == "Type manually":
                fac_pincode_val = st.text_area("Pincode(s)", key="fac_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80,
                    help="Enter one pincode or many separated by commas. All must be 6 digits.")
            else:
                with st.expander("📄 How to prepare your CSV / TXT file", expanded=False):
                    st.markdown(
                        "**Option 1 — One pincode per line (recommended):**\n"
                        "```\n560001\n560002\n560003\n400001\n```\n\n"
                        "**Option 2 — Comma separated:**\n"
                        "```\n560001, 560002, 560003, 400001\n```\n\n"
                        "**Rules:**\n"
                        "- Every pincode must be exactly **6 digits**\n"
                        "- No headers needed — just the pincodes\n"
                        "- Invalid values (letters, 5-digit, 7-digit) are skipped automatically and shown as a warning\n"
                        "- The tool splits them into groups of **40 pincodes per rule** automatically\n"
                        "- Save as `.csv` or `.txt` before uploading"
                    )
                    import io as _io
                    fac_pin_template = _io.StringIO()
                    fac_pin_template.write("pincode\n")
                    for p in ["560001","560002","560003","400001","400002","110001","110002"]:
                        fac_pin_template.write(f"{p}\n")
                    st.download_button(
                        label="⬇️ Download Pincode Template CSV",
                        data=fac_pin_template.getvalue(),
                        file_name="pincode_template.csv",
                        mime="text/csv",
                        key="fac_pin_template_dl",
                        help="Download this template, replace the sample pincodes with your own, and upload it."
                    )
                    st.caption("💡 Tip: you can also just use a plain .txt file with one pincode per line — no headers needed.")
                st.caption("Upload a CSV or TXT file — one pincode per line or comma-separated.")
                pin_file = st.file_uploader("Upload pincode file", type=["csv","txt"], key="fac_pin_file",
                    help="One pincode per line or comma-separated. Invalid entries are skipped. Rules are auto-split into groups of 40.")
                if pin_file:
                    raw = pin_file.read().decode("utf-8", errors="ignore")
                    all_pins = [p.strip() for p in re.split(r'[\n,]+', raw) if re.match(r'^\d{6}$', p.strip())]
                    bad_pins = [p.strip() for p in re.split(r'[\n,]+', raw) if p.strip() and not re.match(r'^\d{6}$', p.strip())]
                    if bad_pins:
                        st.warning(f"⚠️ Skipped {len(bad_pins)} invalid value(s): {', '.join(bad_pins[:10])}{'...' if len(bad_pins)>10 else ''}")
                    if all_pins:
                        CHUNK = 40
                        chunks = [all_pins[i:i+CHUNK] for i in range(0, len(all_pins), CHUNK)]
                        fac_pincode_rules = chunks
                        st.success(f"✅ Loaded {len(all_pins)} valid pincodes — will generate {len(chunks)} rule(s) of up to {CHUNK} pincodes each.")
                        fac_pincode_val = ",".join(all_pins)


    st.write("")
    col5, col6 = st.columns(2)
    with col5:
        fac_use_city, fac_city_val = city_multiselect("fac")
    with col6:
        st.markdown("**Payment Method**")
        fac_use_payment = st.checkbox("Apply Payment Method Filter", key="fac_use_payment",
            help="Restricts to COD or Prepaid orders.\n\nGenerates: `#saleOrder.paymentMethod.code == 'COD'`\n\nUseful for routing COD orders to facilities with cash-handling capability.")
        fac_payment_val = ""
        if fac_use_payment:
            fac_payment_val = st.selectbox("Payment Method", ["PREPAID","COD"], key="fac_payment_val",
                help="PREPAID = online/card/UPI paid | COD = cash on delivery")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── PRODUCT ───────────────────────────────────────────────────
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown("#### 🏷️ Product")
    st.caption("SKU, tags, brand, bundle SKU, and destination country.")
    st.divider()

    col7, col8 = st.columns(2)
    with col7:
        fac_use_country, fac_country_val, fac_country_mode = country_selectbox("fac")
    with col8:
        st.markdown("**SKU Code (Item Type SKU)**")
        fac_use_sku = st.checkbox("Apply SKU Code Filter", key="fac_use_sku",
            help=(
                "What it is: Filters based on the SKU code of the product's item type in Uniware.\n\n"
                "How it helps: Route orders containing specific products to a particular facility.\n\n"
                "Single SKU → checks if at least one item in the order has that SKU\n"
                "Multiple SKUs → same check across all entered SKUs\n\n"
                "Uses `itemType.skuCode` — the correct field for SKU matching in Uniware allocation rules.\n\n"
                "For bundle/combo products: enter the component SKU codes — "
                "Uniware exposes component items as individual order items with their own `itemType.skuCode`."
            )
        )
        fac_sku_val = ""
        if fac_use_sku:
            fac_sku_val = st.text_area("SKU Code(s)", key="fac_sku_val",
                placeholder="Single: SKU001  |  Multiple: SKU001, SKU002, SKU003", height=80,
                help="Enter the exact SKU code(s) as configured in the Uniware item master. Case-sensitive.")

    st.write("")
    col_fac_bundle1, col_fac_bundle2 = st.columns(2)
    with col_fac_bundle1:
        st.markdown("**Bundle SKU Code**")
        fac_use_bundle = st.checkbox("Apply Bundle SKU Code Filter", key="fac_use_bundle",
            help=(
                "What it is: Filters orders that contain a specific bundle/combo product.\n\n"
                "How it helps: Route orders containing a specific bundle SKU to a particular facility.\n\n"
                "Uses `bundleSkuCode` — confirmed from 21 live enabled facility rules.\n\n"
                "Different from regular SKU (itemType.skuCode) — bundle SKU is the code of the parent bundle "
                "and is only present on items that are part of a bundle. "
                "A null check is always applied first to avoid errors on non-bundle items."
            )
        )
        fac_bundle_val = ""
        fac_bundle_notnull_only = False
        if fac_use_bundle:
            fac_bundle_notnull_only = st.checkbox("Just check if any bundle SKU exists (no specific code)", key="fac_bundle_notnull_only",
                help="Matches any order that has at least one bundle item — regardless of which bundle SKU it is.")
            if not fac_bundle_notnull_only:
                fac_bundle_val = st.text_area("Bundle SKU Code(s)", key="fac_bundle_val",
                    placeholder="Single: BUNDLE001  |  Multiple: BUNDLE001, BUNDLE002", height=80,
                    help="Enter exact bundle SKU code(s) as in Uniware item master.")
    with col_fac_bundle2:
        st.write("")

    st.write("")
    col9, col10 = st.columns(2)
    with col9:
        st.markdown("**Item Tag**")
        fac_use_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_tag",
            help=(
                "What it is: Tags are labels you attach to products in the Uniware item master to group them — "
                "e.g. 'Flooring', 'Board', 'Sample', 'Fragile'.\n\n"
                "How it helps: Route orders based on what type of product is in them — "
                "e.g. all Flooring orders go to the Flooring facility, Board orders go to Board facility.\n\n"
                "Two levels available:\n"
                "• Order level — checks if ANY item in the whole order has this tag. "
                "Entire order goes to one facility. Does NOT split mixed-tag orders.\n"
                "• SKU level (item level) — checks each item individually. "
                "Enables splitting — Flooring items go to Flooring facility, "
                "Board items go to Board facility, even within the same order.\n\n"
                "Use SKU level if you want mixed-tag orders to split across facilities."
            )
        )
        fac_tag_val = ""
        fac_tag_level = "order"
        fac_tag_mode = "single"
        if fac_use_tag:
            fac_tag_level = st.radio(
                "Tag is applied at:",
                ["order", "sku"],
                format_func=lambda x: {
                    "order": "📦 Order level — route the whole order based on any item's tag",
                    "sku":   "🔖 SKU level — route each item individually by its own tag (enables splitting)"
                }[x],
                key="fac_tag_level",
                horizontal=True,
                help=(
                    "📦 Order level: if ANY item in the order has this tag, the ENTIRE order goes to this facility.\n"
                    "Use when all items in an order always share the same tag.\n\n"
                    "🔖 SKU level: each item is checked individually. Only items with this tag go to this facility.\n"
                    "Use when a single order can have items with DIFFERENT tags (e.g. Flooring + Board) "
                    "and you want them to split into separate facilities.\n\n"
                    "⚠️ For SKU-level splitting to work, make sure 'Allow Splitting' is enabled "
                    "in the facility allocation settings for this tenant."
                )
            )

            if fac_tag_level == "order":
                st.caption("📦 Order level: the whole order goes to this facility if at least one item carries this tag.")
                fac_tag_val = st.text_input(
                    "Tag Value(s)",
                    key="fac_tag_val",
                    placeholder="Single: Flooring  |  Multiple (generates one rule each): Flooring, Board, Sample",
                    help="Enter one tag for one rule, or multiple comma-separated tags to generate one rule per tag automatically."
                )
                fac_tag_mode = "single" if len([t.strip() for t in fac_tag_val.split(",") if t.strip()]) <= 1 else "multi"

            else:
                st.caption(
                    "🔖 SKU level: each item is evaluated individually — enables order splitting across facilities.\n"
                    "Enter multiple tags to generate one rule per tag (e.g. Flooring, Board, Sample → 3 rules)."
                )
                fac_tag_val = st.text_input(
                    "Tag Value(s) — comma-separated for multiple rules",
                    key="fac_tag_val",
                    placeholder="Single: Flooring  |  Multiple: Flooring, Board, Sample",
                    help=(
                        "Single tag → generates 1 rule using #saleOrderItem.itemType.hasAnyTag('Flooring')\n"
                        "Multiple tags → generates one complete rule per tag, all other conditions (channel, pincode etc.) "
                        "are identical across all rules. Copy each rule separately into Uniware."
                    )
                )
                fac_tag_mode = "single" if len([t.strip() for t in fac_tag_val.split(",") if t.strip()]) <= 1 else "multi"

                if fac_tag_mode == "multi":
                    tag_list_preview = [t.strip() for t in fac_tag_val.split(",") if t.strip()]
                    st.info(
                        f"✅ {len(tag_list_preview)} tags entered — will generate **{len(tag_list_preview)} rules** "
                        f"({', '.join(tag_list_preview)}). "
                        "Each rule routes items with that specific tag to this facility."
                    )

    with col10:
        st.markdown("**Brand (contains match)**")
        fac_use_brand = st.checkbox("Apply Brand Filter", key="fac_use_brand",
            help="Checks if any order item belongs to a brand whose name contains the given text.\n\nGenerates: `#saleOrder.saleOrderItems.^[itemType.brand.contains('BRAND')] != null`\n\nPartial/contains match — not exact.")
        fac_brand_val = ""
        if fac_use_brand:
            fac_brand_val = st.text_input("Brand Name", key="fac_brand_val", placeholder="e.g. Trend Arrest")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── ADVANCED ──────────────────────────────────────────────────
    st.markdown('<div class="section-box-grey">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Advanced")
    st.caption("Custom fields and item-level conditions. Use when standard fields aren't enough.")
    st.divider()

    col11a, col12a = st.columns(2)
    with col11a:
        st.markdown("**Third Party Shipping**")
        fac_use_tps = st.checkbox("Apply Third Party Shipping Filter", key="fac_use_tps",
            help=(
                "What it is: Third Party Shipping means the customer has chosen their own courier "
                "or the order is being shipped via a courier arranged outside of Uniware's standard flow "
                "(e.g. Shopify-managed shipping).\n\n"
                "How it helps: Lets you route third-party shipping orders to a specific facility, "
                "or exclude them from certain facilities entirely.\n\n"
                "Confirmed valid field from live production rules — used as:\n"
                "• Is third party shipping → `#saleOrder.thirdPartyShipping`\n"
                "• Is NOT third party shipping → `!#saleOrder.thirdPartyShipping`"
            )
        )
        fac_tps_value = "true"
        if fac_use_tps:
            fac_tps_value = st.radio(
                "Condition",
                ["true", "false"],
                format_func=lambda x: {
                    "true":  "✅ Is Third Party Shipping — order uses a third-party / self-arranged courier",
                    "false": "🚫 Is NOT Third Party Shipping — order uses standard Uniware courier flow"
                }[x],
                horizontal=True,
                key="fac_tps_value",
                help=(
                    "True: matches orders where the customer or channel has arranged their own shipping\n"
                    "False: matches orders going through the normal courier allocation in Uniware\n\n"
                    "Most common use: route third-party shipping orders to a dedicated facility "
                    "or exclude them from facilities that only handle standard courier orders."
                )
            )
    with col12a:
        st.write("")

    st.write("")
    col11, col12 = st.columns(2)
    with col11:
        st.markdown("**Custom Field (Order Level)**")
        fac_use_cf = st.checkbox("Apply Order-Level Custom Field Filter", key="fac_use_cf",
            help="What it is: Extra data fields that come along with an order from your sales channel (like Shopify tags, delivery type, or on-hold flags).\n\nHow it helps: Lets you route orders based on special information that doesn't have a standard field in Uniware — for example, routing all 'express' tagged orders to a specific facility.\n\nThe field name must match exactly what is set up in Uniware for your tenant.")
        fac_cf_field = ""
        fac_cf_match = "contains"
        fac_cf_value = ""
        fac_cf_strip = False
        if fac_use_cf:
            fac_cf_field = st.text_input("Custom Field Name", key="fac_cf_field",
                placeholder="e.g. Tags  or  Omni  or  OnHold")
            fac_cf_match = st.selectbox("How should the field be matched?",
                ["contains","equalsIgnoreCase","not_null"],
                format_func=lambda x: {"contains":"🔍 Contains — the field has this word somewhere in it","equalsIgnoreCase":"✅ Exactly Equals — the field is precisely this value","not_null":"📌 Just Exists — any value in the field is enough"}[x],
                key="fac_cf_match",
                help="Contains: best for tags — e.g. Tags field = 'express, prepaid' and you check for 'express'\nExactly Equals: when the field must be one specific value, e.g. Omni field = 'false'\nJust Exists: when you only care the field is filled in, not what it says")
            if fac_cf_match != "not_null":
                fac_cf_value = st.text_input("Value to match against", key="fac_cf_value",
                    placeholder="e.g. express  or  employee_delight60  or  false")
            if fac_cf_match in ("contains","equalsIgnoreCase"):
                fac_cf_strip = st.checkbox("Ignore spaces in the field value", key="fac_cf_strip",
                    help="Removes all spaces from the field value before comparing. Useful when the channel sometimes sends values with accidental spaces — e.g. 'express delivery' vs 'expressdelivery'.")

    with col12:
        st.markdown("**Custom Field (Order Item Level)**")
        fac_use_soi_cf = st.checkbox("Apply Order Item-Level Custom Field Filter", key="fac_use_soi_cf",
            help="What it is: Same as the order-level custom field above, but applied to each individual item in the order (SOI = Sale Order Item) rather than the whole order.\n\nHow it helps: Lets you route orders based on properties attached to specific products — for example, a product that has a custom 'bonkers3' tag set on it at the item level.\n\nImportant: For this to work, you must also add a custom field mapping in the Channel Configuration (see the note that appears below when you enable this).")
        fac_soi_cf_field = ""
        fac_soi_cf_value = ""
        if fac_use_soi_cf:
            fac_soi_cf_field = st.text_input("Custom Field Name (item level)", key="fac_soi_cf_field",
                placeholder="e.g. custom  or  product_type  or  delivery_tag")
            fac_soi_cf_value = st.text_input("Value to match against (exact match)", key="fac_soi_cf_value",
                placeholder="e.g. bonkers3  or  express  or  fragile")
            st.info(
                "⚙️ **Channel Configuration Required**\n\n"
                "For item-level custom field rules to work, you must add the following mapping in the channel's "
                "**Additional Custom Field Mapping** section in Uniware channel configuration. "
                f"Replace `custom` in the JSON below with your actual field name (`{fac_soi_cf_field.strip() or 'your_field_name'}`):\n\n"
                "```json\n"
                '[\n'
                '  {\n'
                f'    "{fac_soi_cf_field.strip() or "custom"}": "#{{#saleOrderItem?.get(\'properties\')!=null ? ( #saleOrderItem.get(\'properties\').^[ get(\'name\')!=null and get(\'name\').getAsString().equals(\'{fac_soi_cf_field.strip() or "custom"}\') ] != null ?#saleOrderItem.get(\'properties\').^[ get(\'name\')!=null and get(\'name\').getAsString().equals(\'{fac_soi_cf_field.strip() or "custom"}\')].get(\'value\').getAsString() : \'\') : \'\'}}"\n'
                '  }\n'
                ']\n'
                "```\n\n"
                f"This mapping tells Uniware to read the item property named `{fac_soi_cf_field.strip() or 'custom'}` from the channel and make it available as a custom field on `itemType`.\n\n"
                "**Field path used in rule:** `getCustomFieldValue(#saleOrderItem.itemType, 'field')` — confirmed from live production rules."
            )

    st.write("")

    st.markdown('</div>', unsafe_allow_html=True)
    st.write("")

    if st.button("⚙️ Compile Facility Rule", type="primary", key="fac_compile"):
        warnings_list = []
        if fac_use_channel and fac_channel_val.strip():
            validate_inputs(warnings_list, "Channel Code", fac_channel_val, "channel")
        if fac_use_pincode and fac_pincode_val.strip():
            validate_inputs(warnings_list, "Pincode", fac_pincode_val, "pincode")
        if warnings_list:
            st.warning("⚠️ **Please review before using this rule:**")
            for w in warnings_list: st.markdown(f"- {w}")
            st.write("")

        parts = []
        if fac_use_channel and fac_channel_val.strip():
            e = smart_format_string(fac_channel_val, "#saleOrder.channel.code", fac_channel_icase, fac_channel_strip)
            if e: parts.append(e)
        if fac_inv != "NONE":
            parts.append(f"#allocationCriteria.{fac_inv}()")
        if fac_use_state and fac_state_val.strip():
            e = format_multi_value_condition(fac_state_val, "#saleOrderItem.shippingAddress.stateCode")
            if e: parts.append(e)
        if fac_use_pincode and fac_pincode_val.strip():
            e = format_multi_value_condition(fac_pincode_val, "#saleOrderItem.shippingAddress.pincode")
            if e: parts.append(e)
        if fac_use_city and fac_city_val.strip():
            e = format_multi_value_condition(fac_city_val, "#saleOrderItem.shippingAddress.city")
            if e: parts.append(e)
        if fac_use_payment and fac_payment_val:
            parts.append(f"#saleOrder.paymentMethod.code == '{fac_payment_val}'")
        if fac_use_country and fac_country_val.strip():
            e = format_not_equals_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode") if fac_country_mode == "not_equals" else format_multi_value_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode")
            if e: parts.append(e)
        if fac_use_sku and fac_sku_val.strip():
            sku_items = csv_items(fac_sku_val)
            if sku_items:
                quoted = ", ".join(f"'{v}'" for v in sku_items)
                parts.append(
                    f"#saleOrder.saleOrderItems.?["
                    f"T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {quoted})"
                    f"].size() > 0"
                )
        if fac_use_bundle:
            if fac_bundle_notnull_only:
                parts.append("#saleOrder.saleOrderItems.^[bundleSkuCode != null] != null")
            elif fac_bundle_val.strip():
                bundle_items = csv_items(fac_bundle_val)
                if bundle_items:
                    quoted_b = ", ".join(f"'{v}'" for v in bundle_items)
                    parts.append(
                        f"#saleOrder.saleOrderItems.^["
                        f"bundleSkuCode != null and "
                        f"T(com.unifier.core.utils.StringUtils).equalsAny(bundleSkuCode, {quoted_b})"
                        f"] != null"
                    )
        if fac_use_tag and fac_tag_val.strip():
            tag_items = [t.strip() for t in fac_tag_val.split(",") if t.strip()]
            if fac_tag_level == "order":
                # Order level — whole order check — one condition per tag joined with OR if multiple,
                # but since each facility rule should handle one tag, generate one rule per tag
                for tag in tag_items:
                    parts.append(f"#saleOrder.saleOrderItems.^[itemType.hasAnyTag('{tag}')] != null")
            else:
                # SKU level — item-level check — one rule per tag generated at output stage
                # Store tags for multi-rule output below
                pass  # handled in output section
        if fac_use_brand and fac_brand_val.strip():
            parts.append(f"#saleOrder.saleOrderItems.^[itemType.brand.contains('{fac_brand_val.strip()}')] != null")
        if fac_use_tps:
            if fac_tps_value == "true":
                parts.append("#saleOrder.thirdPartyShipping")
            else:
                parts.append("!#saleOrder.thirdPartyShipping")
        if fac_use_cf and fac_cf_field.strip():
            cf_fn = fac_cf_field.strip()
            cf_val = fac_cf_value.strip() if fac_cf_value else ""
            cf_g = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrder, '{cf_fn}')"
            cf_e = f'{cf_g}.replace(" ", "")' if fac_cf_strip else cf_g
            if fac_cf_match == "contains": parts.append(f"{cf_g} != null and {cf_e}.contains('{cf_val}')")
            elif fac_cf_match == "equalsIgnoreCase": parts.append(f"{cf_e}.equalsIgnoreCase('{cf_val}')")
            elif fac_cf_match == "not_null": parts.append(f"{cf_g} != null")
        if fac_use_soi_cf and fac_soi_cf_field.strip() and fac_soi_cf_value.strip():
            soi_fn  = fac_soi_cf_field.strip()
            soi_val = fac_soi_cf_value.strip()
            soi_g   = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrderItem.itemType, '{soi_fn}')"
            parts.append(f"{soi_g} != null")
            parts.append(f"{soi_g}.equals('{soi_val}')")

        if not parts and not fac_pincode_rules and not (fac_use_tag and fac_tag_val.strip() and fac_tag_level == "sku"):
            st.error("Please select at least one condition and provide a value.")
        else:
            # ── Determine tag items for SKU-level mode ───────────────
            sku_tag_items = []
            if fac_use_tag and fac_tag_val.strip() and fac_tag_level == "sku":
                sku_tag_items = [t.strip() for t in fac_tag_val.split(",") if t.strip()]

            # ── Case 1: SKU-level multi-tag — one rule per tag ───────
            if sku_tag_items:
                # For each tag, combine with pincode chunks if bulk pincodes exist
                if fac_pincode_rules and len(fac_pincode_rules) > 1:
                    total = len(sku_tag_items) * len(fac_pincode_rules)
                    st.success(
                        f"✅ Generated {total} rule(s) — "
                        f"{len(sku_tag_items)} tag(s) × {len(fac_pincode_rules)} pincode group(s). "
                        "Copy each rule separately into Uniware:"
                    )
                    for tag in sku_tag_items:
                        st.markdown(f"##### 🏷️ Tag: `{tag}`")
                        for i, chunk in enumerate(fac_pincode_rules, 1):
                            tag_parts = list(parts)
                            quoted = ", ".join(f"'{p}'" for p in chunk)
                            if len(chunk) == 1:
                                tag_parts.append(f"#saleOrderItem.shippingAddress.pincode == '{chunk[0]}'")
                            else:
                                tag_parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrderItem.shippingAddress.pincode, {quoted})")
                            tag_parts.append(f"#saleOrderItem.itemType.hasAnyTag('{tag}')")
                            with st.expander(f"{tag} — Pincode group {i} of {len(fac_pincode_rules)} ({len(chunk)} pincodes)", expanded=(i == 1)):
                                st.code("#{\n  " + " and\n  ".join(tag_parts) + "\n}", language="java")
                else:
                    st.success(
                        f"✅ Generated {len(sku_tag_items)} rule(s) — one per tag. "
                        "Copy each rule separately into Uniware, pointing each to its own facility:"
                    )
                    st.info(
                        "🔖 These are **SKU-level rules** — each item in an order is evaluated individually. "
                        "Orders with mixed tags (e.g. Flooring + Board items) will split across facilities automatically, "
                        "provided splitting is enabled in the tenant's facility allocation settings."
                    )
                    for tag in sku_tag_items:
                        tag_parts = list(parts)
                        tag_parts.append(f"#saleOrderItem.itemType.hasAnyTag('{tag}')")
                        with st.expander(f"🏷️ Rule for tag: {tag}", expanded=True):
                            st.caption(f"Point this rule to the **{tag} facility** in Uniware.")
                            st.code("#{\n  " + " and\n  ".join(tag_parts) + "\n}", language="java")

            # ── Case 2: Bulk pincodes only (no SKU-level tag) ────────
            elif fac_pincode_rules and len(fac_pincode_rules) > 1:
                st.success(f"✅ Generated {len(fac_pincode_rules)} rule(s) — copy each one separately into Uniware:")
                for i, chunk in enumerate(fac_pincode_rules, 1):
                    chunk_parts = list(parts)
                    quoted = ", ".join(f"'{p}'" for p in chunk)
                    if len(chunk) == 1:
                        chunk_parts.append(f"#saleOrderItem.shippingAddress.pincode == '{chunk[0]}'")
                    else:
                        chunk_parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrderItem.shippingAddress.pincode, {quoted})")
                    with st.expander(f"Rule {i} of {len(fac_pincode_rules)} — {len(chunk)} pincodes", expanded=(i == 1)):
                        st.code("#{\n  " + " and\n  ".join(chunk_parts) + "\n}", language="java")

            # ── Case 3: Single rule ───────────────────────────────────
            else:
                st.success("✅ Rule compiled successfully")
                st.code("#{\n  " + " and\n  ".join(parts) + "\n}", language="java")

# =====================================================================
# ⚙️ RULE COMPILER — SHIPPING PROVIDER
# =====================================================================

def render_shipping_compiler():
    st.caption("Toggle Reverse Pickup ON for returns/RTO rules. Leave OFF for standard forward shipments.")
    st.write("")

    st.markdown("""
<div style='margin-bottom:1rem'>
<p style='font-size:0.78rem;font-weight:600;letter-spacing:0.04em;text-transform:uppercase;color:#6366f1;margin-bottom:8px'>Select Rule Type</p>
</div>
""", unsafe_allow_html=True)
    sp_rule_type = st.radio(
        "Rule Type",
        ["forward", "reverse"],
        format_func=lambda x: {
            "forward": "🚚  Forward Shipment — Standard outbound order courier selection",
            "reverse": "🔄  Reverse Pickup — Return / RTO courier selection"
        }[x],
        horizontal=True,
        key="sp_rule_type",
        label_visibility="collapsed",
        help=(
            "Forward Shipment: builds a rule using #shippingPackage — for selecting which courier ships an outbound order to the customer.\n\n"
            "Reverse Pickup: builds a rule using #reversePickup — for selecting which courier picks up a return or RTO from the customer.\n\n"
            "These two use completely different SpEL variables. Mixing them will cause a runtime error."
        )
    )
    is_reverse = sp_rule_type == "reverse"

    if is_reverse:
        st.markdown("""<div style='background:rgba(245,158,11,0.07);border:1px solid rgba(245,158,11,0.25);border-radius:10px;padding:8px 14px;margin-bottom:1rem;font-size:0.78rem;color:#d97706'>
        🔄 &nbsp;<strong>Reverse Pickup mode</strong> — all fields below use <code>#reversePickup</code> context
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.15);border-radius:10px;padding:8px 14px;margin-bottom:1rem;font-size:0.78rem;color:#6366f1'>
        🚚 &nbsp;<strong>Forward Shipment mode</strong> — all fields below use <code>#shippingPackage</code> context
        </div>""", unsafe_allow_html=True)

    st.write("")

    if is_reverse:
        st.markdown("##### 🔄 Reverse Pickup Conditions")
        st.write("")

        # ── ORDER DETAILS ─────────────────────────────────────────
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown("#### 📦 Order Details")
        st.caption("Channel, payment method, and return package weight.")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Return Channel Code**")
            rev_channel_val = st.text_input("Return Channel Code(s)", key="rev_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: SHOPIFY, CUSTOM",
                help="Channel code of the original order being returned.\n\nAlways uses case-insensitive matching for reverse pickup.\n\nSingle → `equalsIgnoreCase('SHOPIFY')` | Multiple → `equalsIgnoreCaseAny(...)`")
        with col2:
            st.markdown("**Box Weight (grams)**")
            rev_use_weight = st.checkbox("Apply Box Weight Filter", key="rev_use_weight",
                help="Uses `#reversePickup.boxWeight` with exclusive bounds on BOTH sides.\n\nMin → `> value` | Max → `< value`\n\nExample: Min=0, Max=4999 → `(#reversePickup.boxWeight > 0 and #reversePickup.boxWeight < 4999)`")
            rev_weight_min = rev_weight_max = ""
            if rev_use_weight:
                rev_weight_min = st.text_input("Min Box Weight — exclusive > (blank = no lower bound)", key="rev_weight_min", placeholder="e.g. 0").strip()
                rev_weight_max = st.text_input("Max Box Weight — exclusive < (blank = no upper bound)", key="rev_weight_max", placeholder="e.g. 4999").strip()

        st.markdown('</div>', unsafe_allow_html=True)

        # ── PICKUP LOCATION ───────────────────────────────────────
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown("#### 📍 Pickup Location")
        st.caption("Where the return is being picked up from.")
        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**State Code**")
            rev_use_state = st.checkbox("Apply State Code Filter", key="rev_use_state",
                help="Uses: `#reversePickup.shippingAddress.stateCode`")
            rev_state_val = ""
            if rev_use_state:
                rev_sc = st.selectbox("Country (to load states)", options=ALL_COUNTRY_OPTIONS,
                    format_func=lambda x: "— Select country —" if x=="" else COUNTRY_OPTIONS[x], key="rev_state_cc")
                rev_sel = []
                if rev_sc:
                    rev_sel = st.multiselect("State(s)", options=get_state_options(rev_sc), key="rev_state_multi",
                        help="Type to search. Select one or multiple states.")
                rev_state_val = ",".join(extract_state_codes(rev_sel))
        with col4:
            st.markdown("**Pincode**")
            rev_use_pincode = st.checkbox("Apply Pincode Filter", key="rev_use_pincode",
                help="Uses: `#reversePickup.shippingAddress.pincode`")
            rev_pincode_val = ""
            if rev_use_pincode:
                rev_pincode_val = st.text_area("Pincode(s)", key="rev_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80)

        st.write("")
        col5, col6 = st.columns(2)
        with col5:
            rev_use_city, rev_city_val = city_multiselect("rev", label="City")
        with col6:
            st.markdown("**Payment Method**")
            rev_use_payment = st.checkbox("Apply Payment Method Filter", key="rev_use_payment",
                help="Generates: `#reversePickup.saleOrder.paymentMethod.code == 'COD'`")
            rev_payment_val = ""
            if rev_use_payment:
                rev_payment_val = st.selectbox("Payment Method", ["COD","PREPAID"], key="rev_payment_val")

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("⚙️ Compile Reverse Pickup Rule", type="primary", key="rev_compile"):
            warnings_list = []
            if rev_use_weight:
                if rev_weight_min: validate_inputs(warnings_list, "Min Box Weight", rev_weight_min, "number")
                if rev_weight_max: validate_inputs(warnings_list, "Max Box Weight", rev_weight_max, "number")
            if warnings_list:
                st.warning("⚠️ **Please review:**")
                for w in warnings_list: st.markdown(f"- {w}")
            rev_parts = []
            if rev_channel_val.strip():
                e = smart_format_string(rev_channel_val, "#reversePickup.saleOrder.channel.code", use_ignore_case=True)
                if e: rev_parts.append(e)
            if rev_use_weight:
                if rev_weight_min and rev_weight_max:
                    rev_parts.append(f"(#reversePickup.boxWeight > {rev_weight_min} and #reversePickup.boxWeight < {rev_weight_max})")
                elif rev_weight_min: rev_parts.append(f"#reversePickup.boxWeight > {rev_weight_min}")
                elif rev_weight_max: rev_parts.append(f"#reversePickup.boxWeight < {rev_weight_max}")
            if rev_use_state and rev_state_val.strip():
                e = format_multi_value_condition(rev_state_val, "#reversePickup.shippingAddress.stateCode")
                if e: rev_parts.append(e)
            if rev_use_pincode and rev_pincode_val.strip():
                e = format_multi_value_condition(rev_pincode_val, "#reversePickup.shippingAddress.pincode")
                if e: rev_parts.append(e)
            if rev_use_city and rev_city_val.strip():
                e = format_multi_value_condition(rev_city_val, "#reversePickup.shippingAddress.city")
                if e: rev_parts.append(e)
            if rev_use_payment and rev_payment_val:
                rev_parts.append(f"#reversePickup.saleOrder.paymentMethod.code == '{rev_payment_val}'")
            if not rev_parts:
                st.error("Please provide at least one condition.")
            else:
                st.success("✅ Rule compiled successfully")
                st.code("#{\n  " + " and\n  ".join(rev_parts) + "\n}", language="java")

    else:
        # ── ORDER DETAILS ─────────────────────────────────────────
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown("#### 📦 Order Details")
        st.caption("Channel, payment, weight, and price.")
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Channel Code**")
            sp_use_channel = st.checkbox("Apply Channel Code Filter", key="sp_use_channel",
                help="Single → `#shippingPackage.saleOrder.channel.code == 'SHOPIFY'`\nMultiple → `equalsAny(...)`\n\nEnable case-insensitive if channel code may have inconsistent casing.")
            sp_channel_val = ""
            sp_channel_icase = False
            sp_channel_strip = False
            if sp_use_channel:
                sp_channel_val = st.text_input("Channel Code(s)", key="sp_channel_val",
                    placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
                sp_channel_icase = st.checkbox("Case-Insensitive Match", key="sp_channel_icase",
                    help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple.")
                sp_channel_strip = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="sp_channel_strip",
                    help="Removes all spaces from channel code before comparing.")
        with col2:
            st.markdown("**State Code**")
            sp_use_state = st.checkbox("Apply State Code Filter", key="sp_use_state",
                help="Select a country to load its states, then pick one or more.\n\nUses: `#shippingPackage.shippingAddress.stateCode`")
            sp_state_val = ""
            if sp_use_state:
                sp_sc = st.selectbox("Country (to load states)", options=ALL_COUNTRY_OPTIONS,
                    format_func=lambda x: "— Select country —" if x=="" else COUNTRY_OPTIONS[x], key="sp_state_cc")
                sp_sel = []
                if sp_sc:
                    sp_sel = st.multiselect("State(s)", options=get_state_options(sp_sc), key="sp_state_multi",
                        help="Type to search. Select one or multiple states.")
                sp_state_val = ",".join(extract_state_codes(sp_sel))

        st.markdown('</div>', unsafe_allow_html=True)

        # ── DELIVERY LOCATION ─────────────────────────────────────
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown("#### 📍 Delivery Location")
        st.caption("State, pincode, city, and country.")
        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**Pincode**")
            sp_use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode",
                help="What it is: Restricts courier selection to shipments going to specific delivery pincodes.\n\nHow it helps: Assign different couriers based on serviceability zones — e.g. a local courier for certain pincodes, a national courier for the rest.\n\nNote: a single rule handles up to ~40 pincodes reliably. Use the file upload for larger lists.")
            sp_pincode_val = ""
            sp_pincode_rules = []
            if sp_use_pincode:
                sp_pin_mode = st.radio("How do you want to enter pincodes?",
                    ["Type manually", "Upload file (for large lists)"],
                    horizontal=True, key="sp_pin_mode",
                    help="Type manually: best for up to ~40 pincodes\nUpload file: for larger lists — the tool automatically splits them into multiple rules of 40 pincodes each.")
                if sp_pin_mode == "Type manually":
                    sp_pincode_val = st.text_area("Pincode(s)", key="sp_pincode_val",
                        placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80,
                        help="Enter one pincode or many separated by commas. All must be 6 digits.")
                else:
                    with st.expander("📄 How to prepare your CSV / TXT file", expanded=False):
                        st.markdown(
                            "**Option 1 — One pincode per line (recommended):**\n"
                            "```\n560001\n560002\n560003\n400001\n```\n\n"
                            "**Option 2 — Comma separated:**\n"
                            "```\n560001, 560002, 560003, 400001\n```\n\n"
                            "**Rules:**\n"
                            "- Every pincode must be exactly **6 digits**\n"
                            "- No headers needed — just the pincodes\n"
                            "- Invalid values (letters, 5-digit, 7-digit) are skipped automatically and shown as a warning\n"
                            "- The tool splits them into groups of **40 pincodes per rule** automatically\n"
                            "- Save as `.csv` or `.txt` before uploading"
                        )
                        import io as _io2
                        sp_pin_template = _io2.StringIO()
                        sp_pin_template.write("pincode\n")
                        for p in ["560001","560002","560003","400001","400002","110001","110002"]:
                            sp_pin_template.write(f"{p}\n")
                        st.download_button(
                            label="⬇️ Download Pincode Template CSV",
                            data=sp_pin_template.getvalue(),
                            file_name="pincode_template.csv",
                            mime="text/csv",
                            key="sp_pin_template_dl",
                            help="Download this template, replace the sample pincodes with your own, and upload it."
                        )
                        st.caption("💡 Tip: you can also just use a plain .txt file with one pincode per line — no headers needed.")
                    st.caption("Upload a CSV or TXT file — one pincode per line or comma-separated.")
                    sp_pin_file = st.file_uploader("Upload pincode file", type=["csv","txt"], key="sp_pin_file",
                        help="One pincode per line or comma-separated. Invalid entries are skipped. Rules are auto-split into groups of 40.")
                    if sp_pin_file:
                        raw_sp = sp_pin_file.read().decode("utf-8", errors="ignore")
                        all_sp_pins = [p.strip() for p in re.split(r'[\n,]+', raw_sp) if re.match(r'^\d{6}$', p.strip())]
                        bad_sp_pins = [p.strip() for p in re.split(r'[\n,]+', raw_sp) if p.strip() and not re.match(r'^\d{6}$', p.strip())]
                        if bad_sp_pins:
                            st.warning(f"⚠️ Skipped {len(bad_sp_pins)} invalid value(s): {', '.join(bad_sp_pins[:10])}{'...' if len(bad_sp_pins)>10 else ''}")
                        if all_sp_pins:
                            CHUNK_SP = 40
                            sp_chunks = [all_sp_pins[i:i+CHUNK_SP] for i in range(0, len(all_sp_pins), CHUNK_SP)]
                            sp_pincode_rules = sp_chunks
                            st.success(f"✅ Loaded {len(all_sp_pins)} valid pincodes — will generate {len(sp_chunks)} rule(s) of up to {CHUNK_SP} pincodes each.")
                            sp_pincode_val = ",".join(all_sp_pins)
        with col4:
            st.markdown("**Payment Method**")
            sp_use_payment = st.checkbox("Apply Payment Method Filter", key="sp_use_payment",
                help="Generates: `#shippingPackage.saleOrder.paymentMethod.code == 'COD'`\n\nUseful for assigning dedicated COD couriers.")
            sp_payment_val = ""
            if sp_use_payment:
                sp_payment_val = st.selectbox("Payment Method", ["COD","PREPAID"], key="sp_payment_val")

        st.write("")
        col5, col6 = st.columns(2)
        with col5:
            st.markdown("**Package Weight (grams)**")
            sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight",
                help="Uses: `#shippingPackage.actualWeight`\n\n• Min bound is exclusive (>)\n• Max bound is inclusive (<=)\n\nExample: Min=500, Max=1000 → `actualWeight > 500 and actualWeight <= 1000`\n\nThis asymmetry ensures adjacent weight slabs don't overlap.")
            sp_weight_min = sp_weight_max = ""
            if sp_use_weight:
                sp_weight_min = st.text_input("Min Weight — exclusive > (blank = no lower bound)", key="sp_weight_min", placeholder="e.g. 500").strip()
                sp_weight_max = st.text_input("Max Weight — inclusive <= (blank = no upper bound)", key="sp_weight_max", placeholder="e.g. 1000").strip()
        with col6:
            st.markdown("**Total Order Price**")
            sp_use_price = st.checkbox("Apply Price Filter", key="sp_use_price",
                help="Uses: `#shippingPackage.totalPrice`\n\n• Min bound is exclusive (>)\n• Max bound is inclusive (<=)\n\nUseful for routing high-value orders to insured/premium couriers.")
            sp_price_min = sp_price_max = ""
            if sp_use_price:
                sp_price_min = st.text_input("Min Price — exclusive > (blank = no lower bound)", key="sp_price_min", placeholder="e.g. 0").strip()
                sp_price_max = st.text_input("Max Price — inclusive <= (blank = no upper bound)", key="sp_price_max", placeholder="e.g. 6000").strip()

        st.write("")
        col7, col8 = st.columns(2)
        with col7:
            sp_use_city, sp_city_val = city_multiselect("sp")
        with col8:
            sp_use_country, sp_country_val, sp_country_mode = country_selectbox("sp")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── PRODUCT ───────────────────────────────────────────────
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown("#### 🏷️ Product")
        st.caption("SKU, tags, bundle SKU, item count, and package type.")
        st.divider()

        col9, col10 = st.columns(2)
        with col9:
            st.markdown("**Number of Items in Package**")
            sp_use_items = st.checkbox("Apply Item Count Filter", key="sp_use_items",
                help="Filters by how many line items are in the shipping package.\n\nUses: `#shippingPackage.saleOrderItems.size()`\n\nUseful for assigning different couriers for single-item vs bulk shipments.")
            sp_items_op = "<="
            sp_items_val = ""
            if sp_use_items:
                sp_items_op = st.selectbox("Operator", ["<=","<",">=",">","=="],
                    format_func=lambda x: {"<=":"<= (Up to N items — small/single shipments)","<":"<  (Fewer than N — strictly less)",">=":">= (At least N items — bulk)",">":" >  (More than N — strictly greater)","==":"== (Exactly N items)"}[x],
                    key="sp_items_op",
                    help="• <= : up to N items (e.g. <= 1 for single-item-only couriers)\n• >= : at least N items (bulk threshold)\n• == : exactly N items")
                sp_items_val = st.text_input("Item Count Threshold", key="sp_items_val", placeholder="e.g. 12").strip()
        with col10:
            st.markdown("**Item Tag (hasAnyTag)**")
            sp_use_tag = st.checkbox("Apply Item Tag Filter", key="sp_use_tag",
                help="Checks if any item in the package has a specific tag from the item master.\n\nGenerates: `#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`\n\nUseful for routing packages with tagged items (mattress, furniture) to specialist couriers.")
            sp_tag_val = ""
            if sp_use_tag:
                sp_tag_val = st.text_input("Item Tag Value", key="sp_tag_val", placeholder="e.g. mattress  or  Furniture")

        st.write("")
        col_sku1, col_sku2 = st.columns(2)
        with col_sku1:
            st.markdown("**SKU Code (Item Type SKU)**")
            sp_use_sku = st.checkbox("Apply SKU Code Filter", key="sp_use_sku",
                help=(
                    "What it is: Filters courier selection based on specific product SKUs in the package.\n\n"
                    "How it helps: Assign different couriers for specific products — e.g. heavy/fragile SKUs go to a specialist courier.\n\n"
                    "Uses `itemType.skuCode` — confirmed from 20 live enabled SP rules.\n"
                    "Single or multiple SKUs — all handled the same way."
                )
            )
            sp_sku_val = ""
            if sp_use_sku:
                sp_sku_val = st.text_area("SKU Code(s)", key="sp_sku_val",
                    placeholder="Single: SKU001  |  Multiple: SKU001, SKU002, SKU003", height=80,
                    help="Enter exact SKU code(s) as in Uniware item master. Case-sensitive.")

        with col_sku2:
            st.markdown("**Bundle SKU Code**")
            sp_use_bundle = st.checkbox("Apply Bundle SKU Code Filter", key="sp_use_bundle",
                help=(
                    "What it is: Filters by the bundle/combo SKU code — used when the order contains a product that is part of a bundle.\n\n"
                    "How it helps: Route orders containing specific bundles to a particular courier.\n\n"
                    "Uses `bundleSkuCode` — confirmed from live enabled facility rules.\n"
                    "Add a null check — bundle SKU is only present on bundle items, not regular items."
                )
            )
            sp_bundle_val = ""
            if sp_use_bundle:
                sp_bundle_val = st.text_area("Bundle SKU Code(s)", key="sp_bundle_val",
                    placeholder="Single: BUNDLE001  |  Multiple: BUNDLE001, BUNDLE002", height=80,
                    help="Enter exact bundle SKU code(s). Leave blank to check for any bundle SKU (not null check only).")
                sp_bundle_notnull_only = st.checkbox("Just check if any bundle SKU exists (no specific code)", key="sp_bundle_notnull_only",
                    help="Ticking this will match any package that has a bundle item — regardless of which specific bundle SKU it is.")

        st.write("")
        col_spt1, col_spt2 = st.columns(2)
        with col_spt1:
            st.markdown("**Shipping Package Type**")
            sp_use_spt = st.checkbox("Apply Shipping Package Type Filter", key="sp_use_spt",
                help=(
                    "What it is: Filters by the type/category code assigned to the shipping package in Uniware.\n\n"
                    "How it helps: Route packages of a specific type to a particular courier — e.g. all packages of type 'A15' go to a heavy-goods courier.\n\n"
                    "Uses `#shippingPackage.shippingPackageType.code` — confirmed from live enabled SP rules.\n\n"
                    "The code must match exactly as configured in your Uniware shipping package type master."
                )
            )
            sp_spt_val = ""
            if sp_use_spt:
                sp_spt_val = st.text_input("Shipping Package Type Code", key="sp_spt_val",
                    placeholder="e.g. A15  or  T-R1  or  A3",
                    help="Enter the exact package type code as configured in Uniware. Case-sensitive.")
        with col_spt2:
            st.write("")

        st.markdown('</div>', unsafe_allow_html=True)

        # ── ADVANCED ──────────────────────────────────────────────
        st.markdown('<div class="section-box-grey">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Advanced")
        st.caption("Custom fields from your sales channel.")
        st.divider()

        col11, col12 = st.columns(2)
        with col11:
            st.markdown("**Custom Field**")
            sp_use_cf = st.checkbox("Apply Custom Field Filter", key="sp_use_cf",
                help="Filters by a custom field on the sale order (e.g. Tags, Delivery_Partner, tagsfetched).\n\n• Contains — field has this word somewhere (most common)\n• Exactly Equals — field must be precisely this value\n• Just Exists — field just needs to be present\n\nField Name must match exactly as configured in Uniware.")
            sp_cf_field = sp_cf_match = sp_cf_value = sp_cf_strip = ""
            sp_cf_match = "contains"
            sp_cf_strip = False
            if sp_use_cf:
                sp_cf_field = st.text_input("Custom Field Name (exact key in Uniware)", key="sp_cf_field",
                    placeholder="e.g. Tags  or  Delivery_Partner  or  tagsfetched")
                sp_cf_match = st.selectbox("How should the field be matched?",
                    ["contains","equalsIgnoreCase","not_null"],
                    format_func=lambda x: {"contains":"🔍 Contains — field has this word/value somewhere","equalsIgnoreCase":"✅ Exactly Equals — field is precisely this value","not_null":"📌 Just Exists — any non-empty value is enough"}[x],
                    key="sp_cf_match",
                    help="🔍 Contains: most common — use for Tags which holds multiple comma-separated values\n✅ Exactly Equals: field must be one precise value (e.g. Delivery_Partner == 'DELHIVERY_5KGS')\n📌 Just Exists: field just needs to be present")
                if sp_cf_match != "not_null":
                    sp_cf_value = st.text_input("Value to match against", key="sp_cf_value",
                        placeholder="e.g. Express  or  DELHIVERY_5KGS  or  EDNDDTAG")
                if sp_cf_match in ("contains","equalsIgnoreCase"):
                    sp_cf_strip = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="sp_cf_strip",
                        help="Removes all spaces from field value before comparing. Use when channel may send tags with accidental spaces.")
        with col12:
            st.write("")

        st.markdown('</div>', unsafe_allow_html=True)
        st.write("")
        if st.button("⚙️ Compile Shipping Provider Rule", type="primary", key="sp_compile"):
            warnings_list = []
            if sp_use_channel and sp_channel_val.strip(): validate_inputs(warnings_list, "Channel Code", sp_channel_val, "channel")
            if sp_use_pincode and sp_pincode_val.strip(): validate_inputs(warnings_list, "Pincode", sp_pincode_val, "pincode")
            if sp_use_weight:
                if sp_weight_min: validate_inputs(warnings_list, "Min Weight", sp_weight_min, "number")
                if sp_weight_max: validate_inputs(warnings_list, "Max Weight", sp_weight_max, "number")
            if sp_use_price:
                if sp_price_min: validate_inputs(warnings_list, "Min Price", sp_price_min, "number")
                if sp_price_max: validate_inputs(warnings_list, "Max Price", sp_price_max, "number")
            if sp_use_items and sp_items_val: validate_inputs(warnings_list, "Item Count", sp_items_val, "number")
            if warnings_list:
                st.warning("⚠️ **Please review:**")
                for w in warnings_list: st.markdown(f"- {w}")

            parts = []
            if sp_use_channel and sp_channel_val.strip():
                e = smart_format_string(sp_channel_val, "#shippingPackage.saleOrder.channel.code", sp_channel_icase, sp_channel_strip)
                if e: parts.append(e)
            if sp_use_state and sp_state_val.strip():
                e = format_multi_value_condition(sp_state_val, "#shippingPackage.shippingAddress.stateCode")
                if e: parts.append(e)
            if sp_use_pincode and sp_pincode_val.strip():
                e = format_multi_value_condition(sp_pincode_val, "#shippingPackage.shippingAddress.pincode")
                if e: parts.append(e)
            if sp_use_weight:
                if sp_weight_min: parts.append(f"#shippingPackage.actualWeight > {sp_weight_min}")
                if sp_weight_max: parts.append(f"#shippingPackage.actualWeight <= {sp_weight_max}")
            if sp_use_price:
                if sp_price_min: parts.append(f"#shippingPackage.totalPrice > {sp_price_min}")
                if sp_price_max: parts.append(f"#shippingPackage.totalPrice <= {sp_price_max}")
            if sp_use_payment and sp_payment_val:
                parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{sp_payment_val}'")
            if sp_use_city and sp_city_val.strip():
                e = format_multi_value_condition(sp_city_val, "#shippingPackage.shippingAddress.city")
                if e: parts.append(e)
            if sp_use_country and sp_country_val.strip():
                e = format_not_equals_condition(sp_country_val, "#shippingPackage.shippingAddress.countryCode") if sp_country_mode == "not_equals" else format_multi_value_condition(sp_country_val, "#shippingPackage.shippingAddress.countryCode")
                if e: parts.append(e)
            if sp_use_items and sp_items_val:
                parts.append(f"#shippingPackage.saleOrderItems.size() {sp_items_op} {sp_items_val}")
            if sp_use_tag and sp_tag_val.strip():
                parts.append(f"#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('{sp_tag_val.strip()}')] != null")
            if sp_use_sku and sp_sku_val.strip():
                sku_items = csv_items(sp_sku_val)
                if sku_items:
                    quoted = ", ".join(f"'{v}'" for v in sku_items)
                    parts.append(
                        f"#shippingPackage.saleOrderItems.^["
                        f"T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {quoted})"
                        f"] != null"
                    )
            if sp_use_bundle:
                if sp_bundle_notnull_only:
                    parts.append("#shippingPackage.saleOrderItems.^[bundleSkuCode != null] != null")
                elif sp_bundle_val.strip():
                    bundle_items = csv_items(sp_bundle_val)
                    if bundle_items:
                        quoted_b = ", ".join(f"'{v}'" for v in bundle_items)
                        parts.append(
                            f"#shippingPackage.saleOrderItems.^["
                            f"bundleSkuCode != null and "
                            f"T(com.unifier.core.utils.StringUtils).equalsAny(bundleSkuCode, {quoted_b})"
                            f"] != null"
                        )
            if sp_use_spt and sp_spt_val.strip():
                parts.append(f"#shippingPackage.shippingPackageType.code == '{sp_spt_val.strip()}'")
            if sp_use_cf and sp_cf_field.strip():
                sp_fn = sp_cf_field.strip()
                sp_val = sp_cf_value.strip() if sp_cf_value else ""
                sp_g = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#shippingPackage.saleOrder, '{sp_fn}')"
                sp_e = f'{sp_g}.replace(" ", "")' if sp_cf_strip else sp_g
                if sp_cf_match == "contains": parts.append(f"{sp_g} != null and {sp_e}.contains('{sp_val}')")
                elif sp_cf_match == "equalsIgnoreCase": parts.append(f"{sp_e}.equalsIgnoreCase('{sp_val}')")
                elif sp_cf_match == "not_null": parts.append(f"{sp_g} != null")

            if not parts and not sp_pincode_rules:
                st.error("Please select at least one condition and provide a value.")
            elif sp_pincode_rules and len(sp_pincode_rules) > 1:
                st.success(f"✅ Generated {len(sp_pincode_rules)} rule(s) — copy each one separately into Uniware:")
                for i, chunk in enumerate(sp_pincode_rules, 1):
                    chunk_parts = list(parts)
                    quoted = ", ".join(f"'{p}'" for p in chunk)
                    if len(chunk) == 1:
                        chunk_parts.append(f"#shippingPackage.shippingAddress.pincode == '{chunk[0]}'")
                    else:
                        chunk_parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.shippingAddress.pincode, {quoted})")
                    with st.expander(f"Rule {i} of {len(sp_pincode_rules)} — {len(chunk)} pincodes", expanded=(i==1)):
                        st.code("#{\n  " + " and\n  ".join(chunk_parts) + "\n}", language="java")
            else:
                st.success("✅ Rule compiled successfully")
                st.code("#{\n  " + " and\n  ".join(parts) + "\n}", language="java")

# =====================================================================
# ⚙️ RULE COMPILER — INVENTORY
# =====================================================================

def render_inventory_compiler():
    st.caption("Check the stock pools to include. Base deductions (open sales, pendency, blocked stock) are always applied.")
    st.write("")

    sub_type = st.selectbox("Formula Variant",
        ["DEFAULT","BUFFER_3","BUFFER_1","ZERO_SYNC"],
        format_func=lambda x: {
            "DEFAULT":"Standard — push actual calculated stock",
            "BUFFER_3":"Buffer 3 — push 0 if stock ≤ 3 units",
            "BUFFER_1":"Buffer 1 — push 0 if stock ≤ 1 unit",
            "ZERO_SYNC":"Zero Sync — always push 0 (suppress SKU on channel)"
        }[x], key="inv_sub_type",
        help="• Standard: pushes real available stock\n• Buffer 3/1: safety guard — syncs 0 when stock critically low, avoids overselling\n• Zero Sync: always syncs 0 — used to temporarily delist a SKU without touching actual inventory")

    v_inv = st.checkbox("Include Virtual Inventory", key="calc_v_inv",
        help="Adds `#inventorySnapshot.virtualInventory`.\n\nEnable when channel sync should count virtual/buffer reservation stock in addition to physical stock.")
    v_nd = st.checkbox("Include Vendor / Drop-Ship Inventory", key="calc_v_nd",
        help="Adds `#inventorySnapshot.vendorInventory`.\n\nEnable for channels/SKUs that can be fulfilled from vendor or drop-ship warehouses.")
    unproc = st.checkbox("Deduct Unprocessed Orders (Amazon Flex / Slab Channels)", key="calc_unproc",
        help="Subtracts `#unprocessedOrderInventory`.\n\nUnprocessed orders are placed on the channel but haven't entered Uniware's pipeline — they still consume stock and must be deducted.\n\nCritical for Amazon Flex and batch/slab channel integrations.")

    st.write("")
    if st.button("⚙️ Compile Inventory Formula", type="primary", key="inv_compile"):
        inv_part = "#inventorySnapshot.inventory"
        if v_inv: inv_part += " + #inventorySnapshot.virtualInventory"
        if v_nd:  inv_part += " + #inventorySnapshot.vendorInventory"
        deduct = ("- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) "
                  "- #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment")
        if unproc: deduct += " - #unprocessedOrderInventory"
        core = f"{inv_part} {deduct}"
        if sub_type == "DEFAULT":    out = f"#{{{core}}}"
        elif sub_type == "BUFFER_3": out = f"#{{({core})<=3?0:({core})}}"
        elif sub_type == "BUFFER_1": out = f"#{{({core})<=1?0:({core})}}"
        else:                        out = f"#{{({core})*0}}"
        st.success("✅ Formula compiled successfully")
        st.code(out, language="java")

# =====================================================================
# MAIN LAYOUT — MODULE SELECTOR → TABS
# =====================================================================

# Step 1: Module selector
module = st.selectbox(
    "Select what you want to build",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC", "TOOLS"],
    format_func=lambda x: {
        "FACILITY":       "🏭  Facility Allocation Engine (Warehouse Assignment / Routing Rules)",
        "SHIPPING_FWD":   "🚚  Shipping Provider Allocation Engine (Courier / Logistics Partner Selection)",
        "INVENTORY_CALC": "🛠️  Inventory Synchronization Calculation Formula Wrapper",
        "TOOLS":          "🔧  Tools (Validator · Reverse Compiler · Audit · Anomaly Suggester)"
    }[x],
    help="Select what you want to do:\n\n• Facility Allocation — build a rule deciding which warehouse fulfils an order\n• Shipping Provider — build a rule deciding which courier ships a package\n• Inventory Sync — build a formula for how much stock to push to a channel\n• Tools — validate, decode, audit, or analyse existing rules"
)

st.write("")

# ── Compiler modules ──────────────────────────────────────────────
if module == "FACILITY":
    render_facility_compiler()
elif module == "SHIPPING_FWD":
    render_shipping_compiler()
elif module == "INVENTORY_CALC":
    render_inventory_compiler()

# ── Tools ─────────────────────────────────────────────────────────
elif module == "TOOLS":

    tab_validator, tab_reverse, tab_audit, tab_anomaly = st.tabs([
        "🔍  Rule Validator",
        "🔄  Reverse Compiler",
        "📋  Rule Audit",
        "💡  Anomaly Suggester",
    ])

    # ── Tab 1: Validator ──────────────────────────────────────────
    with tab_validator:
        st.write("")
        st.subheader("🔍 Rule Validator")
        st.caption("Paste any existing Uniware rule and the tool will check it for common mistakes before you use it.")
        st.info(
            "**What it checks:** Missing # on variable names · Spelling mistake in method names · "
            "OR condition not properly wrapped in brackets (this caused a real production issue) · "
            "equalsAny used for a single value · Numbers not quoted · Trailing comma · "
            "Custom field check without null safety · Plain text instead of a rule expression"
        )
        rule_input = st.text_area("Paste your rule here", height=150, key="val_input",
            placeholder="#{#shippingPackage.saleOrder.channel.code == 'SHOPIFY' and #shippingPackage.totalPrice <= 6000}",
            help="Paste the complete rule including the #{ and } at the start and end.")
        if st.button("🔍 Check Rule", type="primary", key="val_btn"):
            if not rule_input.strip():
                st.error("Please paste a rule to check.")
            else:
                issues = check_rule_for_issues(rule_input.strip())
                if not issues:
                    st.success("✅ No issues found. Rule looks good.")
                    st.caption("This check covers common structural mistakes. It cannot verify whether your business conditions are correct or whether values like channel codes exist in your Uniware tenant.")
                else:
                    st.error(f"❌ Found {len(issues)} issue(s):")
                    for i, issue in enumerate(issues, 1):
                        with st.expander(f"{issue['severity']} — Issue {i}", expanded=True):
                            st.markdown(f"**What's wrong:** {issue['message']}")
                            st.markdown(f"**How to fix it:** {issue['fix']}")

    # ── Tab 2: Reverse Compiler ───────────────────────────────────
    with tab_reverse:
        st.write("")
        st.subheader("🔄 Reverse Compiler")
        st.caption("Paste any existing Uniware rule and get a plain-English breakdown of what it does — no technical knowledge needed.")
        rule_input2 = st.text_area("Paste rule to decode", height=150, key="rev_input",
            placeholder="#{T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.channel.code, 'FLIPKART', 'AMAZON_IN') and #allocationCriteria.hasCompleteShortTermInventory()}",
            help="Paste the complete rule. The tool will break it down condition by condition.")
        if st.button("🔄 Decode Rule", type="primary", key="rev_btn"):
            if not rule_input2.strip():
                st.error("Please paste a rule to decode.")
            else:
                decoded = decode_spel(rule_input2.strip())
                if not decoded:
                    st.warning("Could not decode this rule. Please check it is a valid Uniware rule expression.")
                else:
                    st.success(f"✅ This rule has {len(decoded)} condition(s):")
                    for label, value in decoded:
                        c1, c2 = st.columns([1, 2])
                        with c1: st.markdown(f"**{label}**")
                        with c2: st.markdown(f"`{value}`")
                    st.caption("Any condition shown as 'Condition: ...' uses a pattern the decoder doesn't recognise — shown as-is.")

    # ── Tab 3: Rule Audit ─────────────────────────────────────────
    with tab_audit:
        st.write("")
        st.subheader("📋 Rule Audit — Bulk Scanner")
        st.caption("Upload a rule dump CSV from Uniware and scan every rule at once for mistakes — instead of checking them one by one.")

        with st.expander("📄 How to get and prepare the file", expanded=False):
            st.markdown(
                "**Step 1 — Export from Uniware:**\n"
                "- Go to **Facility Allocation** or **Shipping Provider Allocation** in Uniware\n"
                "- Click **Export** → download as CSV\n\n"
                "**Step 2 — What the file must contain:**\n"
                "- A column called exactly `condition_expression` — this is where the rules are stored\n"
                "- Other columns like `name`, `preference`, `enabled` are optional but help identify rules in results\n\n"
                "**Alternatively — build your own CSV:**\n"
                "Download the template below, fill in your rules in the `condition_expression` column, and upload it."
            )
            import io
            template_audit = io.StringIO()
            template_audit.write("name,preference,enabled,condition_expression\n")
            template_audit.write("My Rule 1,1,true,\"#{#saleOrder.channel.code == 'SHOPIFY'}\"\n")
            template_audit.write("My Rule 2,2,true,\"#{#shippingPackage.totalPrice <= 6000}\"\n")
            st.download_button(
                label="⬇️ Download Template CSV",
                data=template_audit.getvalue(),
                file_name="rule_audit_template.csv",
                mime="text/csv",
                help="Download this template, fill in your rules in the condition_expression column, then upload it below."
            )

        uploaded = st.file_uploader("Upload rule dump CSV", type=["csv"], key="audit_upload",
            help="Export from Uniware's Facility or Shipping Provider Allocation screen, or use the template above.")
        if uploaded:
            try:
                import pandas as pd
                df = pd.read_csv(uploaded)
                if 'condition_expression' not in df.columns:
                    st.error("❌ This file doesn't have a `condition_expression` column. Please upload a valid Uniware rule dump.")
                else:
                    st.success(f"✅ Loaded {len(df)} rules. Scanning now...")
                    all_issues = []
                    for idx, row in df.iterrows():
                        expr = str(row.get('condition_expression', ''))
                        if not expr or expr.lower() in ('nan', 'true', ''):
                            continue
                        rule_issues = check_rule_for_issues(expr)
                        if rule_issues:
                            rule_name = str(row.get('name', f'Row {idx+2}'))
                            for issue in rule_issues:
                                all_issues.append({
                                    "Rule": rule_name,
                                    "Severity": issue['severity'],
                                    "Issue": issue['message'][:120],
                                    "Fix": issue['fix'][:100],
                                    "Expression": expr[:100] + "..." if len(expr) > 100 else expr
                                })
                    if not all_issues:
                        st.success("🎉 All rules look clean — no known issues found!")
                    else:
                        critical = sum(1 for i in all_issues if "Critical" in i['Severity'])
                        high     = sum(1 for i in all_issues if "High" in i['Severity'])
                        medium   = sum(1 for i in all_issues if "Medium" in i['Severity'])
                        st.error(f"❌ Found {len(all_issues)} issue(s) across {len(set(i['Rule'] for i in all_issues))} rule(s):")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("🔴 Critical", critical)
                        c2.metric("🟠 High", high)
                        c3.metric("🟡 Medium", medium)
                        st.write("")
                        st.dataframe(pd.DataFrame(all_issues), use_container_width=True)
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # ── Tab 4: Anomaly Suggester ──────────────────────────────────
    with tab_anomaly:
        st.write("")
        st.subheader("💡 Anomaly Suggester")
        st.caption("Upload a rule dump CSV and the tool will flag things that look wrong or incomplete — duplicate rules, missing states, catch-alls in the wrong place, and more.")

        with st.expander("📄 How to get and prepare the file", expanded=False):
            st.markdown(
                "**This tool uses the same file as Rule Audit.**\n\n"
                "**Step 1 — Export from Uniware:**\n"
                "- Go to **Facility Allocation** or **Shipping Provider Allocation** in Uniware\n"
                "- Click **Export** → download as CSV\n\n"
                "**Step 2 — What the file must contain:**\n"
                "- `condition_expression` — required (the rule itself)\n"
                "- `name` — optional but recommended (helps identify which rule has the issue)\n"
                "- `preference` — optional (used to detect priority gaps)\n"
                "- `enabled` — optional\n\n"
                "**Or use the template below:**"
            )
            import io
            template_anomaly = io.StringIO()
            template_anomaly.write("name,preference,enabled,condition_expression\n")
            template_anomaly.write("Shopify Rule,1,true,\"#{#saleOrder.channel.code == 'SHOPIFY' and #saleOrderItem.shippingAddress.stateCode == 'MH'}\"\n")
            template_anomaly.write("Catch All,99,true,\"true\"\n")
            st.download_button(
                label="⬇️ Download Template CSV",
                data=template_anomaly.getvalue(),
                file_name="anomaly_suggester_template.csv",
                mime="text/csv",
                help="Download this template, fill in your rules, then upload it below."
            )

        uploaded2 = st.file_uploader("Upload rule dump CSV", type=["csv"], key="anomaly_upload",
            help="Same format as Rule Audit — exported from Uniware or built using the template above.")
        if uploaded2:
            try:
                import pandas as pd
                df2 = pd.read_csv(uploaded2)
                if 'condition_expression' not in df2.columns:
                    st.error("❌ This file doesn't have a `condition_expression` column.")
                else:
                    st.success(f"✅ Loaded {len(df2)} rules. Analysing...")
                    exprs2 = df2['condition_expression'].dropna().astype(str).tolist()
                    anomalies = []

                    # Duplicates
                    seen_e = {}
                    for idx, row in df2.iterrows():
                        expr = str(row.get('condition_expression', '')).strip()
                        if expr in seen_e:
                            anomalies.append({
                                "Type": "🔁 Duplicate Rule",
                                "Detail": f"Rule '{row.get('name', idx)}' has the exact same condition as '{seen_e[expr]}'. Only the one with higher priority will ever be used — the other is wasted.",
                                "Suggestion": "Delete or merge the duplicate rule."
                            })
                        else:
                            seen_e[expr] = row.get('name', str(idx))

                    # Multiple catch-all true rules
                    true_rules = df2[df2['condition_expression'].astype(str).str.strip().str.lower() == 'true']
                    if len(true_rules) > 1:
                        anomalies.append({
                            "Type": "⚠️ Multiple Always-Match Rules",
                            "Detail": f"{len(true_rules)} rules use `true` as their condition — meaning they match every single order. Only the one with the highest priority will ever be reached.",
                            "Suggestion": "Keep only one catch-all rule and place it last (lowest preference number)."
                        })

                    # Uncovered Indian states
                    all_states = set()
                    for expr in exprs2:
                        found = re.findall(r"'([A-Z]{2})'", expr)
                        india_codes = {code for code, _ in COUNTRY_STATE_DATA['IN']['states']}
                        all_states.update(s for s in found if s in india_codes)
                    india_all = {code for code, _ in COUNTRY_STATE_DATA['IN']['states']}
                    missing = india_all - all_states
                    if missing and len(all_states) > 3:
                        missing_names = [f"{code} ({name})" for code, name in COUNTRY_STATE_DATA['IN']['states'] if code in missing]
                        anomalies.append({
                            "Type": "📍 Indian States Not Covered",
                            "Detail": f"{len(missing)} Indian state(s) are not mentioned in any rule: {', '.join(sorted(missing_names)[:10])}{'...' if len(missing_names) > 10 else ''}.",
                            "Suggestion": "If you use state-based routing, check whether these states need a dedicated rule or a catch-all to handle them."
                        })

                    # Catch-all rules
                    catchall = df2[df2['condition_expression'].astype(str).str.strip().str.lower().isin(['true', '#{true}'])]
                    if not catchall.empty:
                        anomalies.append({
                            "Type": "📋 Catch-All Rule(s) Present",
                            "Detail": f"{len(catchall)} rule(s) match every order that reaches them: {', '.join(catchall['name'].astype(str).tolist()[:5])}.",
                            "Suggestion": "Make sure these are intentional and placed last in the priority order — otherwise they will block more specific rules below them."
                        })

                    # Preference gaps
                    if 'preference' in df2.columns:
                        prefs = sorted(df2['preference'].dropna().astype(int).tolist())
                        gaps = [prefs[i+1]-prefs[i] for i in range(len(prefs)-1) if prefs[i+1]-prefs[i] > 10]
                        if gaps:
                            anomalies.append({
                                "Type": "🔢 Gaps in Priority Order",
                                "Detail": f"Found {len(gaps)} large gap(s) between rule priority numbers — this usually means some rules were deleted but the numbers weren't cleaned up.",
                                "Suggestion": "Review the priority order to make sure rules evaluate in the right sequence."
                            })

                    if not anomalies:
                        st.success("🎉 No anomalies found!")
                    else:
                        st.warning(f"💡 Found {len(anomalies)} thing(s) to review:")
                        for a in anomalies:
                            with st.expander(a['Type'], expanded=True):
                                st.markdown(f"**What we found:** {a['Detail']}")
                                st.markdown(f"**What to do:** {a['Suggestion']}")
            except Exception as e:
                st.error(f"Error reading file: {e}")
