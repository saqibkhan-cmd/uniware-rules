import streamlit as st
import re

# =====================================================================
# COUNTRY → STATE DATA (from Uniware supported countries/states)
# =====================================================================

COUNTRY_STATE_DATA = {
    "AE": {"name": "United Arab Emirates", "states": [("AJ", "Ajman"), ("AZ", "Abu Dhabi"), ("DU", "Dubai"), ("FU", "Fujairah"), ("RK", "Ras al-Khaimah"), ("SH", "Sharjah"), ("UQ", "Umm Al Quwain")]},
    "BH": {"name": "Bahrain", "states": [("13", "Al 'Asimah"), ("14", "Al Janubiyah"), ("15", "Al Muharraq"), ("17", "Ash Shamaliyah")]},
    "IN": {"name": "India", "states": [
        ("AN", "Andaman & Nicobar Islands"), ("AP", "Andhra Pradesh (Old)"), ("AD", "Andhra Pradesh"),
        ("AR", "Arunachal Pradesh"), ("AS", "Assam"), ("BR", "Bihar"), ("CH", "Chandigarh"),
        ("CT", "Chhattisgarh"), ("DN", "Dadra and Nagar Haveli and Daman and Diu"),
        ("DD", "Daman & Diu"), ("DL", "Delhi"), ("GA", "Goa"), ("GJ", "Gujarat"),
        ("HR", "Haryana"), ("HP", "Himachal Pradesh"), ("JK", "Jammu & Kashmir"),
        ("JH", "Jharkhand"), ("KA", "Karnataka"), ("KL", "Kerala"), ("LA", "Ladakh"),
        ("LD", "Lakshadweep"), ("MP", "Madhya Pradesh"), ("MH", "Maharashtra"),
        ("MN", "Manipur"), ("ML", "Meghalaya"), ("MZ", "Mizoram"), ("NL", "Nagaland"),
        ("OR", "Odisha"), ("PB", "Punjab"), ("PY", "Puducherry"), ("RJ", "Rajasthan"),
        ("SK", "Sikkim"), ("TN", "Tamil Nadu"), ("TL", "Telangana"), ("TR", "Tripura"),
        ("UP", "Uttar Pradesh"), ("UT", "Uttarakhand"), ("WB", "West Bengal"),
    ]},
    "KW": {"name": "Kuwait", "states": [("AH", "Al Ahmadi"), ("FA", "Al Farwaniyah"), ("JA", "Al Jahra"), ("KU", "Al Kuwayt"), ("HA", "Hawalli"), ("MU", "Mubarak Al-Kabeer")]},
    "LK": {"name": "Sri Lanka", "states": [
        ("11", "Colombo"), ("12", "Gampaha"), ("13", "Kalutara"), ("21", "Kandy"),
        ("22", "Matale"), ("23", "Nuwara Eliya"), ("31", "Galle"), ("32", "Matara"),
        ("33", "Hambantota"), ("41", "Jaffna"), ("42", "Kilinochchi"), ("43", "Mannar"),
        ("44", "Mullaitivu"), ("45", "Vavuniya"), ("51", "Batticaloa"), ("52", "Ampara"),
        ("53", "Trincomalee"), ("61", "Kurunegala"), ("62", "Puttalam"), ("71", "Anuradhapura"),
        ("72", "Polonnaruwa"), ("81", "Badulla"), ("82", "Monaragala"), ("91", "Ratnapura"), ("92", "Kegalle"),
    ]},
    "OM": {"name": "Oman", "states": [("BA", "Al Batinah North"), ("BJ", "Janub al Batinah"), ("BS", "Shamal al Batinah"), ("BU", "Al Buraymi"), ("DA", "Ad Dakhiliyah"), ("MA", "Masqat"), ("MU", "Musandam"), ("SH", "Ash Sharqiyah North"), ("SS", "Ash Sharqiyah South"), ("WU", "Al Wusta"), ("ZA", "Az Zahirah")]},
    "QA": {"name": "Qatar", "states": [("DA", "Ad Dawhah"), ("KH", "Al Khawr"), ("MS", "Ash Shahaniyah"), ("RA", "Ar Rayyan"), ("SH", "Ash Shihaniyah"), ("US", "Umm Salal"), ("WA", "Al Wakrah"), ("ZA", "Az Za'ayin")]},
    "SA": {"name": "Saudi Arabia", "states": [("01", "Ar Riyad"), ("02", "Makkah al Mukarramah"), ("03", "Al Madinah al Munawwarah"), ("04", "Ash Sharqiyah"), ("05", "Al Qasim"), ("06", "Ha'il"), ("07", "Tabuk"), ("08", "Al Hudud ash Shamaliyah"), ("09", "Jizan"), ("10", "Najran"), ("11", "Al Bahah"), ("12", "Al Jawf"), ("14", "Asir")]},
    "US": {"name": "United States", "states": [
        ("AL", "Alabama"), ("AK", "Alaska"), ("AZ", "Arizona"), ("AR", "Arkansas"), ("CA", "California"),
        ("CO", "Colorado"), ("CT", "Connecticut"), ("DE", "Delaware"), ("FL", "Florida"), ("GA", "Georgia"),
        ("HI", "Hawaii"), ("ID", "Idaho"), ("IL", "Illinois"), ("IN", "Indiana"), ("IA", "Iowa"),
        ("KS", "Kansas"), ("KY", "Kentucky"), ("LA", "Louisiana"), ("ME", "Maine"), ("MD", "Maryland"),
        ("MA", "Massachusetts"), ("MI", "Michigan"), ("MN", "Minnesota"), ("MS", "Mississippi"),
        ("MO", "Missouri"), ("MT", "Montana"), ("NE", "Nebraska"), ("NV", "Nevada"), ("NH", "New Hampshire"),
        ("NJ", "New Jersey"), ("NM", "New Mexico"), ("NY", "New York"), ("NC", "North Carolina"),
        ("ND", "North Dakota"), ("OH", "Ohio"), ("OK", "Oklahoma"), ("OR", "Oregon"), ("PA", "Pennsylvania"),
        ("RI", "Rhode Island"), ("SC", "South Carolina"), ("SD", "South Dakota"), ("TN", "Tennessee"),
        ("TX", "Texas"), ("UT", "Utah"), ("VT", "Vermont"), ("VA", "Virginia"), ("WA", "Washington"),
        ("WV", "West Virginia"), ("WI", "Wisconsin"), ("WY", "Wyoming"), ("DC", "District of Columbia"),
        ("AS", "American Samoa"), ("GU", "Guam"), ("MP", "Northern Mariana Islands"),
        ("PR", "Puerto Rico"), ("VI", "U.S. Virgin Islands"),
    ]},
}

COUNTRY_OPTIONS = {cc: f"{cc} — {data['name']}" for cc, data in COUNTRY_STATE_DATA.items()}

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
    page_title="UniCommerce Master Production Engine Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ UniCommerce Master Production Engine Suite")
st.caption("Version 8.0.0 | Rule Compiler · Validator · Audit · Log Analyser · Anomaly Detector")

# =====================================================================
# TOP-LEVEL TOOL SELECTION
# =====================================================================

TOOLS = {
    "compiler":   "⚙️  Rule Compiler",
    "validator":  "🔍  Rule Validator",
    "reverse":    "🔄  Reverse Compiler",
    "audit":      "📋  Rule Audit (Dump Scanner)",
    "anomaly":    "💡  Anomaly Suggester",
    "log":        "🪵  Loki Log Analyser",
}

selected_tool = st.selectbox(
    "Select Tool",
    list(TOOLS.keys()),
    format_func=lambda x: TOOLS[x],
    help=(
        "⚙️  Rule Compiler — Build a new Facility / Shipping / Inventory rule step-by-step\n"
        "🔍  Rule Validator — Paste an existing rule and check it for known bugs\n"
        "🔄  Reverse Compiler — Paste a SpEL expression to decode it back to plain English\n"
        "📋  Rule Audit — Upload a rule dump CSV to scan all rules for bad patterns\n"
        "💡  Anomaly Suggester — Upload a rule dump to find gaps and dead rules\n"
        "🪵  Loki Log Analyser — Paste a Uniware error log for instant diagnosis"
    )
)

st.write("---")

# =====================================================================
# HELPER METHODS (shared across all tools)
# =====================================================================

def csv_items(raw_input):
    return [x.strip() for x in raw_input.split(",") if x.strip()]

def quoted_csv(raw_input):
    return [f"'{x.strip()}'" for x in raw_input.split(",") if x.strip()]

def smart_format_string(raw_input, var_name, use_ignore_case=False, strip_spaces=False):
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    effective_var = f'{var_name}.replace(" ", "")' if strip_spaces else var_name
    if len(items) == 1:
        val = items[0]
        if use_ignore_case:
            return f"{effective_var}.equalsIgnoreCase('{val}')"
        else:
            return f"{effective_var} == '{val}'"
    quoted = ", ".join(f"'{v}'" for v in items)
    func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
    return f"T(com.unifier.core.utils.StringUtils).{func}({effective_var}, {quoted})"

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
        if i.lower() in seen:
            dups.add(i)
        seen.add(i.lower())
    if dups:
        warnings_list.append(f"**{field_label}:** Duplicate value(s) — `{'`, `'.join(dups)}`. Each value should appear only once.")
    if field_type == "pincode":
        bad = [p for p in clean if not re.match(r'^\d{6}$', p)]
        if bad:
            warnings_list.append(f"**{field_label}:** `{'`, `'.join(bad)}` — pincodes must be exactly 6 digits.")
    elif field_type == "channel":
        for c in clean:
            if ' ' in c:
                warnings_list.append(f"**{field_label}:** `{c}` contains a space — channel codes should not have spaces.")
            elif c != c.upper():
                warnings_list.append(f"**{field_label}:** `{c}` has mixed casing — channel codes are typically uppercase. Enable Case-Insensitive Match if casing varies.")
    elif field_type == "number":
        bad = [n for n in clean if not re.match(r'^\d+(\.\d+)?$', n)]
        if bad:
            warnings_list.append(f"**{field_label}:** `{'`, `'.join(bad)}` — must be a numeric value.")

# =====================================================================
# KNOWN BAD PATTERN CHECKS (used by Validator and Audit tools)
# =====================================================================

def check_rule_for_issues(expr):
    """
    Checks a single SpEL expression for all known bad patterns.
    Returns list of issue dicts with {severity, message, fix}.
    """
    issues = []
    s = str(expr)

    # 1. Missing # prefix on shippingPackage or saleOrder
    # Only flag if the variable appears WITHOUT a preceding # (but not inside #shippingPackage etc.)
    if re.search(r'(?<![#\w.])(shippingPackage|saleOrder|reversePickup|allocationCriteria|inventorySnapshot)\.', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "Variable reference missing `#` prefix (e.g. `shippingPackage.x` instead of `#shippingPackage.x`). This causes `Property or field cannot be found on null` at runtime and crashes the entire allocation.",
            "fix": "Add `#` before every variable reference: `#shippingPackage`, `#saleOrder`, `#reversePickup`."
        })

    # 2. equalsIngoreCase typo
    if 'equalsIngoreCase' in s:
        issues.append({
            "severity": "🔴 Critical",
            "message": "`equalsIngoreCase` is a typo — the correct method is `equalsIgnoreCase` (capital I, not IngoreCase). This rule will never match because Uniware cannot find the method.",
            "fix": "Replace `equalsIngoreCase` with `equalsIgnoreCase` everywhere in this rule."
        })

    # 3. equalsIngoreCaseAny typo
    if 'equalsIngoreCaseAny' in s:
        issues.append({
            "severity": "🔴 Critical",
            "message": "`equalsIngoreCaseAny` is a typo — correct method is `equalsIgnoreCaseAny`.",
            "fix": "Replace `equalsIngoreCaseAny` with `equalsIgnoreCaseAny`."
        })

    # 4. OR without parentheses alongside AND (precedence bug)
    has_and = bool(re.search(r'\band\b', s, re.IGNORECASE))
    has_or  = bool(re.search(r'\bor\b', s, re.IGNORECASE))
    if has_and and has_or:
        # Recursively strip all parenthesised groups, then check if OR remains at top level
        stripped = s
        prev = None
        while prev != stripped:
            prev = stripped
            stripped = re.sub(r'\([^()]*\)', '', stripped)
        or_at_top_level = bool(re.search(r'\bor\b', stripped, re.IGNORECASE))
        if or_at_top_level:
            issues.append({
                "severity": "🟠 High",
                "message": "Rule mixes `and` and `or` without enclosing the `or` clause in parentheses. In SpEL (like Java), `and` binds tighter than `or`, so `A and B or C and D` evaluates as `(A and B) or (C and D)` — NOT `A and (B or C) and D`. This has caused real production incidents where rules matched far more orders than intended.",
                "fix": "Wrap the `or` clause in its own parentheses: `... and (conditionA or conditionB)`."
            })

    # 5. equalsAny with only one value
    m = re.findall(r'equalsAny\([^,)]+,\s*\'[^\']+\'\s*\)', s)
    if m:
        issues.append({
            "severity": "🟡 Medium",
            "message": f"`equalsAny()` used with only a single value: `{m[0][:80]}`. `equalsAny` is designed for multiple values. For a single value, use a direct `== 'VALUE'` comparison instead.",
            "fix": "Replace `equalsAny(field, 'VALUE')` with `field == 'VALUE'`."
        })

    # 6. Unquoted integer in list (type mismatch)
    if re.search(r'equalsAny\([^)]*,\s*\d+\s*[,)]', s):
        issues.append({
            "severity": "🔴 Critical",
            "message": "Unquoted integer found inside `equalsAny()`. SpEL compares this as a number against a string field, which will never match. All values in `equalsAny()` must be quoted strings.",
            "fix": "Quote all values: `equalsAny(field, '110001', '110002')` not `equalsAny(field, 110001, 110002)`."
        })

    # 7. Trailing comma inside equalsAny
    if re.search(r',\s*\)', s):
        issues.append({
            "severity": "🟠 High",
            "message": "Trailing comma before closing `)` found. This causes a SpEL parse error.",
            "fix": "Remove the trailing comma."
        })

    # 8. .contains() without prior null check
    if '.contains(' in s and '!= null' not in s and 'CustomFieldUtils' in s:
        issues.append({
            "severity": "🟠 High",
            "message": "`getCustomFieldValue(...).contains(...)` used without a prior `!= null` check. If the custom field is absent on an order, `getCustomFieldValue()` returns null and `.contains()` throws a NullPointerException at runtime.",
            "fix": "Add a null check: `getCustomFieldValue(...) != null and getCustomFieldValue(...).contains('value')`."
        })

    # 9. plain text (not SpEL) — missing #{ } wrapper
    stripped = s.strip()
    if stripped and not stripped.startswith('#{') and not stripped.startswith('#'):
        issues.append({
            "severity": "🔴 Critical",
            "message": "This expression does not start with `#{` — it appears to be plain text, not a SpEL expression. Uniware cannot evaluate it and will throw a type-conversion error.",
            "fix": "Wrap the entire expression: `#{your condition here}`."
        })

    return issues

# =====================================================================
# REVERSE COMPILER HELPER
# =====================================================================

def decode_spel(expr):
    """Decodes a SpEL expression into human-readable field/value pairs."""
    s = str(expr).strip()
    if s.startswith("#{") and s.endswith("}"):
        s = s[2:-1].strip()

    results = []

    def split_top_level_and(text):
        parts, depth, current = [], 0, []
        i = 0
        while i < len(text):
            c = text[i]
            if c == '(':
                depth += 1
                current.append(c)
            elif c == ')':
                depth -= 1
                current.append(c)
            elif depth == 0 and text[i:i+4].lower() == ' and':
                parts.append(''.join(current).strip())
                current = []
                i += 4
                continue
            else:
                current.append(c)
            i += 1
        if current:
            parts.append(''.join(current).strip())
        return [p for p in parts if p]

    conditions = split_top_level_and(s)

    VAR_MAP = {
        "#saleOrder.channel.code": "Channel Code (Facility)",
        "#shippingPackage.saleOrder.channel.code": "Channel Code (Shipping)",
        "#reversePickup.saleOrder.channel.code": "Return Channel Code",
        "#saleOrderItem.shippingAddress.stateCode": "State Code (Facility)",
        "#shippingPackage.shippingAddress.stateCode": "State Code (Shipping)",
        "#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode": "State Code (Return)",
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

    for cond in conditions:
        cond = cond.strip()

        # equalsAny / equalsIgnoreCaseAny
        m = re.match(r'T\(com\.unifier\.core\.utils\.StringUtils\)\.(equalsAny|equalsIgnoreCaseAny)\(([^,]+),\s*(.+)\)', cond)
        if m:
            func, var, vals_raw = m.group(1), m.group(2).strip(), m.group(3).strip()
            vals = re.findall(r"'([^']*)'", vals_raw)
            label = VAR_MAP.get(var, var)
            case_note = " (case-insensitive)" if "IgnoreCase" in func else ""
            results.append((label, f"equals any of: {', '.join(vals)}{case_note}"))
            continue

        # equalsIgnoreCase single
        m = re.match(r'(#[\w.]+)\.equalsIgnoreCase\(\'([^\']+)\'\)', cond)
        if m:
            label = VAR_MAP.get(m.group(1), m.group(1))
            results.append((label, f"equals (case-insensitive): {m.group(2)}"))
            continue

        # simple ==
        m = re.match(r"(#[\w.]+)\s*==\s*'([^']*)'", cond)
        if m:
            label = VAR_MAP.get(m.group(1), m.group(1))
            results.append((label, f"equals: {m.group(2)}"))
            continue

        # simple !=
        m = re.match(r"(#[\w.]+)\s*!=\s*'([^']*)'", cond)
        if m:
            label = VAR_MAP.get(m.group(1), m.group(1))
            results.append((label, f"does NOT equal: {m.group(2)}"))
            continue

        # != null
        m = re.match(r"(#[\w.]+)\s*!=\s*null", cond)
        if m:
            label = VAR_MAP.get(m.group(1), m.group(1))
            results.append((label, "must exist (not null)"))
            continue

        # numeric comparisons
        m = re.match(r'(#[\w.]+)\s*([><=!]+)\s*(\d+(?:\.\d+)?)', cond)
        if m:
            label = VAR_MAP.get(m.group(1), m.group(1))
            results.append((label, f"{m.group(2)} {m.group(3)}"))
            continue

        # allocationCriteria
        m = re.match(r'#allocationCriteria\.(\w+)\(\)', cond)
        if m:
            results.append(("Inventory Criteria", m.group(1)))
            continue

        # hasAnyTag
        m = re.search(r"hasAnyTag\('([^']+)'\)", cond)
        if m:
            results.append(("Item Tag", m.group(1)))
            continue

        # brand.contains
        m = re.search(r"brand\.contains\('([^']+)'\)", cond)
        if m:
            results.append(("Brand (contains)", m.group(1)))
            continue

        # size() comparisons
        m = re.search(r'saleOrderItems\.size\(\)\s*([><=!]+)\s*(\d+)', cond)
        if m:
            results.append(("Item Count", f"{m.group(1)} {m.group(2)}"))
            continue

        # CustomFieldUtils
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)[^)]*\.contains\('([^']+)'\)", cond)
        if m:
            results.append((f"Custom Field '{m.group(1)}'", f"contains: {m.group(2)}"))
            continue
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)\.equalsIgnoreCase\('([^']+)'\)", cond)
        if m:
            results.append((f"Custom Field '{m.group(1)}'", f"equals (case-insensitive): {m.group(2)}"))
            continue
        m = re.search(r"getCustomFieldValue\([^,]+,\s*'([^']+)'\)\s*!=\s*null", cond)
        if m:
            results.append((f"Custom Field '{m.group(1)}'", "must exist (not null)"))
            continue

        # boxWeight range
        m = re.search(r'boxWeight\s*([><=]+)\s*(\d+)', cond)
        if m:
            results.append(("Box Weight (g)", f"{m.group(1)} {m.group(2)}"))
            continue

        # inventory formula
        if "inventorySnapshot" in cond:
            results.append(("Inventory Formula", cond[:120]))
            continue

        results.append(("Condition", cond[:120]))

    return results

# ===================================================================
# ⚙️ RULE COMPILER
# ===================================================================

if selected_tool == "compiler":

    st.subheader("⚙️ Rule Compiler")
    st.caption("Build a Facility Allocation, Shipping Provider Allocation, or Inventory Sync rule step by step.")

    module = st.selectbox(
        "1. Select Module",
        ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
        format_func=lambda x: {
            "FACILITY":       "🏭  Facility Allocation Engine",
            "SHIPPING_FWD":   "🚚  Shipping Provider Allocation Engine",
            "INVENTORY_CALC": "🛠️  Inventory Synchronization Calculation"
        }[x],
        help="Choose which type of rule you want to build.\n\n• Facility Allocation — decides which warehouse fulfils an order\n• Shipping Provider — decides which courier ships a package\n• Inventory Sync — calculates how much stock to push to a channel"
    )

    if module == "INVENTORY_CALC":
        sub_type = st.selectbox(
            "2. Choose Formula Variant",
            ["DEFAULT", "BUFFER_3", "BUFFER_1", "ZERO_SYNC"],
            format_func=lambda x: {
                "DEFAULT":   "Standard — push actual calculated stock",
                "BUFFER_3":  "Buffer 3 — push 0 if stock ≤ 3 units",
                "BUFFER_1":  "Buffer 1 — push 0 if stock ≤ 1 unit",
                "ZERO_SYNC": "Zero Sync — always push 0 (suppress SKU on channel)"
            }[x],
            help="• Standard: pushes real available stock to the channel\n• Buffer 3/1: adds a safety guard — syncs 0 instead of the real quantity when stock is critically low, to avoid overselling\n• Zero Sync: always syncs 0 regardless of stock — used to temporarily delist a SKU without changing actual inventory"
        )
    else:
        sub_type = "STANDARD"

    st.write("---")
    st.write("### 3. Conditions")

    # ── FACILITY ──────────────────────────────────────────────────────
    if module == "FACILITY":

        st.markdown("**🏭 Facility Allocation Rule Constructor**")
        st.caption("Tick the conditions you need. Leave others unticked — every ticked condition is joined with AND.")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Channel Code**")
            fac_use_channel = st.checkbox("Apply Channel Code Filter", key="fac_use_channel",
                help="Single value → `== 'SHOPIFY'`\nMultiple (comma-separated) → `equalsAny('SHOPIFY','FLIPKART')`\n\nEnable case-insensitive if the channel code in Uniware may have inconsistent casing.")
            fac_channel_val = ""
            fac_channel_icase = False
            fac_channel_strip_spaces = False
            if fac_use_channel:
                fac_channel_val = st.text_input("Channel Code(s)", key="fac_channel_val",
                    placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
                fac_channel_icase = st.checkbox("Case-Insensitive Match", key="fac_channel_icase",
                    help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple. Use if channel code casing varies.")
                fac_channel_strip_spaces = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="fac_channel_strip_spaces",
                    help="Removes all spaces from the channel code before comparing. Use if the source data sometimes contains accidental spaces.")

        with col2:
            st.markdown("**Inventory Allocation Criteria**")
            fac_inv = st.selectbox("Inventory Criteria", [
                "NONE","hasShortTermInventory","hasCompleteShortTermInventory",
                "hasCompleteLongTermInventory","hasCompleteInventory","hasFulfillableInventory",
                "hasInventory","hasLiveInventory","hasLongTermInventory",
                "hasCompleteMidTermInventory","hasAllocationWithinMaxOrderCapacity"],
                format_func=lambda x: {
                    "NONE": "— No Inventory Filter —",
                    "hasShortTermInventory": "Has Short Term Inventory",
                    "hasCompleteShortTermInventory": "Has Complete Short Term Inventory",
                    "hasCompleteLongTermInventory": "Has Complete Long Term Inventory",
                    "hasCompleteInventory": "Has Complete Inventory",
                    "hasFulfillableInventory": "Has Fulfillable Inventory",
                    "hasInventory": "Has Inventory",
                    "hasLiveInventory": "Has Live Inventory",
                    "hasLongTermInventory": "Has Long Term Inventory",
                    "hasCompleteMidTermInventory": "Has Complete Mid Term Inventory",
                    "hasAllocationWithinMaxOrderCapacity": "Has Allocation Within Max Order Capacity",
                }.get(x, x), key="fac_inv",
                help="Checks whether the facility has the right type of stock before allocating:\n• Short Term — near-term available stock\n• Complete Short Term — all order items have short-term stock\n• Fulfillable — stock in a non-blocked, sellable state\n• Has Inventory — any stock exists at all\n• Max Order Capacity — facility hasn't hit its order cap")

        st.write("")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**State Code**")
            fac_use_state = st.checkbox("Apply State Code Filter", key="fac_use_state",
                help="Select a country to load its state list, then pick one or more states.\n\nSingle state → `== 'MH'` | Multiple → `equalsAny('MH','GJ')`")
            fac_state_val = ""
            if fac_use_state:
                fac_sc = st.selectbox("Country (to load states)", options=[""] + list(COUNTRY_OPTIONS.keys()),
                    format_func=lambda x: "— Select country —" if x == "" else COUNTRY_OPTIONS[x], key="fac_state_cc",
                    help="Select the country whose states you want to choose from.")
                fac_sel_states = []
                if fac_sc:
                    fac_sel_states = st.multiselect("State(s)", options=get_state_options(fac_sc), key="fac_state_multi",
                        help="Select one or multiple states. The rule will match any of the selected states.")
                fac_state_val = ",".join(extract_state_codes(fac_sel_states))

        with col4:
            st.markdown("**Pincode**")
            fac_use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode",
                help="Single → `== '560001'` | Multiple → `equalsAny('560001','560002')`\n\nEnter 6-digit Indian pincodes. Values are automatically quoted as strings in the output.")
            fac_pincode_val = ""
            if fac_use_pincode:
                fac_pincode_val = st.text_area("Pincode(s)", key="fac_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80)

        st.write("")
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**City**")
            fac_use_city = st.checkbox("Apply City Filter", key="fac_use_city",
                help="Single → `== 'DELHI'` | Multiple → `equalsAny('DELHI','MUMBAI')`\n\nCity matching is exact — check the exact spelling stored in your Uniware tenant's order data before using this filter.")
            fac_city_val = ""
            if fac_use_city:
                fac_city_val = st.text_input("City / Cities", key="fac_city_val",
                    placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi, Bangalore")

        with col6:
            st.markdown("**Payment Method**")
            fac_use_payment = st.checkbox("Apply Payment Method Filter", key="fac_use_payment",
                help="Restricts the rule to COD or Prepaid orders.\n\nGenerates: `#saleOrder.paymentMethod.code == 'COD'`\n\nUseful for routing COD orders to specific facilities with cash-handling capability.")
            fac_payment_val = ""
            if fac_use_payment:
                fac_payment_val = st.selectbox("Payment Method", ["PREPAID", "COD"], key="fac_payment_val",
                    help="PREPAID = online/card/UPI paid orders\nCOD = cash on delivery orders")

        st.write("")
        col7, col8 = st.columns(2)

        with col7:
            st.markdown("**Country Code**")
            fac_use_country = st.checkbox("Apply Country Code Filter", key="fac_use_country",
                help="Equals: `== 'IN'` — order IS from this country\nNot Equals: `!= 'IN'` — order is NOT from this country\n\nUseful for separating domestic (IN) from international routing.")
            fac_country_val = ""
            fac_country_mode = "equals"
            if fac_use_country:
                fac_country_mode = st.radio("Match Type", ["equals", "not_equals"],
                    format_func=lambda x: {"equals": "✅ Equals — order IS from this country", "not_equals": "🚫 Not Equals — order is NOT from this country"}[x],
                    horizontal=True, key="fac_country_mode",
                    help="Equals: matches orders shipping TO the given country.\nNot Equals: matches orders shipping ANYWHERE EXCEPT the given country — e.g. all non-India orders.")
                fac_country_val = st.text_input("Country Code(s)", key="fac_country_val",
                    placeholder="Single: IN  |  Multiple: IN, US, AE")

        with col8:
            st.markdown("**SKU Code**")
            fac_use_sku = st.checkbox("Apply SKU Code Filter", key="fac_use_sku",
                help="Checks if any item in the order matches the given SKU(s).\n\nSingle → `saleOrderItems.?[skuCode == 'SKU001'].size() > 0`\nMultiple → uses `equalsAny` inside the collection filter\n\nDoes NOT require every item to match — at least one matching item is enough.")
            fac_sku_val = ""
            if fac_use_sku:
                fac_sku_val = st.text_area("SKU Code(s)", key="fac_sku_val",
                    placeholder="Single: SKU001  |  Multiple: SKU001, SKU002, SKU003", height=80)

        st.write("")
        col9, col10 = st.columns(2)

        with col9:
            st.markdown("**Item Tag (hasAnyTag)**")
            fac_use_item_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_item_tag",
                help="Checks if any item in the order carries a specific tag from the item master.\n\nGenerates: `#saleOrder.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`\n\nUseful for routing orders containing specially tagged products (e.g. fragile, hazardous, brand-specific).")
            fac_item_tag_val = ""
            if fac_use_item_tag:
                fac_item_tag_val = st.text_input("Item Tag Value", key="fac_item_tag_val",
                    placeholder="e.g. SWAYAM  or  Fragile  or  Rudra")

        with col10:
            st.markdown("**Brand (contains match)**")
            fac_use_brand = st.checkbox("Apply Brand Filter", key="fac_use_brand",
                help="Checks if any order item belongs to a brand whose name contains the given text.\n\nGenerates: `#saleOrder.saleOrderItems.^[itemType.brand.contains('BRAND')] != null`\n\nNote: this is a partial/contains match, not an exact match.")
            fac_brand_val = ""
            if fac_use_brand:
                fac_brand_val = st.text_input("Brand Name", key="fac_brand_val",
                    placeholder="e.g. Trend Arrest")

        st.write("")
        col11, col12 = st.columns(2)

        with col11:
            st.markdown("**Custom Field**")
            fac_use_cf = st.checkbox("Apply Custom Field Filter", key="fac_use_cf",
                help="Filters by a custom field on the sale order (e.g. Shopify tags, delivery flags, on-hold markers).\n\n• **Contains** — field holds multiple tags/words, you want to check if one appears in it (most common)\n• **Exactly Equals** — field must be precisely one value\n• **Just Exists** — field just needs to be present, value doesn't matter\n\nField Name must match exactly as configured in Uniware (case-sensitive).")
            fac_cf_field = ""
            fac_cf_match = "contains"
            fac_cf_value = ""
            fac_cf_strip_spaces = False
            if fac_use_cf:
                fac_cf_field = st.text_input("Custom Field Name (exact key in Uniware)", key="fac_cf_field",
                    placeholder="e.g. Tags  or  Omni  or  OnHold")
                fac_cf_match = st.selectbox("How should the field be matched?",
                    ["contains", "equalsIgnoreCase", "not_null"],
                    format_func=lambda x: {
                        "contains": "🔍 Contains — field has this word/value somewhere in it",
                        "equalsIgnoreCase": "✅ Exactly Equals — field is precisely this value",
                        "not_null": "📌 Just Exists — any non-empty value is enough"
                    }[x], key="fac_cf_match",
                    help="🔍 Contains: use when the field holds multiple comma-separated tags and you want to check if one specific tag appears in it\n✅ Exactly Equals: use when the field must be one precise value (e.g. Omni == 'false')\n📌 Just Exists: use when you only care the field is filled in at all")
                if fac_cf_match != "not_null":
                    fac_cf_value = st.text_input("Value to match against", key="fac_cf_value",
                        placeholder="e.g. express  or  employee_delight60  or  false")
                if fac_cf_match in ("contains", "equalsIgnoreCase"):
                    fac_cf_strip_spaces = st.checkbox("Strip Spaces Before Matching (.replace(\" \", \"\"))", key="fac_cf_strip_spaces",
                        help="Removes all spaces from the field value before comparing. Use when Shopify/channel may send tags with accidental spaces (e.g. 'HyperLocalStore_DSBB 10' instead of 'HyperLocalStore_DSBB10').")

        with col12:
            st.write("")

        st.write("")

    # ── SHIPPING PROVIDER ─────────────────────────────────────────────
    elif module == "SHIPPING_FWD":

        st.markdown("**🚚 Shipping Provider Allocation Rule Constructor**")
        st.caption("Toggle Reverse Pickup ON for returns/RTO rules. Leave it OFF for standard forward shipments.")

        is_reverse = st.checkbox("This is a Reverse Pickup / Return Rule (uses #reversePickup context)", key="sp_is_reverse",
            help="ON → rule uses `#reversePickup` variable (for return courier selection)\nOFF → rule uses `#shippingPackage` (standard outbound shipment courier selection)\n\nThe two flows use different SpEL variables — mixing them will cause a runtime error.")

        st.write("")

        if is_reverse:
            st.markdown("##### Reverse Pickup Conditions")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Return Channel Code**")
                rev_channel_val = st.text_input("Return Channel Code(s)", key="rev_channel_val",
                    placeholder="Single: SHOPIFY  |  Multiple: SHOPIFY, CUSTOM",
                    help="The channel code of the original order being returned.\n\nAlways uses case-insensitive matching for reverse pickup (confirmed from production rule patterns).\n\nSingle → `equalsIgnoreCase('SHOPIFY')` | Multiple → `equalsIgnoreCaseAny(...)`")
            with col2:
                st.markdown("**Box Weight (grams)**")
                rev_use_weight = st.checkbox("Apply Box Weight Filter", key="rev_use_weight",
                    help="Filters by the physical box weight of the return package.\n\nUses `#reversePickup.boxWeight` with **exclusive bounds on both sides** (> min, < max).\n\nExample: Min=0, Max=4999 → `(#reversePickup.boxWeight > 0 and #reversePickup.boxWeight < 4999)`")
                rev_weight_min = ""
                rev_weight_max = ""
                if rev_use_weight:
                    rev_weight_min = st.text_input("Min Box Weight — exclusive > (blank = no lower bound)", key="rev_weight_min", placeholder="e.g. 0").strip()
                    rev_weight_max = st.text_input("Max Box Weight — exclusive < (blank = no upper bound)", key="rev_weight_max", placeholder="e.g. 4999").strip()

            st.write("")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**State Code**")
                rev_use_state = st.checkbox("Apply State Code Filter", key="rev_use_state",
                    help="Restricts the reverse pickup rule to specific state codes.\n\nUses: `#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode`")
                rev_state_val = ""
                if rev_use_state:
                    rev_sc = st.selectbox("Country (to load states)", options=[""] + list(COUNTRY_OPTIONS.keys()),
                        format_func=lambda x: "— Select country —" if x == "" else COUNTRY_OPTIONS[x], key="rev_state_cc")
                    rev_sel = []
                    if rev_sc:
                        rev_sel = st.multiselect("State(s)", options=get_state_options(rev_sc), key="rev_state_multi")
                    rev_state_val = ",".join(extract_state_codes(rev_sel))
            with col4:
                st.markdown("**Pincode**")
                rev_use_pincode = st.checkbox("Apply Pincode Filter", key="rev_use_pincode",
                    help="Restricts by pickup pincode.\n\nUses: `#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode`")
                rev_pincode_val = ""
                if rev_use_pincode:
                    rev_pincode_val = st.text_area("Pincode(s)", key="rev_pincode_val",
                        placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80)

            st.write("")
            col5, col6 = st.columns(2)
            with col5:
                st.markdown("**City**")
                rev_use_city = st.checkbox("Apply City Filter", key="rev_use_city",
                    help="Restricts by pickup city.\n\nUses: `#reversePickup.saleOrder.shippingPackage.shippingAddress.city`")
                rev_city_val = ""
                if rev_use_city:
                    rev_city_val = st.text_input("City / Cities", key="rev_city_val",
                        placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi")
            with col6:
                st.markdown("**Payment Method**")
                rev_use_payment = st.checkbox("Apply Payment Method Filter", key="rev_use_payment",
                    help="Filters by the original order's payment type.\n\nGenerates: `#reversePickup.saleOrder.paymentMethod.code == 'COD'`")
                rev_payment_val = ""
                if rev_use_payment:
                    rev_payment_val = st.selectbox("Payment Method", ["COD", "PREPAID"], key="rev_payment_val")

            st.write("")

        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Channel Code**")
                sp_use_channel = st.checkbox("Apply Channel Code Filter", key="sp_use_channel",
                    help="Single → `#shippingPackage.saleOrder.channel.code == 'SHOPIFY'`\nMultiple → `equalsAny(...)`\n\nEnable case-insensitive if the channel code may have inconsistent casing in Uniware.")
                sp_channel_val = ""
                sp_channel_icase = False
                sp_channel_strip_spaces = False
                if sp_use_channel:
                    sp_channel_val = st.text_input("Channel Code(s)", key="sp_channel_val",
                        placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
                    sp_channel_icase = st.checkbox("Case-Insensitive Match", key="sp_channel_icase",
                        help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple.")
                    sp_channel_strip_spaces = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="sp_channel_strip_spaces",
                        help="Removes all spaces before comparing. Use if channel code may contain accidental spaces.")
            with col2:
                st.markdown("**State Code**")
                sp_use_state = st.checkbox("Apply State Code Filter", key="sp_use_state",
                    help="Select a country to load its state list, then pick one or more states.\n\nUses: `#shippingPackage.shippingAddress.stateCode`")
                sp_state_val = ""
                if sp_use_state:
                    sp_sc = st.selectbox("Country (to load states)", options=[""] + list(COUNTRY_OPTIONS.keys()),
                        format_func=lambda x: "— Select country —" if x == "" else COUNTRY_OPTIONS[x], key="sp_state_cc")
                    sp_sel = []
                    if sp_sc:
                        sp_sel = st.multiselect("State(s)", options=get_state_options(sp_sc), key="sp_state_multi")
                    sp_state_val = ",".join(extract_state_codes(sp_sel))

            st.write("")
            col3, col4 = st.columns(2)
            with col3:
                st.markdown("**Pincode**")
                sp_use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode",
                    help="Restricts courier selection to specific delivery pincodes.\n\nUses: `#shippingPackage.shippingAddress.pincode`\n\nSingle → `==` | Multiple → `equalsAny(...)`")
                sp_pincode_val = ""
                if sp_use_pincode:
                    sp_pincode_val = st.text_area("Pincode(s)", key="sp_pincode_val",
                        placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=80)
            with col4:
                st.markdown("**Payment Method**")
                sp_use_payment = st.checkbox("Apply Payment Method Filter", key="sp_use_payment",
                    help="Restricts courier selection to COD or Prepaid orders.\n\nGenerates: `#shippingPackage.saleOrder.paymentMethod.code == 'COD'`\n\nUseful for assigning dedicated COD couriers.")
                sp_payment_val = ""
                if sp_use_payment:
                    sp_payment_val = st.selectbox("Payment Method", ["COD", "PREPAID"], key="sp_payment_val")

            st.write("")
            col5, col6 = st.columns(2)
            with col5:
                st.markdown("**Package Weight (grams)**")
                sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight",
                    help="Filters by actual package weight in grams.\n\nUses: `#shippingPackage.actualWeight`\n\n• Min bound is **exclusive** (>)\n• Max bound is **inclusive** (<=)\n\nExample: Min=500, Max=1000 → `actualWeight > 500 and actualWeight <= 1000`\n\nThis asymmetry ensures adjacent weight slabs don't overlap.")
                sp_weight_min = ""
                sp_weight_max = ""
                if sp_use_weight:
                    sp_weight_min = st.text_input("Min Weight — exclusive > (blank = no lower bound)", key="sp_weight_min", placeholder="e.g. 500").strip()
                    sp_weight_max = st.text_input("Max Weight — inclusive <= (blank = no upper bound)", key="sp_weight_max", placeholder="e.g. 1000").strip()
            with col6:
                st.markdown("**Total Order Price**")
                sp_use_price = st.checkbox("Apply Price Filter", key="sp_use_price",
                    help="Filters by total declared order value.\n\nUses: `#shippingPackage.totalPrice`\n\n• Min bound is exclusive (>)\n• Max bound is inclusive (<=)\n\nUseful for routing high-value orders to insured/premium couriers.")
                sp_price_min = ""
                sp_price_max = ""
                if sp_use_price:
                    sp_price_min = st.text_input("Min Price — exclusive > (blank = no lower bound)", key="sp_price_min", placeholder="e.g. 0").strip()
                    sp_price_max = st.text_input("Max Price — inclusive <= (blank = no upper bound)", key="sp_price_max", placeholder="e.g. 6000").strip()

            st.write("")
            col7, col8 = st.columns(2)
            with col7:
                st.markdown("**City**")
                sp_use_city = st.checkbox("Apply City Filter", key="sp_use_city",
                    help="Restricts courier selection to specific delivery cities.\n\nUses: `#shippingPackage.shippingAddress.city`\n\nExact match — check the exact spelling in your Uniware tenant's order data.")
                sp_city_val = ""
                if sp_use_city:
                    sp_city_val = st.text_input("City / Cities", key="sp_city_val",
                        placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi")
            with col8:
                st.markdown("**Country Code**")
                sp_use_country = st.checkbox("Apply Country Code Filter", key="sp_use_country",
                    help="Restricts courier selection by destination country.\n\nUses: `#shippingPackage.shippingAddress.countryCode`\n\nSingle → `==` | Multiple → `equalsAny(...)`")
                sp_country_val = ""
                if sp_use_country:
                    sp_country_val = st.text_input("Country Code(s)", key="sp_country_val",
                        placeholder="Single: IN  |  Multiple: IN, US, AE")

            st.write("")
            col9, col10 = st.columns(2)
            with col9:
                st.markdown("**Number of Items in Package**")
                sp_use_item_count = st.checkbox("Apply Item Count Filter", key="sp_use_item_count",
                    help="Filters by how many line items are in the shipping package.\n\nUses: `#shippingPackage.saleOrderItems.size()`\n\nUseful for assigning different couriers for single-item vs bulk shipments.")
                sp_item_count_op = "<="
                sp_item_count_val = ""
                if sp_use_item_count:
                    sp_item_count_op = st.selectbox("Operator", ["<=", "<", ">=", ">", "=="],
                        format_func=lambda x: {
                            "<=": "<= (Up to N items — small/single shipments)",
                            "<": "<  (Fewer than N items — strictly less)",
                            ">=": ">= (At least N items — bulk shipments)",
                            ">": ">  (More than N items — strictly greater)",
                            "==": "== (Exactly N items)"
                        }[x], key="sp_item_count_op",
                        help="• <= : package has up to N items (e.g. <= 1 for single-item-only couriers)\n• >= : package has at least N items (bulk threshold)\n• == : exactly N items")
                    sp_item_count_val = st.text_input("Item Count Threshold", key="sp_item_count_val", placeholder="e.g. 12").strip()
            with col10:
                st.markdown("**Item Tag (hasAnyTag)**")
                sp_use_item_tag = st.checkbox("Apply Item Tag Filter", key="sp_use_item_tag",
                    help="Checks if any item in the package has a specific tag from the item master.\n\nGenerates: `#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`\n\nUseful for routing packages containing specially tagged items (e.g. mattress, furniture) to specialist couriers.")
                sp_item_tag_val = ""
                if sp_use_item_tag:
                    sp_item_tag_val = st.text_input("Item Tag Value", key="sp_item_tag_val",
                        placeholder="e.g. mattress  or  Furniture  or  Accessories")

            st.write("")
            col11, col12 = st.columns(2)
            with col11:
                st.markdown("**Custom Field**")
                sp_use_cf = st.checkbox("Apply Custom Field Filter", key="sp_use_cf",
                    help="Filters by a custom field on the sale order (e.g. Tags, Delivery_Partner, tagsfetched).\n\n• Contains — field has this word somewhere in it (most common)\n• Exactly Equals — field must be precisely this value\n• Just Exists — field just needs to be present\n\nField Name must match the exact key in Uniware (case-sensitive).")
                sp_cf_field = ""
                sp_cf_match = "contains"
                sp_cf_value = ""
                sp_cf_strip_spaces = False
                if sp_use_cf:
                    sp_cf_field = st.text_input("Custom Field Name (exact key in Uniware)", key="sp_cf_field",
                        placeholder="e.g. Tags  or  Delivery_Partner  or  tagsfetched")
                    sp_cf_match = st.selectbox("How should the field be matched?",
                        ["contains", "equalsIgnoreCase", "not_null"],
                        format_func=lambda x: {
                            "contains": "🔍 Contains — field has this word/value somewhere in it",
                            "equalsIgnoreCase": "✅ Exactly Equals — field is precisely this value",
                            "not_null": "📌 Just Exists — any non-empty value is enough"
                        }[x], key="sp_cf_match",
                        help="🔍 Contains: most common — use for Tags field which holds multiple comma-separated tags\n✅ Exactly Equals: use when the field must be one exact value (e.g. Delivery_Partner == 'DELHIVERY_5KGS')\n📌 Just Exists: use when any value in the field is sufficient to trigger the rule")
                    if sp_cf_match != "not_null":
                        sp_cf_value = st.text_input("Value to match against", key="sp_cf_value",
                            placeholder="e.g. Express  or  DELHIVERY_5KGS  or  EDNDDTAG")
                    if sp_cf_match in ("contains", "equalsIgnoreCase"):
                        sp_cf_strip_spaces = st.checkbox("Strip Spaces (.replace(\" \", \"\"))", key="sp_cf_strip_spaces",
                            help="Removes all spaces from the field value before comparing. Use when the channel may send tags with accidental spaces.")
            with col12:
                st.write("")
            st.write("")

    # ── INVENTORY CALC ────────────────────────────────────────────────
    elif module == "INVENTORY_CALC":
        st.markdown("**🛠️ Inventory Synchronization Formula Constructor**")
        st.caption("Check the stock pools to include in the formula. The base deductions (open sales, pendency, blocked stock) are always applied.")
        v_inv = st.checkbox("Include Virtual Inventory", key="calc_v_inv",
            help="Adds `#inventorySnapshot.virtualInventory` to the formula.\n\nVirtual inventory is stock allocated via buffer/reservation mechanisms. Enable when the channel sync should count this pool in addition to physical stock.")
        v_nd = st.checkbox("Include Vendor / Drop-Ship Inventory", key="calc_v_nd",
            help="Adds `#inventorySnapshot.vendorInventory` to the formula.\n\nEnable for channels/SKUs that can be fulfilled from vendor or drop-ship warehouses in addition to your own stock.")
        unproc = st.checkbox("Deduct Unprocessed Orders (Amazon Flex / Slab Channels)", key="calc_unproc",
            help="Subtracts `#unprocessedOrderInventory` from the formula.\n\nUnprocessed orders have been placed on the channel but haven't entered Uniware's processing pipeline yet — they still consume stock, so they must be deducted.\n\nCritical for Amazon Flex and similar batch/slab channel integrations.")
        st.write("")

    # ── COMPILE BUTTON ─────────────────────────────────────────────────
    if st.button("⚙️ Compile Rule", type="primary"):
        final_output = ""
        warnings_list = []

        if module == "FACILITY":
            if fac_use_channel and fac_channel_val.strip():
                validate_inputs(warnings_list, "Channel Code", fac_channel_val, "channel")
            if fac_use_pincode and fac_pincode_val.strip():
                validate_inputs(warnings_list, "Pincode", fac_pincode_val, "pincode")
            if fac_use_city and fac_city_val.strip():
                validate_inputs(warnings_list, "City", fac_city_val, "generic")
            if fac_use_country and fac_country_val.strip():
                validate_inputs(warnings_list, "Country Code", fac_country_val, "generic")
            if fac_use_sku and fac_sku_val.strip():
                validate_inputs(warnings_list, "SKU Code", fac_sku_val, "generic")

            if warnings_list:
                st.warning("⚠️ **Please review before using this rule:**")
                for w in warnings_list:
                    st.markdown(f"- {w}")
                st.write("")

            parts = []
            if fac_use_channel and fac_channel_val.strip():
                e = smart_format_string(fac_channel_val, "#saleOrder.channel.code", fac_channel_icase, fac_channel_strip_spaces)
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
                if fac_country_mode == "not_equals":
                    e = format_not_equals_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode")
                else:
                    e = format_multi_value_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode")
                if e: parts.append(e)
            if fac_use_sku and fac_sku_val.strip():
                sku_items = csv_items(fac_sku_val)
                if sku_items:
                    if len(sku_items) == 1:
                        parts.append(f"#saleOrder.saleOrderItems.?[skuCode == '{sku_items[0]}'].size() > 0")
                    else:
                        quoted = ", ".join(f"'{v}'" for v in sku_items)
                        parts.append(f"#saleOrder.saleOrderItems.?[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {quoted})].size() > 0")
            if fac_use_item_tag and fac_item_tag_val.strip():
                parts.append(f"#saleOrder.saleOrderItems.^[itemType.hasAnyTag('{fac_item_tag_val.strip()}')] != null")
            if fac_use_brand and fac_brand_val.strip():
                parts.append(f"#saleOrder.saleOrderItems.^[itemType.brand.contains('{fac_brand_val.strip()}')] != null")
            if fac_use_cf and fac_cf_field.strip():
                cf_fn = fac_cf_field.strip()
                cf_val = fac_cf_value.strip() if fac_cf_value else ""
                cf_getter = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrder, '{cf_fn}')"
                cf_eff = f'{cf_getter}.replace(" ", "")' if fac_cf_strip_spaces else cf_getter
                if fac_cf_match == "contains":
                    parts.append(f"{cf_getter} != null and {cf_eff}.contains('{cf_val}')")
                elif fac_cf_match == "equalsIgnoreCase":
                    parts.append(f"{cf_eff}.equalsIgnoreCase('{cf_val}')")
                elif fac_cf_match == "not_null":
                    parts.append(f"{cf_getter} != null")

            if not parts:
                st.error("Please select at least one condition and provide a value.")
            else:
                final_output = "#{\n  " + " and\n  ".join(parts) + "\n}"

        elif module == "SHIPPING_FWD":
            if is_reverse:
                warnings_list2 = []
                if rev_use_weight:
                    if rev_weight_min: validate_inputs(warnings_list2, "Min Box Weight", rev_weight_min, "number")
                    if rev_weight_max: validate_inputs(warnings_list2, "Max Box Weight", rev_weight_max, "number")
                if warnings_list2:
                    st.warning("⚠️ **Please review before using this rule:**")
                    for w in warnings_list2: st.markdown(f"- {w}")
                    st.write("")

                rev_parts = []
                if rev_channel_val.strip():
                    e = smart_format_string(rev_channel_val, "#reversePickup.saleOrder.channel.code", use_ignore_case=True)
                    if e: rev_parts.append(e)
                if rev_use_weight:
                    if rev_weight_min and rev_weight_max:
                        rev_parts.append(f"(#reversePickup.boxWeight > {rev_weight_min} and #reversePickup.boxWeight < {rev_weight_max})")
                    elif rev_weight_min:
                        rev_parts.append(f"#reversePickup.boxWeight > {rev_weight_min}")
                    elif rev_weight_max:
                        rev_parts.append(f"#reversePickup.boxWeight < {rev_weight_max}")
                if rev_use_state and rev_state_val.strip():
                    e = format_multi_value_condition(rev_state_val, "#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode")
                    if e: rev_parts.append(e)
                if rev_use_pincode and rev_pincode_val.strip():
                    e = format_multi_value_condition(rev_pincode_val, "#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode")
                    if e: rev_parts.append(e)
                if rev_use_city and rev_city_val.strip():
                    e = format_multi_value_condition(rev_city_val, "#reversePickup.saleOrder.shippingPackage.shippingAddress.city")
                    if e: rev_parts.append(e)
                if rev_use_payment and rev_payment_val:
                    rev_parts.append(f"#reversePickup.saleOrder.paymentMethod.code == '{rev_payment_val}'")
                if not rev_parts:
                    st.error("Please provide at least one condition for the Reverse Pickup rule.")
                else:
                    final_output = "#{\n  " + " and\n  ".join(rev_parts) + "\n}"
            else:
                if sp_use_channel and sp_channel_val.strip():
                    validate_inputs(warnings_list, "Channel Code", sp_channel_val, "channel")
                if sp_use_pincode and sp_pincode_val.strip():
                    validate_inputs(warnings_list, "Pincode", sp_pincode_val, "pincode")
                if sp_use_weight:
                    if sp_weight_min: validate_inputs(warnings_list, "Min Weight", sp_weight_min, "number")
                    if sp_weight_max: validate_inputs(warnings_list, "Max Weight", sp_weight_max, "number")
                if sp_use_price:
                    if sp_price_min: validate_inputs(warnings_list, "Min Price", sp_price_min, "number")
                    if sp_price_max: validate_inputs(warnings_list, "Max Price", sp_price_max, "number")
                if sp_use_item_count and sp_item_count_val:
                    validate_inputs(warnings_list, "Item Count", sp_item_count_val, "number")
                if warnings_list:
                    st.warning("⚠️ **Please review before using this rule:**")
                    for w in warnings_list: st.markdown(f"- {w}")
                    st.write("")

                parts = []
                if sp_use_channel and sp_channel_val.strip():
                    e = smart_format_string(sp_channel_val, "#shippingPackage.saleOrder.channel.code", sp_channel_icase, sp_channel_strip_spaces)
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
                    e = format_multi_value_condition(sp_country_val, "#shippingPackage.shippingAddress.countryCode")
                    if e: parts.append(e)
                if sp_use_item_count and sp_item_count_val:
                    parts.append(f"#shippingPackage.saleOrderItems.size() {sp_item_count_op} {sp_item_count_val}")
                if sp_use_item_tag and sp_item_tag_val.strip():
                    parts.append(f"#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('{sp_item_tag_val.strip()}')] != null")
                if sp_use_cf and sp_cf_field.strip():
                    sp_fn = sp_cf_field.strip()
                    sp_val = sp_cf_value.strip() if sp_cf_value else ""
                    sp_getter = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#shippingPackage.saleOrder, '{sp_fn}')"
                    sp_eff = f'{sp_getter}.replace(" ", "")' if sp_cf_strip_spaces else sp_getter
                    if sp_cf_match == "contains":
                        parts.append(f"{sp_getter} != null and {sp_eff}.contains('{sp_val}')")
                    elif sp_cf_match == "equalsIgnoreCase":
                        parts.append(f"{sp_eff}.equalsIgnoreCase('{sp_val}')")
                    elif sp_cf_match == "not_null":
                        parts.append(f"{sp_getter} != null")
                if not parts:
                    st.error("Please select at least one condition and provide a value.")
                else:
                    final_output = "#{\n  " + " and\n  ".join(parts) + "\n}"

        elif module == "INVENTORY_CALC":
            inv_part = "#inventorySnapshot.inventory"
            if v_inv: inv_part += " + #inventorySnapshot.virtualInventory"
            if v_nd:  inv_part += " + #inventorySnapshot.vendorInventory"
            deduct_part = ("- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) "
                           "- #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment")
            if unproc: deduct_part += " - #unprocessedOrderInventory"
            core_expr = f"{inv_part} {deduct_part}"
            if sub_type == "DEFAULT":   final_output = f"#{{{core_expr}}}"
            elif sub_type == "BUFFER_3": final_output = f"#{{({core_expr})<=3?0:({core_expr})}}"
            elif sub_type == "BUFFER_1": final_output = f"#{{({core_expr})<=1?0:({core_expr})}}"
            elif sub_type == "ZERO_SYNC": final_output = f"#{{({core_expr})*0}}"

        if final_output:
            st.success("✅ Rule compiled successfully")
            st.code(final_output, language="java")

# ===================================================================
# 🔍 RULE VALIDATOR
# ===================================================================

elif selected_tool == "validator":

    st.subheader("🔍 Rule Validator")
    st.caption("Paste any existing Uniware SpEL rule and instantly check it for known bugs and bad patterns.")

    st.info(
        "**What this checks for:**\n"
        "- Missing `#` prefix on variables (crashes entire allocation)\n"
        "- `equalsIngoreCase` typo (rule silently never matches)\n"
        "- `OR` without parentheses mixed with `AND` (precedence bug — real production incident)\n"
        "- `equalsAny()` with only one value (should be `==` instead)\n"
        "- Unquoted integers inside `equalsAny()` (type mismatch, never matches)\n"
        "- Trailing comma before `)` (parse error)\n"
        "- `.contains()` without null check on Custom Field (NullPointerException)\n"
        "- Plain text passed as SpEL (missing `#{}` wrapper)"
    )

    rule_input = st.text_area(
        "Paste SpEL Expression Here",
        height=160,
        placeholder="#{#shippingPackage.saleOrder.channel.code == 'SHOPIFY' and #shippingPackage.totalPrice <= 6000}",
        help="Paste the full expression including the #{ } wrapper. You can paste rules directly from Uniware's rule configuration screen."
    )

    if st.button("🔍 Validate Rule", type="primary"):
        if not rule_input.strip():
            st.error("Please paste a rule to validate.")
        else:
            issues = check_rule_for_issues(rule_input.strip())
            if not issues:
                st.success("✅ No known issues found. This rule looks clean.")
                st.caption("Note: this validator checks for known structural and syntax problems. It cannot verify that your business logic is correct, that field values exist in your tenant, or that the rule will match the orders you expect.")
            else:
                st.error(f"❌ Found {len(issues)} issue(s):")
                for i, issue in enumerate(issues, 1):
                    with st.expander(f"{issue['severity']} — Issue {i}", expanded=True):
                        st.markdown(f"**Problem:** {issue['message']}")
                        st.markdown(f"**Fix:** {issue['fix']}")

# ===================================================================
# 🔄 REVERSE COMPILER
# ===================================================================

elif selected_tool == "reverse":

    st.subheader("🔄 Reverse Compiler")
    st.caption("Paste any Uniware SpEL rule expression to decode it into plain English — useful for understanding rules you didn't write, or auditing existing rules.")

    rule_input = st.text_area(
        "Paste SpEL Expression to Decode",
        height=160,
        placeholder="#{T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.channel.code, 'FLIPKART', 'AMAZON_IN') and #allocationCriteria.hasCompleteShortTermInventory() and T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrderItem.shippingAddress.stateCode, 'MH', 'GJ')}",
        help="Paste the full SpEL expression including the #{ } wrapper. The decoder will break it down condition by condition."
    )

    if st.button("🔄 Decode Rule", type="primary"):
        if not rule_input.strip():
            st.error("Please paste a rule to decode.")
        else:
            decoded = decode_spel(rule_input.strip())
            if not decoded:
                st.warning("Could not decode this expression. Please verify it is a valid Uniware SpEL rule.")
            else:
                st.success(f"✅ Decoded — {len(decoded)} condition(s) found:")
                for label, value in decoded:
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.markdown(f"**{label}**")
                    with col2:
                        st.markdown(f"`{value}`")
                st.caption("If a condition shows as 'Condition: ...' it means it didn't match a known pattern and is shown as raw SpEL.")

# ===================================================================
# 📋 RULE AUDIT (DUMP SCANNER)
# ===================================================================

elif selected_tool == "audit":

    st.subheader("📋 Rule Audit — Dump Scanner")
    st.caption("Upload a Facility Allocation or Shipping Provider Allocation rule dump CSV exported from Uniware. The tool scans every rule for known bad patterns and flags issues.")

    st.info(
        "**Upload your rule dump CSV.** The file must have a `condition_expression` column. "
        "Export it from Uniware's rule configuration screen."
    )

    uploaded_file = st.file_uploader(
        "Upload Rule Dump CSV",
        type=["csv"],
        help="The CSV must contain a 'condition_expression' column. Other columns (name, preference, facility_id etc.) are shown alongside results but not required."
    )

    if uploaded_file:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file)

            if 'condition_expression' not in df.columns:
                st.error("❌ No `condition_expression` column found. Please upload a valid Uniware rule dump CSV.")
            else:
                st.success(f"✅ Loaded {len(df)} rules. Scanning...")

                all_issues = []
                for idx, row in df.iterrows():
                    expr = str(row.get('condition_expression', ''))
                    if not expr or expr.lower() in ('nan', 'true', ''):
                        continue
                    issues = check_rule_for_issues(expr)
                    if issues:
                        rule_name = str(row.get('name', f'Row {idx+2}'))
                        for issue in issues:
                            all_issues.append({
                                "Rule": rule_name,
                                "Severity": issue['severity'],
                                "Issue": issue['message'][:120],
                                "Fix": issue['fix'][:120],
                                "Expression": expr[:100] + "..." if len(expr) > 100 else expr
                            })

                if not all_issues:
                    st.success("🎉 No known bad patterns found across all rules!")
                else:
                    st.error(f"❌ Found {len(all_issues)} issue(s) across {len(set(i['Rule'] for i in all_issues))} rule(s):")

                    critical = [i for i in all_issues if "Critical" in i['Severity']]
                    high = [i for i in all_issues if "High" in i['Severity']]
                    medium = [i for i in all_issues if "Medium" in i['Severity']]

                    c1, c2, c3 = st.columns(3)
                    c1.metric("🔴 Critical", len(critical))
                    c2.metric("🟠 High", len(high))
                    c3.metric("🟡 Medium", len(medium))

                    st.write("")
                    issues_df = pd.DataFrame(all_issues)
                    st.dataframe(issues_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ===================================================================
# 💡 ANOMALY SUGGESTER
# ===================================================================

elif selected_tool == "anomaly":

    st.subheader("💡 Anomaly Suggester")
    st.caption("Upload a rule dump CSV to detect gaps, overlaps, duplicate rules, and dead rules in your configuration.")

    uploaded_file = st.file_uploader(
        "Upload Rule Dump CSV",
        type=["csv"],
        key="anomaly_upload",
        help="Upload the Facility Allocation or Shipping Provider Allocation rule dump exported from Uniware."
    )

    if uploaded_file:
        try:
            import pandas as pd
            df = pd.read_csv(uploaded_file)

            if 'condition_expression' not in df.columns:
                st.error("❌ No `condition_expression` column found.")
            else:
                st.success(f"✅ Loaded {len(df)} rules. Analysing...")
                exprs = df['condition_expression'].dropna().astype(str).tolist()
                anomalies = []

                # 1. Duplicate expressions
                seen_exprs = {}
                for idx, row in df.iterrows():
                    expr = str(row.get('condition_expression', '')).strip()
                    if expr in seen_exprs:
                        anomalies.append({
                            "Type": "🔁 Duplicate Rule",
                            "Detail": f"Rule '{row.get('name', idx)}' has identical condition_expression to '{seen_exprs[expr]}'. Only the higher-preference one will ever be used.",
                            "Suggestion": "Remove or consolidate the duplicate."
                        })
                    else:
                        seen_exprs[expr] = row.get('name', str(idx))

                # 2. TRUE / always-match rules
                true_rules = df[df['condition_expression'].astype(str).str.strip().str.lower() == 'true']
                if len(true_rules) > 1:
                    anomalies.append({
                        "Type": "⚠️ Multiple Always-Match Rules",
                        "Detail": f"{len(true_rules)} rules have `true` as their condition — they always match every order. Only the one with the highest preference will ever be reached.",
                        "Suggestion": "Ensure only one catch-all `true` rule exists, placed last (lowest preference)."
                    })

                # 3. Detect state codes used — check for gaps in common Indian states
                all_states_in_rules = set()
                for expr in exprs:
                    found = re.findall(r"'([A-Z]{2})'", expr)
                    india_codes = {code for code, name in COUNTRY_STATE_DATA['IN']['states']}
                    all_states_in_rules.update(s for s in found if s in india_codes)

                india_codes_all = {code for code, name in COUNTRY_STATE_DATA['IN']['states']}
                missing_states = india_codes_all - all_states_in_rules
                if missing_states and len(all_states_in_rules) > 3:
                    missing_names = []
                    for code, name in COUNTRY_STATE_DATA['IN']['states']:
                        if code in missing_states:
                            missing_names.append(f"{code} ({name})")
                    anomalies.append({
                        "Type": "📍 Uncovered Indian States",
                        "Detail": f"{len(missing_states)} Indian state code(s) not referenced in any rule: {', '.join(sorted(missing_names)[:10])}{'...' if len(missing_names) > 10 else ''}.",
                        "Suggestion": "If state-based routing is intended, verify these states have a catch-all or default rule covering them."
                    })

                # 4. Rules with no real condition (only 'true')
                catchall = df[df['condition_expression'].astype(str).str.strip().str.lower().isin(['true', '#{true}'])]
                if not catchall.empty:
                    anomalies.append({
                        "Type": "📋 Catch-All Rule(s) Detected",
                        "Detail": f"{len(catchall)} rule(s) use `true` as their condition — these will match every order that reaches them.",
                        "Suggestion": f"Verify these are intentional catch-alls and are placed last in priority: {', '.join(catchall['name'].astype(str).tolist()[:5])}."
                    })

                # 5. High preference number gaps
                if 'preference' in df.columns:
                    prefs = sorted(df['preference'].dropna().astype(int).tolist())
                    gaps = [prefs[i+1] - prefs[i] for i in range(len(prefs)-1) if prefs[i+1] - prefs[i] > 10]
                    if gaps:
                        anomalies.append({
                            "Type": "🔢 Large Preference Gaps",
                            "Detail": f"Found {len(gaps)} gap(s) of more than 10 between consecutive preference numbers. This may indicate rules were deleted but preference numbers were not recalculated.",
                            "Suggestion": "Review preference ordering to ensure evaluation order is intentional."
                        })

                if not anomalies:
                    st.success("🎉 No anomalies detected!")
                else:
                    st.warning(f"💡 Found {len(anomalies)} anomaly/anomalies:")
                    for a in anomalies:
                        with st.expander(a['Type'], expanded=True):
                            st.markdown(f"**Finding:** {a['Detail']}")
                            st.markdown(f"**Suggestion:** {a['Suggestion']}")

        except Exception as e:
            st.error(f"Error reading file: {e}")

# ===================================================================
# 🪵 LOKI LOG ANALYSER
# ===================================================================

elif selected_tool == "log":

    st.subheader("🪵 Loki Log Analyser")
    st.caption("Paste a Uniware error log (copied from Loki/Grafana or a trace log) for instant diagnosis. No manual reading required.")

    st.info(
        "**Diagnoses these errors automatically:**\n"
        "- `Property or field 'X' cannot be found on null` — missing `#` prefix or null context\n"
        "- `Failed to convert from type String to Boolean` — plain text passed as SpEL\n"
        "- `SpelEvaluationException` — general SpEL rule evaluation failure\n"
        "- `Failed to allocate shipping provider` — shipping allocation failure\n"
        "- `Failed to allocate facility` — facility allocation failure\n"
        "- `NullPointerException` in allocation context — null field access in rule"
    )

    log_input = st.text_area(
        "Paste Log Content Here",
        height=250,
        placeholder="Paste the full Loki/Grafana log output here...",
        help="Paste any portion of a Uniware log containing an error. You can paste the full stack trace — the analyser will extract the relevant parts."
    )

    if st.button("🔍 Analyse Log", type="primary"):
        if not log_input.strip():
            st.error("Please paste a log to analyse.")
        else:
            log = log_input
            findings = []

            # 1. Property or field cannot be found on null
            null_matches = re.findall(r"Property or field '(\w+)' cannot be found on null", log)
            if null_matches:
                for field in null_matches:
                    findings.append({
                        "severity": "🔴 Critical",
                        "title": f"Null Context — `{field}` not found",
                        "diagnosis": (
                            f"SpEL tried to access `.{field}` on an object that is null. "
                            f"This almost always means a rule references `{field}` without the `#` prefix "
                            f"(e.g. `{field}.something` instead of `#{field}.something`). "
                            f"Without `#`, SpEL treats it as a property on the root context object, which is null."
                        ),
                        "fix": (
                            f"Find every rule that contains `{field}.` and add the `#` prefix: "
                            f"`#{field}.someField`. Use the Rule Validator tool to scan all rules."
                        )
                    })

            # 2. Cannot convert String to Boolean
            bool_matches = re.findall(r"Failed to convert from type \[java\.lang\.String\] to type \[java\.lang\.Boolean\] for value '([^']+)'", log)
            if bool_matches:
                for val in bool_matches:
                    findings.append({
                        "severity": "🔴 Critical",
                        "title": "Plain Text Passed as SpEL Rule",
                        "diagnosis": (
                            f"The value `{val}` is plain text — it is not a valid SpEL expression. "
                            f"Uniware tried to evaluate it as a boolean condition but received a raw string, "
                            f"which it cannot convert. This crashes the entire allocation process, "
                            f"not just this one rule — which is why other rules appear to be skipped."
                        ),
                        "fix": (
                            f"Wrap the expression in `#{{...}}` and use valid SpEL syntax. "
                            f"For example, if the rule says `{val}`, it likely should be "
                            f"`#{{#shippingPackage.totalPrice >= {val.split('>= ')[-1] if '>=' in val else 'VALUE'}}}`. "
                            f"Use the Rule Compiler tool to build the correct expression."
                        )
                    })

            # 3. General SpelEvaluationException
            if 'SpelEvaluationException' in log and not null_matches and not bool_matches:
                spel_msg = re.search(r'SpelEvaluationException: ([^\n]+)', log)
                msg = spel_msg.group(1) if spel_msg else "See stack trace for details."
                findings.append({
                    "severity": "🔴 Critical",
                    "title": "SpEL Evaluation Exception",
                    "diagnosis": f"A SpEL rule failed to evaluate at runtime: `{msg}`. This crashes the entire allocation for this order — all rules fail, not just the broken one.",
                    "fix": "Identify which rule contains the problematic expression (check around the time shown in the log) and use the Rule Validator tool to check it."
                })

            # 4. Allocation failure type
            if 'Failed to allocate shipping provider' in log:
                order_match = re.search(r'SALE_ORDER/(\d+)', log)
                sp_match = re.search(r'shipping code (SP/[^\s]+)', log)
                findings.append({
                    "severity": "ℹ️ Context",
                    "title": "Shipping Provider Allocation Failed",
                    "diagnosis": (
                        f"Shipping provider allocation failed"
                        f"{' for order ' + order_match.group(1) if order_match else ''}"
                        f"{' (package ' + sp_match.group(1) + ')' if sp_match else ''}. "
                        f"This is the operation that triggered the error above."
                    ),
                    "fix": "Fix the SpEL rule error identified above. Once fixed, retry shipping provider allocation for this order."
                })

            if 'Failed to allocate facility' in log:
                findings.append({
                    "severity": "ℹ️ Context",
                    "title": "Facility Allocation Failed",
                    "diagnosis": "Facility allocation failed. This is the operation that triggered the error above.",
                    "fix": "Fix the SpEL rule error identified above. Once fixed, retry facility allocation for this order."
                })

            # 5. NullPointerException in allocation
            if 'NullPointerException' in log and 'SpelEvaluationException' not in log:
                findings.append({
                    "severity": "🟠 High",
                    "title": "NullPointerException in Allocation",
                    "diagnosis": "A null reference was accessed during rule evaluation. This usually means a rule calls a method (e.g. `.contains()`) on a value that may be null for this specific order.",
                    "fix": "Find rules that use `.contains()` or similar methods on Custom Field values and ensure they include a `!= null` check before the method call. Use the Rule Validator tool to scan."
                })

            # 6. Tenant / facility / order context
            tenant_match = re.search(r'\[HTTP-\d+:(\w+):', log)
            facility_match = re.search(r'UserContext Facility: (\S+)', log)
            order_match2 = re.search(r'SALE_ORDER/(\d+)', log)

            if not findings:
                st.success("✅ No known error patterns found in this log. The log may be informational — review the ERROR lines manually.")
            else:
                st.write("")
                if tenant_match or facility_match or order_match2:
                    with st.expander("📌 Log Context", expanded=False):
                        if tenant_match: st.markdown(f"**Tenant:** `{tenant_match.group(1)}`")
                        if facility_match: st.markdown(f"**Facility:** `{facility_match.group(1)}`")
                        if order_match2: st.markdown(f"**Sale Order:** `{order_match2.group(1)}`")

                for finding in findings:
                    with st.expander(f"{finding['severity']} — {finding['title']}", expanded=True):
                        st.markdown(f"**Diagnosis:** {finding['diagnosis']}")
                        st.markdown(f"**Fix:** {finding['fix']}")
