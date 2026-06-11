import streamlit as st
import re
import json

# =====================================================================
# SYSTEM CONFIGURATION & UI INITIALIZATION
# =====================================================================

st.set_page_config(
    page_title="UniCommerce Master Production Engine Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ UniCommerce Master Production Engine Suite")
st.caption("Version 8.0.0 | Complete Verified Multi-Parameter Rule Compiler Matrix")

# =====================================================================
# PRIMARY MODULE SELECTION
# =====================================================================

module = st.selectbox(
    "1. Select Operational Target Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY":       "Facility Allocation Engine (Warehouse Assignment / Routing Rules)",
        "SHIPPING_FWD":   "Shipping Provider Allocation Engine (Courier / Logistics Partner Selection)",
        "INVENTORY_CALC": "Inventory Synchronization Calculation Formula Wrapper"
    }[x]
)

# =====================================================================
# SUB TYPE
# =====================================================================

if module == "INVENTORY_CALC":
    sub_type = st.selectbox(
        "2. Choose Allocation Formula Variant",
        ["DEFAULT", "BUFFER_3", "BUFFER_1", "ZERO_SYNC"],
        format_func=lambda x: {
            "DEFAULT":   "Standard Global Marketplace Sync Formula",
            "BUFFER_3":  "Safety Buffer Guard (Syncs 0 if Stock <= 3)",
            "BUFFER_1":  "Safety Buffer Guard (Syncs 0 if Stock <= 1)",
            "ZERO_SYNC": "Absolute Forced Stock Suppress Override (Always Pushes 0)"
        }[x]
    )
else:
    sub_type = st.selectbox(
        "2. Choose Rule Evaluation Type",
        ["STANDARD_COMBINATIONS"],
        format_func=lambda x: "Configurable Multi-Parameter Combination Matrix"
    )

st.write("---")
st.write("### 3. Active Parameter Conditions Layer")

# =====================================================================
# HELPER METHODS
# =====================================================================

def csv_items(raw_input):
    return [x.strip() for x in raw_input.split(",") if x.strip()]

def quoted_csv(raw_input):
    return [f"'{x.strip()}'" for x in raw_input.split(",") if x.strip()]

def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """
    Single value  → var_name == 'VALUE'  or  var_name.equalsIgnoreCase('VALUE')
    Multiple CSV  → T(StringUtils).equalsAny(...)  or  equalsIgnoreCaseAny(...)
    Returns "" if blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    if len(items) == 1:
        val = items[0]
        if use_ignore_case:
            return f"{var_name}.equalsIgnoreCase('{val}')"
        else:
            return f"{var_name} == '{val}'"
    quoted = ", ".join(f"'{v}'" for v in items)
    func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
    return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {quoted})"

def format_multi_value_condition(raw_input, var_name):
    """
    Single value  → var_name == 'VALUE'
    Multiple CSV  → T(StringUtils).equalsAny(var_name, 'A', 'B', ...)
    Returns "" if blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    if len(items) == 1:
        return f"{var_name} == '{items[0]}'"
    quoted = ", ".join(f"'{v}'" for v in items)
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {quoted})"

# =====================================================================
# VALIDATION HELPERS
# =====================================================================

def validate_inputs(warnings, field_label, raw_input, field_type="generic"):
    """
    Checks common bad patterns and appends human-readable warnings.
    field_type: 'pincode' | 'state' | 'channel' | 'sku' | 'city' | 'number' | 'generic'
    """
    if not raw_input or not raw_input.strip():
        return
    items = [x.strip() for x in raw_input.split(",")]

    # Empty entry from trailing/double comma
    if any(i == "" for i in items):
        warnings.append(f"⚠️ **{field_label}**: Contains an empty entry (trailing or double comma). Remove extra commas.")

    clean = [i for i in items if i]

    # Duplicate values
    seen = set()
    dups = set()
    for i in clean:
        if i.lower() in seen:
            dups.add(i)
        seen.add(i.lower())
    if dups:
        warnings.append(f"⚠️ **{field_label}**: Duplicate value(s) detected — {', '.join(dups)}. Each value should appear only once.")

    if field_type == "pincode":
        for p in clean:
            if not re.match(r'^\d{6}$', p):
                warnings.append(f"⚠️ **{field_label}**: `{p}` does not look like a valid 6-digit Indian pincode.")
                break

    if field_type == "state":
        for s in clean:
            if not re.match(r'^[A-Z]{2,3}$', s):
                warnings.append(f"⚠️ **{field_label}**: `{s}` doesn't look like a valid state code (expected 2-3 uppercase letters like MH, GJ, KA).")
                break

    if field_type == "channel":
        for c in clean:
            if ' ' in c:
                warnings.append(f"⚠️ **{field_label}**: `{c}` contains a space. Channel codes should not have spaces.")
                break
            if c != c.upper():
                warnings.append(f"⚠️ **{field_label}**: `{c}` has mixed casing. Channel codes are typically uppercase — consider enabling Case-Insensitive Match.")
                break

    if field_type == "number":
        for n in clean:
            if not re.match(r'^\d+(\.\d+)?$', n):
                warnings.append(f"⚠️ **{field_label}**: `{n}` is not a valid number.")
                break

# =====================================================================
# REVERSE COMPILER — SpEL → UI field extraction
# =====================================================================

def parse_spel_to_fields(expr):
    """
    Parses a Uniware SpEL expression back into human-readable field descriptions.
    Returns a list of (field_label, value) tuples.
    """
    # Strip outer #{ }
    expr = expr.strip()
    if expr.startswith("#{") and expr.endswith("}"):
        expr = expr[2:-1].strip()

    fields = []

    # Split on ' and ' (case-insensitive) respecting parentheses
    def split_conditions(s):
        parts = []
        depth = 0
        current = []
        tokens = re.split(r'(\band\b)', s, flags=re.IGNORECASE)
        for token in tokens:
            if token.strip().lower() == 'and':
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(token)
        if current:
            parts.append(''.join(current).strip())
        return [p for p in parts if p]

    conditions = split_conditions(expr)

    for cond in conditions:
        cond = cond.strip()

        # equalsAny / equalsIgnoreCaseAny
        m = re.match(
            r'T\(com\.unifier\.core\.utils\.StringUtils\)\.(equalsAny|equalsIgnoreCaseAny)\(([^,]+),\s*(.+)\)',
            cond
        )
        if m:
            func, var, vals_str = m.group(1), m.group(2).strip(), m.group(3).strip()
            vals = re.findall(r"'([^']*)'", vals_str)
            label = _var_to_label(var)
            fields.append((label, ", ".join(vals)))
            continue

        # equalsIgnoreCase
        m = re.match(r'(#[\w.]+)\.equalsIgnoreCase\(\'([^\']+)\'\)', cond)
        if m:
            label = _var_to_label(m.group(1))
            fields.append((label + " (case-insensitive)", m.group(2)))
            continue

        # Simple equality  var == 'VALUE'
        m = re.match(r"(#[\w.]+)\s*==\s*'([^']*)'", cond)
        if m:
            label = _var_to_label(m.group(1))
            fields.append((label, m.group(2)))
            continue

        # Numeric comparison  var > N  var <= N
        m = re.match(r'(#[\w.]+)\s*([><=!]+)\s*(\d+(?:\.\d+)?)', cond)
        if m:
            label = _var_to_label(m.group(1))
            fields.append((label, f"{m.group(2)} {m.group(3)}"))
            continue

        # allocationCriteria method
        m = re.match(r'#allocationCriteria\.(\w+)\(\)', cond)
        if m:
            fields.append(("Inventory Criteria", m.group(1)))
            continue

        # hasAnyTag
        m = re.match(r".*hasAnyTag\('([^']+)'\)", cond)
        if m:
            fields.append(("Item Tag", m.group(1)))
            continue

        # brand.contains
        m = re.match(r".*brand\.contains\('([^']+)'\)", cond)
        if m:
            fields.append(("Brand", m.group(1)))
            continue

        # saleOrderItems.size()
        m = re.match(r'.*saleOrderItems\.size\(\)\s*([><=!]+)\s*(\d+)', cond)
        if m:
            fields.append(("Item Count", f"{m.group(1)} {m.group(2)}"))
            continue

        # boxWeight
        m = re.match(r'.*boxWeight\s*([><=]+)\s*(\d+)', cond)
        if m:
            fields.append(("Box Weight", f"{m.group(1)} {m.group(2)}"))
            continue

        # Parenthesised compound (boxWeight range)
        m = re.match(r'\((.*)\)', cond.strip())
        if m:
            inner = m.group(1)
            bw = re.findall(r'boxWeight\s*([><=]+)\s*(\d+)', inner)
            if bw:
                for op, val in bw:
                    fields.append(("Box Weight", f"{op} {val}"))
                continue

        # Inventory formula — just show as-is
        if "inventorySnapshot" in cond or "pendency" in cond:
            fields.append(("Inventory Formula", cond.strip()))
            continue

        # Fallback
        fields.append(("Condition", cond.strip()))

    return fields

def _var_to_label(var):
    mapping = {
        "#saleOrder.channel.code":                                              "Channel Code",
        "#shippingPackage.saleOrder.channel.code":                              "Channel Code",
        "#reversePickup.saleOrder.channel.code":                                "Return Channel Code",
        "#saleOrderItem.shippingAddress.stateCode":                             "State Code",
        "#shippingPackage.shippingAddress.stateCode":                           "State Code",
        "#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode":   "State Code (Return)",
        "#saleOrderItem.shippingAddress.pincode":                               "Pincode",
        "#shippingPackage.shippingAddress.pincode":                             "Pincode",
        "#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode":     "Pincode (Return)",
        "#saleOrderItem.shippingAddress.city":                                  "City",
        "#shippingPackage.shippingAddress.city":                                "City",
        "#reversePickup.saleOrder.shippingPackage.shippingAddress.city":        "City (Return)",
        "#saleOrderItem.shippingAddress.countryCode":                           "Country Code",
        "#shippingPackage.shippingAddress.countryCode":                         "Country Code",
        "#saleOrder.paymentMethod.code":                                        "Payment Method",
        "#shippingPackage.saleOrder.paymentMethod.code":                        "Payment Method",
        "#reversePickup.saleOrder.paymentMethod.code":                          "Payment Method (Return)",
        "#saleOrderItem.skuCode":                                               "SKU Code",
        "#shippingPackage.actualWeight":                                        "Package Weight (g)",
        "#shippingPackage.totalPrice":                                          "Total Price",
        "#reversePickup.boxWeight":                                             "Box Weight (g)",
    }
    return mapping.get(var.strip(), var.strip())

# =====================================================================
# BULK GENERATOR HELPER
# =====================================================================

def build_facility_rule(channel, inv, states, pincodes, city, payment, country, sku, tag, brand):
    parts = []
    if channel.strip():
        e = smart_format_string(channel, "#saleOrder.channel.code")
        if e: parts.append(e)
    if inv and inv != "NONE":
        parts.append(f"#allocationCriteria.{inv}()")
    if states.strip():
        e = format_multi_value_condition(states, "#saleOrderItem.shippingAddress.stateCode")
        if e: parts.append(e)
    if pincodes.strip():
        e = format_multi_value_condition(pincodes, "#saleOrderItem.shippingAddress.pincode")
        if e: parts.append(e)
    if city.strip():
        e = format_multi_value_condition(city, "#saleOrderItem.shippingAddress.city")
        if e: parts.append(e)
    if payment.strip():
        parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.paymentMethod.code, '{payment}')")
    if country.strip():
        e = format_multi_value_condition(country, "#saleOrderItem.shippingAddress.countryCode")
        if e: parts.append(e)
    if sku.strip():
        e = format_multi_value_condition(sku, "#saleOrderItem.skuCode")
        if e: parts.append(e)
    if tag.strip():
        parts.append(f"#saleOrder.saleOrderItems.^[itemType.hasAnyTag('{tag.strip()}')] != null")
    if brand.strip():
        parts.append(f"#saleOrder.saleOrderItems.^[itemType.brand.contains('{brand.strip()}')] != null")
    if not parts:
        return None
    return "#{\n  " + " and\n  ".join(parts) + "\n}"

def build_sp_rule(channel, icase, states, pincodes, wmin, wmax, pmin, pmax, payment, city, country, item_count_op, item_count_val):
    parts = []
    if channel.strip():
        e = smart_format_string(channel, "#shippingPackage.saleOrder.channel.code", icase)
        if e: parts.append(e)
    if states.strip():
        e = format_multi_value_condition(states, "#shippingPackage.shippingAddress.stateCode")
        if e: parts.append(e)
    if pincodes.strip():
        e = format_multi_value_condition(pincodes, "#shippingPackage.shippingAddress.pincode")
        if e: parts.append(e)
    if wmin.strip():
        parts.append(f"#shippingPackage.actualWeight > {wmin.strip()}")
    if wmax.strip():
        parts.append(f"#shippingPackage.actualWeight <= {wmax.strip()}")
    if pmin.strip():
        parts.append(f"#shippingPackage.totalPrice > {pmin.strip()}")
    if pmax.strip():
        parts.append(f"#shippingPackage.totalPrice <= {pmax.strip()}")
    if payment.strip():
        parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{payment}'")
    if city.strip():
        e = format_multi_value_condition(city, "#shippingPackage.shippingAddress.city")
        if e: parts.append(e)
    if country.strip():
        e = format_multi_value_condition(country, "#shippingPackage.shippingAddress.countryCode")
        if e: parts.append(e)
    if item_count_val.strip():
        parts.append(f"#shippingPackage.saleOrderItems.size() {item_count_op} {item_count_val.strip()}")
    if not parts:
        return None
    return "#{\n  " + " and\n  ".join(parts) + "\n}"

# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Channel Code**")
        fac_use_channel = st.checkbox("Apply Channel Code Filter", key="fac_use_channel",
            help="Single value → `== 'VALUE'`\nMultiple (comma-separated) → `equalsAny(...)`\nEnable case-insensitive if codes have mixed casing.")
        fac_channel_val = ""
        fac_channel_icase = False
        if fac_use_channel:
            fac_channel_val = st.text_input("Channel Code(s)", key="fac_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
            fac_channel_icase = st.checkbox("Case-Insensitive Match (equalsIgnoreCase)", key="fac_channel_icase",
                help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple values.")

    with col2:
        st.markdown("**Inventory Allocation Criteria**")
        fac_inv = st.selectbox("Inventory Criteria", [
                "NONE", "hasShortTermInventory", "hasCompleteShortTermInventory",
                "hasCompleteLongTermInventory", "hasCompleteInventory", "hasFulfillableInventory",
                "hasInventory", "hasLiveInventory", "hasLongTermInventory",
                "hasCompleteMidTermInventory", "hasAllocationWithinMaxOrderCapacity",
            ],
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
            help="• hasShortTermInventory — near-term stock available\n• hasCompleteShortTermInventory — all items have short-term stock\n• hasCompleteLongTermInventory — all items have long-term stock\n• hasCompleteInventory — full stock for all order items\n• hasFulfillableInventory — stock in fulfillable (non-blocked) state\n• hasInventory — any stock exists\n• hasLiveInventory — live, available-to-sell stock\n• hasAllocationWithinMaxOrderCapacity — facility under its order cap")

    st.write("")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**State Code**")
        fac_use_state = st.checkbox("Apply State Code Filter", key="fac_use_state",
            help="Single → `== 'MH'` | Multiple → `equalsAny(...)`\nUse 2-3 letter uppercase state codes: MH, GJ, KA, TN, DL")
        fac_state_val = ""
        if fac_use_state:
            fac_state_val = st.text_input("State Code(s)", key="fac_state_val",
                placeholder="Single: MH  |  Multiple: MH, GJ, KA, TN")

    with col4:
        st.markdown("**Pincode**")
        fac_use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode",
            help="Single → `== '560001'` | Multiple → `equalsAny(...)`\nEnter 6-digit pincodes. Values are auto-quoted as strings.")
        fac_pincode_val = ""
        if fac_use_pincode:
            fac_pincode_val = st.text_area("Pincode(s)", key="fac_pincode_val",
                placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=100)

    st.write("")
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("**City**")
        fac_use_city = st.checkbox("Apply City Filter", key="fac_use_city",
            help="Single → `== 'DELHI'` | Multiple → `equalsAny(...)`\nUse exact city name as stored in Uniware.")
        fac_city_val = ""
        if fac_use_city:
            fac_city_val = st.text_input("City / Cities", key="fac_city_val",
                placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi, Bangalore")

    with col6:
        st.markdown("**Payment Method**")
        fac_use_payment = st.checkbox("Apply Payment Method Filter", key="fac_use_payment",
            help="Filters by order payment type.\nPREPAID = online paid | COD = cash on delivery\nGenerates: `T(StringUtils).equalsAny(#saleOrder.paymentMethod.code, 'COD')`")
        fac_payment_val = ""
        if fac_use_payment:
            fac_payment_val = st.selectbox("Payment Method", ["PREPAID", "COD"], key="fac_payment_val",
                help="PREPAID = online/prepaid orders | COD = cash-on-delivery orders")

    st.write("")
    col7, col8 = st.columns(2)

    with col7:
        st.markdown("**Country Code**")
        fac_use_country = st.checkbox("Apply Country Code Filter", key="fac_use_country",
            help="Single → `== 'IN'` | Multiple → `equalsAny(...)`\nSeparates domestic (IN) from international routing.")
        fac_country_val = ""
        if fac_use_country:
            fac_country_val = st.text_input("Country Code(s)", key="fac_country_val",
                placeholder="Single: IN  |  Multiple: IN, US, AE")

    with col8:
        st.markdown("**SKU Code**")
        fac_use_sku = st.checkbox("Apply SKU Code Filter", key="fac_use_sku",
            help="Single → `#saleOrderItem.skuCode == 'SKU001'`\nMultiple → `equalsAny(#saleOrderItem.skuCode, 'A', 'B')`\nMatches the individual order item's SKU.")
        fac_sku_val = ""
        if fac_use_sku:
            fac_sku_val = st.text_area("SKU Code(s)", key="fac_sku_val",
                placeholder="Single: SKU001  |  Multiple: SKU001, SKU002, SKU003", height=100)

    st.write("")
    col9, col10 = st.columns(2)

    with col9:
        st.markdown("**Item Tag (hasAnyTag)**")
        fac_use_item_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_item_tag",
            help="Checks if any item in the order has a specific tag in the item master.\nGenerates: `#saleOrder.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`\nUseful for routing hazardous, fragile, or brand-specific items.")
        fac_item_tag_val = ""
        if fac_use_item_tag:
            fac_item_tag_val = st.text_input("Item Tag Value", key="fac_item_tag_val",
                placeholder="e.g. SWAYAM  or  Infinity_Goodies")

    with col10:
        st.markdown("**Brand (contains match)**")
        fac_use_brand = st.checkbox("Apply Brand Filter", key="fac_use_brand",
            help="Checks if any order item belongs to a specific brand (partial contains match).\nGenerates: `#saleOrder.saleOrderItems.^[itemType.brand.contains('BRAND')] != null`")
        fac_brand_val = ""
        if fac_use_brand:
            fac_brand_val = st.text_input("Brand Name", key="fac_brand_val",
                placeholder="e.g. Trend Arrest")

    st.write("")

# =====================================================================
# SHIPPING PROVIDER ALLOCATION MODULE
# =====================================================================

elif module == "SHIPPING_FWD":

    st.subheader("🚚 Shipping Provider Allocation Rule Constructor")

    st.markdown("**Rule Context**")
    is_reverse = st.checkbox("This is a Reverse Pickup / Return Rule  (uses #reversePickup context)",
        key="sp_is_reverse",
        help="ON → uses `#reversePickup` variable and `reversePickup.boxWeight` for weight.\nOFF → standard forward shipment using `#shippingPackage`.")

    st.write("")

    if is_reverse:
        st.markdown("##### Reverse Pickup Conditions")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Return Channel Code**")
            rev_channel_val = st.text_input("Return Channel Code(s)", key="rev_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: SHOPIFY, CUSTOM",
                help="Single → `#reversePickup.saleOrder.channel.code.equalsIgnoreCase('VALUE')`\nMultiple → `T(StringUtils).equalsAny(...)`\nAlways case-insensitive for reverse pickup.")

        with col2:
            st.markdown("**Box Weight (grams)**")
            rev_use_weight = st.checkbox("Apply Box Weight Filter", key="rev_use_weight",
                help="Uses `#reversePickup.boxWeight` with exclusive bounds on BOTH sides.\nMin → `> value` | Max → `< value`\nExample: Min=0, Max=4999 → `(#reversePickup.boxWeight > 0 and #reversePickup.boxWeight < 4999)`")
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
                help="Uses `#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            rev_state_val = ""
            if rev_use_state:
                rev_state_val = st.text_input("State Code(s)", key="rev_state_val",
                    placeholder="Single: MH  |  Multiple: MH, KA, UP, WB")

        with col4:
            st.markdown("**Pincode**")
            rev_use_pincode = st.checkbox("Apply Pincode Filter", key="rev_use_pincode",
                help="Uses `#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            rev_pincode_val = ""
            if rev_use_pincode:
                rev_pincode_val = st.text_area("Pincode(s)", key="rev_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=100)

        st.write("")
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**City**")
            rev_use_city = st.checkbox("Apply City Filter", key="rev_use_city",
                help="Uses `#reversePickup.saleOrder.shippingPackage.shippingAddress.city`.")
            rev_city_val = ""
            if rev_use_city:
                rev_city_val = st.text_input("City / Cities", key="rev_city_val",
                    placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi")

        with col6:
            st.markdown("**Payment Method**")
            rev_use_payment = st.checkbox("Apply Payment Method Filter", key="rev_use_payment",
                help="Uses `#reversePickup.saleOrder.paymentMethod.code == 'COD'` or `'PREPAID'`.")
            rev_payment_val = ""
            if rev_use_payment:
                rev_payment_val = st.selectbox("Payment Method", ["COD", "PREPAID"], key="rev_payment_val",
                    help="COD = cash-on-delivery | PREPAID = prepaid/online paid")

        st.write("")

    else:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Channel Code**")
            sp_use_channel = st.checkbox("Apply Channel Code Filter", key="sp_use_channel",
                help="Single → `#shippingPackage.saleOrder.channel.code == 'VALUE'`\nMultiple → `equalsAny(...)`\nEnable case-insensitive if codes have mixed casing.")
            sp_channel_val = ""
            sp_channel_icase = False
            if sp_use_channel:
                sp_channel_val = st.text_input("Channel Code(s)", key="sp_channel_val",
                    placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN")
                sp_channel_icase = st.checkbox("Case-Insensitive Match (equalsIgnoreCase)", key="sp_channel_icase",
                    help="Uses `.equalsIgnoreCase()` for single or `equalsIgnoreCaseAny()` for multiple.")

        with col2:
            st.markdown("**State Code**")
            sp_use_state = st.checkbox("Apply State Code Filter", key="sp_use_state",
                help="Uses `#shippingPackage.shippingAddress.stateCode`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            sp_state_val = ""
            if sp_use_state:
                sp_state_val = st.text_input("State Code(s)", key="sp_state_val",
                    placeholder="Single: MH  |  Multiple: MH, GJ, KA")

        st.write("")
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Pincode**")
            sp_use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode",
                help="Uses `#shippingPackage.shippingAddress.pincode`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            sp_pincode_val = ""
            if sp_use_pincode:
                sp_pincode_val = st.text_area("Pincode(s)", key="sp_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001", height=100)

        with col4:
            st.markdown("**Payment Method**")
            sp_use_payment = st.checkbox("Apply Payment Method Filter", key="sp_use_payment",
                help="Generates: `#shippingPackage.saleOrder.paymentMethod.code == 'COD'`\nUse for dedicated COD or prepaid courier routing.")
            sp_payment_val = ""
            if sp_use_payment:
                sp_payment_val = st.selectbox("Payment Method", ["COD", "PREPAID"], key="sp_payment_val",
                    help="COD = cash-on-delivery | PREPAID = online/prepaid orders")

        st.write("")
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**Package Weight (grams)**")
            sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight",
                help="Uses `#shippingPackage.actualWeight`.\nMin → exclusive `>` | Max → inclusive `<=`\nExample: Min=500, Max=1000 → `actualWeight > 500 and actualWeight <= 1000`")
            sp_weight_min = ""
            sp_weight_max = ""
            if sp_use_weight:
                sp_weight_min = st.text_input("Min Weight — exclusive > (blank = no lower bound)", key="sp_weight_min", placeholder="e.g. 500").strip()
                sp_weight_max = st.text_input("Max Weight — inclusive <= (blank = no upper bound)", key="sp_weight_max", placeholder="e.g. 1000").strip()

        with col6:
            st.markdown("**Total Order Price**")
            sp_use_price = st.checkbox("Apply Price Filter", key="sp_use_price",
                help="Uses `#shippingPackage.totalPrice`.\nMin → exclusive `>` | Max → inclusive `<=`\nExample: Max=6000 → `totalPrice <= 6000`")
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
                help="Uses `#shippingPackage.shippingAddress.city`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            sp_city_val = ""
            if sp_use_city:
                sp_city_val = st.text_input("City / Cities", key="sp_city_val",
                    placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi")

        with col8:
            st.markdown("**Country Code**")
            sp_use_country = st.checkbox("Apply Country Code Filter", key="sp_use_country",
                help="Uses `#shippingPackage.shippingAddress.countryCode`.\nSingle → `==` | Multiple → `equalsAny(...)`")
            sp_country_val = ""
            if sp_use_country:
                sp_country_val = st.text_input("Country Code(s)", key="sp_country_val",
                    placeholder="Single: IN  |  Multiple: IN, US, AE")

        st.write("")
        col9, col10 = st.columns(2)

        with col9:
            st.markdown("**Number of Items in Package**")
            sp_use_item_count = st.checkbox("Apply Item Count Filter", key="sp_use_item_count",
                help="Uses `#shippingPackage.saleOrderItems.size()` with your chosen operator.\nExample: `<= 12` → package has at most 12 line items.\nUseful for assigning different couriers for single-item vs bulk shipments.")
            sp_item_count_op = "<="
            sp_item_count_val = ""
            if sp_use_item_count:
                sp_item_count_op = st.selectbox("Operator", ["<=", "<", ">=", ">", "=="],
                    format_func=lambda x: {
                        "<=": "<= (Up to N items — e.g. single or small shipments)",
                        "<":  "<  (Fewer than N items — strictly less)",
                        ">=": ">= (At least N items — e.g. bulk shipments)",
                        ">":  ">  (More than N items — strictly greater)",
                        "==": "== (Exactly N items)"
                    }[x], key="sp_item_count_op",
                    help="• `<=` — up to N items (e.g. `<= 1` = single-item only)\n• `<` — fewer than N (strictly)\n• `>=` — at least N items (bulk threshold)\n• `>` — more than N (strictly)\n• `==` — exactly N items")
                sp_item_count_val = st.text_input("Item Count Threshold", key="sp_item_count_val", placeholder="e.g. 12").strip()

        with col10:
            st.write("")

        st.write("")

# =====================================================================
# INVENTORY CALCULATION MODULE
# =====================================================================

elif module == "INVENTORY_CALC":

    st.subheader("🛠️ Global Synchronizer Formula Constructor")

    v_inv = st.checkbox("Incorporate Virtual Allocated Stock Threshold Multipliers", key="calc_v_inv",
        help="Adds `#inventorySnapshot.virtualInventory` to the base formula.\nEnable when your channel sync should include virtual/buffer stock reservations.")
    v_nd = st.checkbox("Incorporate Vendor Catalog Shared Warehouse Stock Pools", key="calc_v_nd",
        help="Adds `#inventorySnapshot.vendorInventory` to the base formula.\nEnable for channels that can fulfil from vendor/drop-ship locations.")
    unproc = st.checkbox("Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)", key="calc_unproc",
        help="DEDUCTS `#unprocessedOrderInventory` from the formula.\nUnprocessed orders consume stock but haven't entered Uniware's pipeline yet.\nCritical for Amazon Flex and slab-based channel integrations.")

st.write("")

# =====================================================================
# FINAL COMPILER
# =====================================================================

if st.button("⚙️ Compile Target Token Blueprint", type="primary"):

    final_output = ""
    warnings = []

    # =================================================================
    # FACILITY RULE COMPILER
    # =================================================================

    if module == "FACILITY":

        # ── Input validation ─────────────────────────────────────────
        if fac_use_channel and fac_channel_val.strip():
            validate_inputs(warnings, "Channel Code", fac_channel_val, "channel")
        if fac_use_state and fac_state_val.strip():
            validate_inputs(warnings, "State Code", fac_state_val, "state")
        if fac_use_pincode and fac_pincode_val.strip():
            validate_inputs(warnings, "Pincode", fac_pincode_val, "pincode")
        if fac_use_city and fac_city_val.strip():
            validate_inputs(warnings, "City", fac_city_val, "generic")
        if fac_use_country and fac_country_val.strip():
            validate_inputs(warnings, "Country Code", fac_country_val, "generic")
        if fac_use_sku and fac_sku_val.strip():
            validate_inputs(warnings, "SKU Code", fac_sku_val, "generic")

        if warnings:
            for w in warnings:
                st.warning(w)

        parts = []

        if fac_use_channel and fac_channel_val.strip():
            e = smart_format_string(fac_channel_val, "#saleOrder.channel.code", fac_channel_icase)
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
            parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.paymentMethod.code, '{fac_payment_val}')")
        if fac_use_country and fac_country_val.strip():
            e = format_multi_value_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode")
            if e: parts.append(e)
        if fac_use_sku and fac_sku_val.strip():
            e = format_multi_value_condition(fac_sku_val, "#saleOrderItem.skuCode")
            if e: parts.append(e)
        if fac_use_item_tag and fac_item_tag_val.strip():
            parts.append(f"#saleOrder.saleOrderItems.^[itemType.hasAnyTag('{fac_item_tag_val.strip()}')] != null")
        if fac_use_brand and fac_brand_val.strip():
            parts.append(f"#saleOrder.saleOrderItems.^[itemType.brand.contains('{fac_brand_val.strip()}')] != null")

        if not parts:
            st.error("Validation Error: Please select at least one condition and provide a value.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"

    # =================================================================
    # SHIPPING PROVIDER RULE COMPILER
    # =================================================================

    elif module == "SHIPPING_FWD":

        if is_reverse:
            if rev_channel_val.strip():
                validate_inputs(warnings, "Return Channel Code", rev_channel_val, "channel")
            if rev_use_state and rev_state_val.strip():
                validate_inputs(warnings, "State Code", rev_state_val, "state")
            if rev_use_pincode and rev_pincode_val.strip():
                validate_inputs(warnings, "Pincode", rev_pincode_val, "pincode")
            if rev_use_weight:
                if rev_weight_min: validate_inputs(warnings, "Min Box Weight", rev_weight_min, "number")
                if rev_weight_max: validate_inputs(warnings, "Max Box Weight", rev_weight_max, "number")
            if warnings:
                for w in warnings: st.warning(w)

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
                st.error("Validation Error: Please provide at least one condition for the Reverse Pickup rule.")
            else:
                final_output = "#{\n  " + " and \n  ".join(rev_parts) + "\n}"

        else:
            if sp_use_channel and sp_channel_val.strip():
                validate_inputs(warnings, "Channel Code", sp_channel_val, "channel")
            if sp_use_state and sp_state_val.strip():
                validate_inputs(warnings, "State Code", sp_state_val, "state")
            if sp_use_pincode and sp_pincode_val.strip():
                validate_inputs(warnings, "Pincode", sp_pincode_val, "pincode")
            if sp_use_weight:
                if sp_weight_min: validate_inputs(warnings, "Min Weight", sp_weight_min, "number")
                if sp_weight_max: validate_inputs(warnings, "Max Weight", sp_weight_max, "number")
            if sp_use_price:
                if sp_price_min: validate_inputs(warnings, "Min Price", sp_price_min, "number")
                if sp_price_max: validate_inputs(warnings, "Max Price", sp_price_max, "number")
            if sp_use_item_count and sp_item_count_val:
                validate_inputs(warnings, "Item Count", sp_item_count_val, "number")
            if warnings:
                for w in warnings: st.warning(w)

            parts = []
            if sp_use_channel and sp_channel_val.strip():
                e = smart_format_string(sp_channel_val, "#shippingPackage.saleOrder.channel.code", sp_channel_icase)
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

            if not parts:
                st.error("Validation Error: Please select at least one condition and provide a value.")
            else:
                final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"

    # =================================================================
    # INVENTORY CALCULATION
    # =================================================================

    elif module == "INVENTORY_CALC":
        inv_part = "#inventorySnapshot.inventory"
        if v_inv: inv_part += " + #inventorySnapshot.virtualInventory"
        if v_nd:  inv_part += " + #inventorySnapshot.vendorInventory"
        deduct_part = (
            "- #inventorySnapshot.openSale "
            "- #pendency "
            "- (#failedOrderInventory?:0) "
            "- #inventoryBlockedOnOtherChannels "
            "- #inventorySnapshot.pendingInventoryAssessment"
        )
        if unproc: deduct_part += " - #unprocessedOrderInventory"
        core_expr = f"{inv_part} {deduct_part}"
        if sub_type == "DEFAULT":   final_output = f"#{{{core_expr}}}"
        elif sub_type == "BUFFER_3": final_output = f"#{{({core_expr})<=3?0:({core_expr})}}"
        elif sub_type == "BUFFER_1": final_output = f"#{{({core_expr})<=1?0:({core_expr})}}"
        elif sub_type == "ZERO_SYNC": final_output = f"#{{({core_expr})*0}}"

    # =================================================================
    # OUTPUT + COPY BUTTON
    # =================================================================

    if final_output:
        st.subheader("📋 Compiled System Token String (Copy directly to Uniware)")
        st.code(final_output, language="java")
        st.button(
            "📋 Copy to Clipboard",
            on_click=lambda: st.write(
                f"<script>navigator.clipboard.writeText({json.dumps(final_output)})</script>",
                unsafe_allow_html=True
            ),
            key="copy_btn",
            help="Copies the compiled rule to your clipboard"
        )

st.write("---")

# =====================================================================
# ADVANCED TOOLS
# =====================================================================

with st.expander("🔍 Rule Explainer — Paste a SpEL expression to decode it"):
    st.caption("Paste any existing Uniware SpEL rule and get a plain-English breakdown of what it does.")
    explain_input = st.text_area("Paste SpEL Expression", key="explain_input",
        placeholder="e.g. #{#saleOrder.channel.code == 'SHOPIFY' and #allocationCriteria.hasCompleteShortTermInventory()}", height=120)
    if st.button("🔎 Explain This Rule", key="btn_explain"):
        if not explain_input.strip():
            st.error("Please paste a SpEL expression to explain.")
        else:
            fields = parse_spel_to_fields(explain_input.strip())
            if not fields:
                st.warning("Could not parse the expression. Please check it is a valid Uniware SpEL rule.")
            else:
                st.success("✅ Rule decoded successfully:")
                for label, value in fields:
                    st.markdown(f"- **{label}**: `{value}`")

st.write("")

with st.expander("🔄 Reverse Compiler — Decode a SpEL expression back to its parameters"):
    st.caption("Paste any existing Uniware rule expression to extract all its individual parameter values.")
    reverse_input = st.text_area("Paste SpEL Expression to Decode", key="reverse_input",
        placeholder="e.g. #{T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.channel.code, 'FLIPKART', 'AMAZON_IN') and #allocationCriteria.hasCompleteShortTermInventory() and T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrderItem.shippingAddress.stateCode, 'MH', 'GJ')}",
        height=120)
    if st.button("🔄 Decode Rule", key="btn_reverse"):
        if not reverse_input.strip():
            st.error("Please paste a SpEL expression to decode.")
        else:
            fields = parse_spel_to_fields(reverse_input.strip())
            if not fields:
                st.warning("Could not decode the expression. Please verify it is a valid Uniware SpEL rule.")
            else:
                st.success("✅ Decoded parameters:")
                rc1, rc2 = st.columns(2)
                for i, (label, value) in enumerate(fields):
                    with (rc1 if i % 2 == 0 else rc2):
                        st.info(f"**{label}**\n\n`{value}`")

st.write("")

with st.expander("📋 Natural Language Rule Generator — Describe your rule in plain English"):
    st.caption("Type what you want your rule to do. The tool will generate the correct SpEL expression.")

    nl_module = st.selectbox("Module for this rule", ["FACILITY", "SHIPPING_FWD"], key="nl_module",
        format_func=lambda x: "Facility Allocation" if x == "FACILITY" else "Shipping Provider (Forward)")

    nl_input = st.text_area("Describe your rule in plain English", key="nl_input",
        placeholder=(
            "Examples:\n"
            "- Route all COD orders going to Maharashtra and Gujarat to this facility\n"
            "- Assign courier only for SHOPIFY orders weighing between 500g and 1000g with value under 6000\n"
            "- Match orders with SKU ABC123 going to Delhi pincode 110001"
        ), height=130)

    if st.button("✨ Generate Rule from Description", key="btn_nl"):
        if not nl_input.strip():
            st.error("Please describe your rule first.")
        else:
            txt = nl_input.lower()

            # ── Channel ──
            ch_match = re.search(r'\b(shopify|flipkart|amazon[_\s]in|amazon|myntra|meesho|ajio|woocommerce|magento|custom)\b', txt)
            ch_val = ch_match.group(1).upper().replace(" ", "_") if ch_match else ""

            # ── States ──
            state_map = {
                "maharashtra": "MH", "gujarat": "GJ", "karnataka": "KA",
                "tamil nadu": "TN", "delhi": "DL", "rajasthan": "RJ",
                "uttar pradesh": "UP", "west bengal": "WB", "kerala": "KL",
                "andhra pradesh": "AP", "telangana": "TG", "madhya pradesh": "MP",
                "punjab": "PB", "haryana": "HR", "bihar": "BR", "odisha": "OD"
            }
            states_found = [code for name, code in state_map.items() if name in txt]

            # ── Payment ──
            payment = ""
            if "cod" in txt or "cash on delivery" in txt or "cash-on-delivery" in txt:
                payment = "COD"
            elif "prepaid" in txt or "online" in txt:
                payment = "PREPAID"

            # ── Weight ──
            w_range = re.search(r'weight(?:ing)?\s+(?:between\s+)?(\d+)\s*g?\s*(?:and|to|-)\s*(\d+)\s*g?', txt)
            w_min = w_range.group(1) if w_range else ""
            w_max = w_range.group(2) if w_range else ""
            if not w_range:
                w_lt = re.search(r'(?:under|below|less than|lighter than)\s+(\d+)\s*g', txt)
                w_gt = re.search(r'(?:above|over|more than|heavier than)\s+(\d+)\s*g', txt)
                w_min = w_gt.group(1) if w_gt else ""
                w_max = w_lt.group(1) if w_lt else ""

            # ── Price ──
            p_range = re.search(r'(?:value|price|order value)\s+(?:between\s+)?(?:rs\.?\s*|inr\s*|₹\s*)?(\d+)\s*(?:and|to|-)\s*(?:rs\.?\s*|inr\s*|₹\s*)?(\d+)', txt)
            p_min = p_range.group(1) if p_range else ""
            p_max = p_range.group(2) if p_range else ""
            if not p_range:
                p_lt = re.search(r'(?:under|below|value less than|under rs\.?\s*|under ₹\s*)(\d+)', txt)
                p_gt = re.search(r'(?:above|over|value more than|above rs\.?\s*|above ₹\s*)(\d+)', txt)
                p_min = p_gt.group(1) if p_gt else ""
                p_max = p_lt.group(1) if p_lt else ""

            # ── Pincode ──
            pincodes = re.findall(r'\b(\d{6})\b', txt)
            pin_val = ", ".join(pincodes) if pincodes else ""

            # ── SKU ──
            sku_match = re.search(r'sku\s+([A-Z0-9_\-]+)', nl_input, re.IGNORECASE)
            sku_val = sku_match.group(1) if sku_match else ""

            # ── Inventory (facility only) ──
            inv = "NONE"
            if "complete short" in txt: inv = "hasCompleteShortTermInventory"
            elif "short term" in txt: inv = "hasShortTermInventory"
            elif "complete long" in txt: inv = "hasCompleteLongTermInventory"
            elif "long term" in txt: inv = "hasLongTermInventory"
            elif "fulfillable" in txt: inv = "hasFulfillableInventory"
            elif "complete inventory" in txt: inv = "hasCompleteInventory"

            # ── Build rule ──
            if nl_module == "FACILITY":
                result = build_facility_rule(
                    channel=ch_val,
                    inv=inv,
                    states=", ".join(states_found),
                    pincodes=pin_val,
                    city="",
                    payment=payment,
                    country="",
                    sku=sku_val,
                    tag="",
                    brand=""
                )
            else:
                result = build_sp_rule(
                    channel=ch_val,
                    icase=False,
                    states=", ".join(states_found),
                    pincodes=pin_val,
                    wmin=w_min,
                    wmax=w_max,
                    pmin=p_min,
                    pmax=p_max,
                    payment=payment,
                    city="",
                    country="",
                    item_count_op="<=",
                    item_count_val=""
                )

            if result:
                st.success("✅ Generated rule based on your description:")
                st.code(result, language="java")
                st.caption("ℹ️ Review the output carefully. For complex or unusual combinations, use the Rule Compiler above for full precision.")
            else:
                st.warning("Could not extract enough information from your description. Try being more specific — include channel name, state names, payment type, or weight/price ranges.")

st.write("")

with st.expander("📦 Bulk Rule Generator — Generate multiple rules from a table"):
    st.caption(
        "Paste a CSV table to generate multiple rules at once.\n\n"
        "**Facility CSV columns** (all optional except at least one must have a value):\n"
        "`channel, inventory_criteria, states, pincodes, city, payment, country, sku, item_tag, brand`\n\n"
        "**Shipping Provider CSV columns**:\n"
        "`channel, states, pincodes, weight_min, weight_max, price_min, price_max, payment, city, country, item_count_op, item_count_val`\n\n"
        "Leave a cell blank to skip that condition for that row."
    )

    bulk_module = st.selectbox("Module for bulk rules", ["FACILITY", "SHIPPING_FWD"], key="bulk_module",
        format_func=lambda x: "Facility Allocation" if x == "FACILITY" else "Shipping Provider (Forward)")

    bulk_csv = st.text_area("Paste CSV data here", key="bulk_csv", height=180,
        placeholder=(
            "FACILITY example:\nchannel,inventory_criteria,states,payment\nSHOPIFY,hasCompleteShortTermInventory,MH,COD\nFLIPKART,hasInventory,GJ,PREPAID\n\n"
            "SHIPPING_FWD example:\nchannel,weight_min,weight_max,payment\nSHOPIFY,0,500,COD\nSHOPIFY,500,1000,PREPAID"
        ))

    if st.button("🚀 Generate Bulk Rules", key="btn_bulk"):
        if not bulk_csv.strip():
            st.error("Please paste CSV data first.")
        else:
            lines = [l.strip() for l in bulk_csv.strip().splitlines() if l.strip()]
            if len(lines) < 2:
                st.error("CSV must have a header row and at least one data row.")
            else:
                headers = [h.strip().lower() for h in lines[0].split(",")]
                results = []
                errors = []

                for row_num, line in enumerate(lines[1:], start=2):
                    vals = [v.strip() for v in line.split(",")]
                    # Pad if fewer columns than headers
                    while len(vals) < len(headers):
                        vals.append("")
                    row = dict(zip(headers, vals))

                    if bulk_module == "FACILITY":
                        rule = build_facility_rule(
                            channel=row.get("channel", ""),
                            inv=row.get("inventory_criteria", "NONE") or "NONE",
                            states=row.get("states", ""),
                            pincodes=row.get("pincodes", ""),
                            city=row.get("city", ""),
                            payment=row.get("payment", ""),
                            country=row.get("country", ""),
                            sku=row.get("sku", ""),
                            tag=row.get("item_tag", ""),
                            brand=row.get("brand", "")
                        )
                    else:
                        rule = build_sp_rule(
                            channel=row.get("channel", ""),
                            icase=False,
                            states=row.get("states", ""),
                            pincodes=row.get("pincodes", ""),
                            wmin=row.get("weight_min", ""),
                            wmax=row.get("weight_max", ""),
                            pmin=row.get("price_min", ""),
                            pmax=row.get("price_max", ""),
                            payment=row.get("payment", ""),
                            city=row.get("city", ""),
                            country=row.get("country", ""),
                            item_count_op=row.get("item_count_op", "<="),
                            item_count_val=row.get("item_count_val", "")
                        )

                    if rule:
                        results.append((row_num, rule))
                    else:
                        errors.append(f"Row {row_num}: No valid conditions found — skipped.")

                if errors:
                    for e in errors:
                        st.warning(e)

                if results:
                    st.success(f"✅ Generated {len(results)} rule(s):")
                    all_rules = "\n\n".join(f"-- Row {rn} --\n{rule}" for rn, rule in results)
                    st.text_area("All Generated Rules (copy all)", value=all_rules,
                        height=min(400, 80 * len(results)), key="bulk_output")
                    for row_num, rule in results:
                        with st.expander(f"Row {row_num}"):
                            st.code(rule, language="java")
                else:
                    st.error("No valid rules could be generated. Check your CSV data and column names.")
