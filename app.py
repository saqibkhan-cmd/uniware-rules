import streamlit as st
import re

# =====================================================================
# SYSTEM CONFIGURATION & UI INITIALIZATION
# =====================================================================

st.set_page_config(
    page_title="UniCommerce Master Production Engine Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ UniCommerce Master Production Engine Suite")
st.caption("Version 7.1.0 | Complete Verified Multi-Parameter Rule Compiler Matrix")

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
    Single value  -> var_name == 'VALUE'  or  var_name.equalsIgnoreCase('VALUE')
    Multiple CSV  -> T(StringUtils).equalsAny(...)  or  equalsIgnoreCaseAny(...)
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
    Single value  -> var_name == 'VALUE'
    Multiple CSV  -> T(StringUtils).equalsAny(var_name, 'A', 'B', ...)
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
# VALIDATION HELPER
# =====================================================================

def validate_inputs(warnings_list, field_label, raw_input, field_type="generic"):
    """
    Checks for common bad patterns and appends warnings to warnings_list.
    field_type: 'pincode' | 'state' | 'channel' | 'number' | 'generic'
    """
    if not raw_input or not raw_input.strip():
        return

    items = [x.strip() for x in raw_input.split(",")]

    # Trailing / double comma produces empty entry
    if any(i == "" for i in items):
        warnings_list.append(
            f"**{field_label}:** Contains an empty entry — check for a trailing or double comma."
        )

    clean = [i for i in items if i]

    # Duplicate values
    seen, dups = set(), set()
    for i in clean:
        if i.lower() in seen:
            dups.add(i)
        seen.add(i.lower())
    if dups:
        warnings_list.append(
            f"**{field_label}:** Duplicate value(s) found — `{'`, `'.join(dups)}`. "
            "Each value should appear only once."
        )

    # Field-type specific checks
    if field_type == "pincode":
        bad = [p for p in clean if not re.match(r'^\d{6}$', p)]
        if bad:
            warnings_list.append(
                f"**{field_label}:** `{'`, `'.join(bad)}` — "
                "pincodes must be exactly 6 digits with no spaces or letters."
            )

    elif field_type == "state":
        bad = [s for s in clean if not re.match(r'^[A-Z]{2,3}$', s)]
        if bad:
            warnings_list.append(
                f"**{field_label}:** `{'`, `'.join(bad)}` — "
                "state codes should be 2–3 uppercase letters (e.g. MH, GJ, KA, TN)."
            )

    elif field_type == "channel":
        for c in clean:
            if ' ' in c:
                warnings_list.append(
                    f"**{field_label}:** `{c}` contains a space — "
                    "channel codes should not have spaces."
                )
            elif c != c.upper():
                warnings_list.append(
                    f"**{field_label}:** `{c}` has mixed casing — "
                    "channel codes are typically uppercase. "
                    "Enable Case-Insensitive Match if casing varies in Uniware."
                )

    elif field_type == "number":
        bad = [n for n in clean if not re.match(r'^\d+(\.\d+)?$', n)]
        if bad:
            warnings_list.append(
                f"**{field_label}:** `{'`, `'.join(bad)}` — must be a numeric value."
            )

# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    # ── Row 1: Channel Code | Inventory Criteria ────────────────────
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
        fac_inv = st.selectbox("Inventory Criteria",
            ["NONE", "hasShortTermInventory", "hasCompleteShortTermInventory",
             "hasCompleteLongTermInventory", "hasCompleteInventory", "hasFulfillableInventory",
             "hasInventory", "hasLiveInventory", "hasLongTermInventory",
             "hasCompleteMidTermInventory", "hasAllocationWithinMaxOrderCapacity"],
            format_func=lambda x: {
                "NONE":                                "— No Inventory Filter —",
                "hasShortTermInventory":               "Has Short Term Inventory",
                "hasCompleteShortTermInventory":       "Has Complete Short Term Inventory",
                "hasCompleteLongTermInventory":        "Has Complete Long Term Inventory",
                "hasCompleteInventory":                "Has Complete Inventory",
                "hasFulfillableInventory":             "Has Fulfillable Inventory",
                "hasInventory":                        "Has Inventory",
                "hasLiveInventory":                    "Has Live Inventory",
                "hasLongTermInventory":                "Has Long Term Inventory",
                "hasCompleteMidTermInventory":         "Has Complete Mid Term Inventory",
                "hasAllocationWithinMaxOrderCapacity": "Has Allocation Within Max Order Capacity",
            }.get(x, x), key="fac_inv",
            help="• hasShortTermInventory — near-term stock available\n• hasCompleteShortTermInventory — all items have short-term stock\n• hasCompleteLongTermInventory — all items have long-term stock\n• hasCompleteInventory — full stock for all order items\n• hasFulfillableInventory — stock in fulfillable (non-blocked) state\n• hasInventory — any stock exists\n• hasLiveInventory — live available-to-sell stock\n• hasAllocationWithinMaxOrderCapacity — facility under its order cap")

    st.write("")

    # ── Row 2: State Code | Pincode ─────────────────────────────────
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

    # ── Row 3: City | Payment Method ────────────────────────────────
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
            help="PREPAID = online paid orders | COD = cash on delivery\nGenerates: `T(StringUtils).equalsAny(#saleOrder.paymentMethod.code, 'COD')`")
        fac_payment_val = ""
        if fac_use_payment:
            fac_payment_val = st.selectbox("Payment Method", ["PREPAID", "COD"], key="fac_payment_val",
                help="PREPAID = online/prepaid orders | COD = cash-on-delivery orders")

    st.write("")

    # ── Row 4: Country Code | SKU Code ──────────────────────────────
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

    # ── Row 5: Item Tag | Brand ─────────────────────────────────────
    col9, col10 = st.columns(2)

    with col9:
        st.markdown("**Item Tag (hasAnyTag)**")
        fac_use_item_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_item_tag",
            help="Checks if any item in the order has a specific tag in the item master.\nGenerates: `#saleOrder.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`")
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

    # ── Row 6: Custom Field ────────────────────────────────────────────
    col11, col12 = st.columns(2)

    with col11:
        st.markdown("**Custom Field**")
        fac_use_cf = st.checkbox("Apply Custom Field Filter", key="fac_use_cf",
            help=(
                "Custom fields are extra data fields attached to an order from your sales channel "
                "(e.g. Shopify tags, delivery instructions, on-hold flags).\n\n"
                "**Field Name** — the exact key name as configured in Uniware "
                "(e.g. `Tags`, `Omni`, `OnHold`, `note_attributes`)\n\n"
                "**When to use each match type:**\n"
                "• **Contains** — field may have multiple words/tags and you want to find one specific word "
                "(most common — e.g. Tags field contains 'Instant_Shipping')\n"
                "• **Exactly Equals** — field must be one specific value "
                "(e.g. Omni field is exactly 'false')\n"
                "• **Just Exists** — any non-empty value in the field is enough to trigger the rule "
                "(e.g. if OnHold field is present at all)\n\n"
                "Common field names: Tags, Omni, OnHold, note_attributes, S&N_DAY_DELIVERY"
            )
        )
        fac_cf_field = ""
        fac_cf_match = "contains"
        fac_cf_value = ""
        if fac_use_cf:
            fac_cf_field = st.text_input("Custom Field Name (as configured in Uniware)", key="fac_cf_field",
                placeholder="e.g. Tags  or  Omni  or  OnHold  or  note_attributes")
            fac_cf_match = st.selectbox("How should the field be matched?",
                ["contains", "equalsIgnoreCase", "not_null"],
                format_func=lambda x: {
                    "contains":         "🔍 Field contains this value  (e.g. Tags field has the word 'express')",
                    "equalsIgnoreCase": "✅ Field exactly equals this value  (e.g. Omni field is exactly 'false')",
                    "not_null":         "📌 Field just needs to exist  (any non-empty value is enough)"
                }[x], key="fac_cf_match",
                help=(
                    "**🔍 Contains** — Use when the field may have multiple values or a long string and you want "
                    "to check if your value appears anywhere in it. "
                    "Example: Tags field = 'express, prepaid, vip' → checking for 'express' will match.\n\n"
                    "**✅ Exactly Equals** — Use when the field must be one specific value and nothing else. "
                    "Example: Omni field must be exactly 'false' to route to this facility.\n\n"
                    "**📌 Just Exists** — Use when you only care that the field has been filled in, "
                    "regardless of what the value is. Example: if 'OnHold' field is present at all, apply this rule."
                )
            )
            if fac_cf_match != "not_null":
                fac_cf_value = st.text_input("Value to match against", key="fac_cf_value",
                    placeholder="e.g. express  or  On Hold  or  Instant_Shipping  or  false")

    with col12:
        st.write("")

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

    # ==================================================================
    # REVERSE PICKUP SECTION
    # ==================================================================

    if is_reverse:

        st.markdown("##### Reverse Pickup Conditions")

        # ── Row R1: Channel Code | Box Weight ────────────────────────
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
                rev_weight_min = st.text_input("Min Box Weight — exclusive > (blank = no lower bound)",
                    key="rev_weight_min", placeholder="e.g. 0").strip()
                rev_weight_max = st.text_input("Max Box Weight — exclusive < (blank = no upper bound)",
                    key="rev_weight_max", placeholder="e.g. 4999").strip()

        st.write("")

        # ── Row R2: State Code | Pincode ─────────────────────────────
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

        # ── Row R3: City | Payment Method ────────────────────────────
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
                rev_payment_val = st.selectbox("Payment Method", ["COD", "PREPAID"],
                    key="rev_payment_val",
                    help="COD = cash-on-delivery | PREPAID = prepaid/online paid")

        st.write("")

    # ==================================================================
    # FORWARD SHIPPING SECTION
    # ==================================================================

    else:

        # ── Row 1: Channel Code | State Code ─────────────────────────
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

        # ── Row 2: Pincode | Payment Method ──────────────────────────
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

        # ── Row 3: Weight | Price ─────────────────────────────────────
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**Package Weight (grams)**")
            sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight",
                help="Uses `#shippingPackage.actualWeight`.\nMin → exclusive `>` | Max → inclusive `<=`\nExample: Min=500, Max=1000 → `actualWeight > 500 and actualWeight <= 1000`")
            sp_weight_min = ""
            sp_weight_max = ""
            if sp_use_weight:
                sp_weight_min = st.text_input("Min Weight — exclusive > (blank = no lower bound)",
                    key="sp_weight_min", placeholder="e.g. 500").strip()
                sp_weight_max = st.text_input("Max Weight — inclusive <= (blank = no upper bound)",
                    key="sp_weight_max", placeholder="e.g. 1000").strip()

        with col6:
            st.markdown("**Total Order Price**")
            sp_use_price = st.checkbox("Apply Price Filter", key="sp_use_price",
                help="Uses `#shippingPackage.totalPrice`.\nMin → exclusive `>` | Max → inclusive `<=`\nExample: Max=6000 → `totalPrice <= 6000`")
            sp_price_min = ""
            sp_price_max = ""
            if sp_use_price:
                sp_price_min = st.text_input("Min Price — exclusive > (blank = no lower bound)",
                    key="sp_price_min", placeholder="e.g. 0").strip()
                sp_price_max = st.text_input("Max Price — inclusive <= (blank = no upper bound)",
                    key="sp_price_max", placeholder="e.g. 6000").strip()

        st.write("")

        # ── Row 4: City | Country Code ────────────────────────────────
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

        # ── Row 5: Item Count ─────────────────────────────────────────
        col9, col10 = st.columns(2)

        with col9:
            st.markdown("**Number of Items in Package**")
            sp_use_item_count = st.checkbox("Apply Item Count Filter", key="sp_use_item_count",
                help="Uses `#shippingPackage.saleOrderItems.size()` with your chosen operator.\nExample: `<= 12` → package has at most 12 line items.")
            sp_item_count_op = "<="
            sp_item_count_val = ""
            if sp_use_item_count:
                sp_item_count_op = st.selectbox("Operator",
                    ["<=", "<", ">=", ">", "=="],
                    format_func=lambda x: {
                        "<=": "<= (Up to N items — e.g. single or small shipments)",
                        "<":  "<  (Fewer than N items — strictly less)",
                        ">=": ">= (At least N items — e.g. bulk shipments)",
                        ">":  ">  (More than N items — strictly greater)",
                        "==": "== (Exactly N items)"
                    }[x], key="sp_item_count_op",
                    help="• `<=` — up to N items\n• `<` — fewer than N (strictly)\n• `>=` — at least N items\n• `>` — more than N (strictly)\n• `==` — exactly N items")
                sp_item_count_val = st.text_input("Item Count Threshold",
                    key="sp_item_count_val", placeholder="e.g. 12").strip()

        with col10:
            st.write("")

        st.write("")

        # ── Row 6: Item Tag | Custom Field ───────────────────────────────
        col11, col12 = st.columns(2)

        with col11:
            st.markdown("**Item Tag (hasAnyTag)**")
            sp_use_item_tag = st.checkbox("Apply Item Tag Filter", key="sp_use_item_tag",
                help=(
                    "Checks if any item in the package has a specific tag in the item master.\n\n"
                    "Generates: `#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`\n\n"
                    "Used for routing packages containing tagged items (e.g. mattress, furniture, fragile) "
                    "to specific couriers."
                )
            )
            sp_item_tag_val = ""
            if sp_use_item_tag:
                sp_item_tag_val = st.text_input("Item Tag Value", key="sp_item_tag_val",
                    placeholder="e.g. mattress  or  Furniture  or  Accessories")

        with col12:
            st.markdown("**Custom Field**")
            sp_use_cf = st.checkbox("Apply Custom Field Filter", key="sp_use_cf",
                help=(
                    "Custom fields are extra data fields attached to an order from your sales channel "
                    "(e.g. Shopify tags, delivery type, shipping reference).\n\n"
                    "**Field Name** — the exact key name as configured in Uniware.\n"
                    "Common field names: Tags, Delivery_Partner, tagsfetched, "
                    "Shopify_shipping_reference, PartialCOD, express_lmd\n\n"
                    "**When to use each match type:**\n"
                    "• **Contains (recommended)** — field has multiple words/tags and you want to find "
                    "one specific word. Safe even if some orders don't have this field at all. "
                    "Example: Tags field contains 'Express' → assign this courier.\n"
                    "• **Contains (strict)** — same result but written differently. "
                    "Use if your team prefers the explicit style.\n"
                    "• **Exactly Equals** — field must be one precise value. "
                    "Example: Delivery_Partner field is exactly 'DELHIVERY_5KGS'.\n"
                    "• **Just Exists** — any non-empty value in the field triggers the rule. "
                    "Example: if Shopify_shipping_reference field is present at all, use this courier."
                )
            )
            sp_cf_field = ""
            sp_cf_match = "contains_safe"
            sp_cf_value = ""
            if sp_use_cf:
                sp_cf_field = st.text_input("Custom Field Name (as configured in Uniware)", key="sp_cf_field",
                    placeholder="e.g. Tags  or  Delivery_Partner  or  tagsfetched  or  Shopify_shipping_reference")
                sp_cf_match = st.selectbox("How should the field be matched?",
                    ["contains_safe", "contains_strict", "equalsIgnoreCase", "not_null"],
                    format_func=lambda x: {
                        "contains_safe":    "🔍 Field contains this value  (recommended — handles missing fields safely)",
                        "contains_strict":  "🔍 Field contains this value  (strict — field must also explicitly exist)",
                        "equalsIgnoreCase": "✅ Field exactly equals this value  (ignores uppercase/lowercase)",
                        "not_null":         "📌 Field just needs to exist  (any non-empty value is enough)"
                    }[x], key="sp_cf_match",
                    help=(
                        "**🔍 Contains (recommended)** — Use this for Tags, Delivery_Partner, tagsfetched and most "
                        "custom fields. Safely handles cases where the field may not exist on some orders — "
                        "it won't throw an error if the field is missing. "
                        "Example: Tags field contains 'Express' → this courier is selected.\n\n"
                        "**🔍 Contains (strict)** — Same as above but explicitly checks the field is not empty "
                        "before checking the value. Use when you want to be very explicit. "
                        "Slightly longer expression but identical result.\n\n"
                        "**✅ Exactly Equals** — Use when the field must be one precise value. "
                        "Example: Delivery_Partner field is exactly 'DELHIVERY_5KGS'.\n\n"
                        "**📌 Just Exists** — Use when you only care that the field has been filled in "
                        "at all. Example: if 'Shopify_shipping_reference' field is present, apply this courier rule."
                    )
                )
                if sp_cf_match != "not_null":
                    sp_cf_value = st.text_input("Value to match against", key="sp_cf_value",
                        placeholder="e.g. Express  or  DELHIVERY_5KGS  or  EDNDDTAG  or  fastrr, Rush")

        st.write("")


# =====================================================================
# INVENTORY CALCULATION MODULE
# =====================================================================

elif module == "INVENTORY_CALC":

    st.subheader("🛠️ Global Synchronizer Formula Constructor")

    v_inv = st.checkbox(
        "Incorporate Virtual Allocated Stock Threshold Multipliers",
        key="calc_v_inv",
        help="Adds `#inventorySnapshot.virtualInventory` to the base formula.\nEnable when your channel sync should include virtual/buffer stock reservations."
    )
    v_nd = st.checkbox(
        "Incorporate Vendor Catalog Shared Warehouse Stock Pools",
        key="calc_v_nd",
        help="Adds `#inventorySnapshot.vendorInventory` to the base formula.\nEnable for channels that can fulfil from vendor/drop-ship locations."
    )
    unproc = st.checkbox(
        "Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)",
        key="calc_unproc",
        help="DEDUCTS `#unprocessedOrderInventory` from the formula.\nUnprocessed orders consume stock but haven't entered Uniware's pipeline yet.\nCritical for Amazon Flex and slab-based channel integrations."
    )

st.write("")

# =====================================================================
# FINAL COMPILER
# =====================================================================

if st.button("⚙️ Compile Target Token Blueprint", type="primary"):

    final_output = ""
    warnings_list = []

    # =================================================================
    # FACILITY RULE COMPILER
    # =================================================================

    if module == "FACILITY":

        # ── Validate inputs ──────────────────────────────────────────
        if fac_use_channel and fac_channel_val.strip():
            validate_inputs(warnings_list, "Channel Code", fac_channel_val, "channel")
        if fac_use_state and fac_state_val.strip():
            validate_inputs(warnings_list, "State Code", fac_state_val, "state")
        if fac_use_pincode and fac_pincode_val.strip():
            validate_inputs(warnings_list, "Pincode", fac_pincode_val, "pincode")
        if fac_use_city and fac_city_val.strip():
            validate_inputs(warnings_list, "City", fac_city_val, "generic")
        if fac_use_country and fac_country_val.strip():
            validate_inputs(warnings_list, "Country Code", fac_country_val, "generic")
        if fac_use_sku and fac_sku_val.strip():
            validate_inputs(warnings_list, "SKU Code", fac_sku_val, "generic")

        # ── Show warnings ────────────────────────────────────────────
        if warnings_list:
            st.warning("⚠️ **Please review the following before using this rule:**")
            for w in warnings_list:
                st.markdown(f"- {w}")
            st.write("")

        # ── Build rule ───────────────────────────────────────────────
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
            # Direct equality — confirmed pattern from production data
            parts.append(f"#saleOrder.paymentMethod.code == '{fac_payment_val}'")
        if fac_use_country and fac_country_val.strip():
            e = format_multi_value_condition(fac_country_val, "#saleOrderItem.shippingAddress.countryCode")
            if e: parts.append(e)
        if fac_use_sku and fac_sku_val.strip():
            sku_items = csv_items(fac_sku_val)
            if sku_items:
                if len(sku_items) == 1:
                    # Single SKU: saleOrderItems.?[skuCode == 'X'].size() > 0
                    parts.append(
                        f"#saleOrder.saleOrderItems.?[skuCode == '{sku_items[0]}'].size() > 0"
                    )
                else:
                    # Multiple SKUs: saleOrderItems.?[T(StringUtils).equalsAny(itemType.skuCode, 'A','B')].size() > 0
                    quoted = ", ".join(f"'{v}'" for v in sku_items)
                    parts.append(
                        f"#saleOrder.saleOrderItems.?["
                        f"T(com.unifier.core.utils.StringUtils).equalsAny("
                        f"itemType.skuCode, {quoted})].size() > 0"
                    )
        if fac_use_item_tag and fac_item_tag_val.strip():
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.hasAnyTag('{fac_item_tag_val.strip()}')] != null"
            )
        if fac_use_brand and fac_brand_val.strip():
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.brand.contains('{fac_brand_val.strip()}')] != null"
            )
        if fac_use_cf and fac_cf_field.strip():
            cf_fn = fac_cf_field.strip()
            cf_val = fac_cf_value.strip() if fac_cf_value else ""
            cf_getter = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrder, '{cf_fn}')"
            if fac_cf_match == "contains":
                parts.append(f"{cf_getter} != null and {cf_getter}.contains('{cf_val}')")
            elif fac_cf_match == "equalsIgnoreCase":
                parts.append(f"{cf_getter}.equalsIgnoreCase('{cf_val}')")
            elif fac_cf_match == "not_null":
                parts.append(f"{cf_getter} != null")


        if not parts:
            st.error("Validation Error: Please select at least one condition and provide a value.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"

    # =================================================================
    # SHIPPING PROVIDER RULE COMPILER
    # =================================================================

    elif module == "SHIPPING_FWD":

        # ── REVERSE PICKUP PATH ──────────────────────────────────────
        if is_reverse:

            if rev_channel_val.strip():
                validate_inputs(warnings_list, "Return Channel Code", rev_channel_val, "channel")
            if rev_use_state and rev_state_val.strip():
                validate_inputs(warnings_list, "State Code", rev_state_val, "state")
            if rev_use_pincode and rev_pincode_val.strip():
                validate_inputs(warnings_list, "Pincode", rev_pincode_val, "pincode")
            if rev_use_weight:
                if rev_weight_min: validate_inputs(warnings_list, "Min Box Weight", rev_weight_min, "number")
                if rev_weight_max: validate_inputs(warnings_list, "Max Box Weight", rev_weight_max, "number")

            if warnings_list:
                st.warning("⚠️ **Please review the following before using this rule:**")
                for w in warnings_list:
                    st.markdown(f"- {w}")
                st.write("")

            rev_parts = []

            if rev_channel_val.strip():
                e = smart_format_string(rev_channel_val, "#reversePickup.saleOrder.channel.code", use_ignore_case=True)
                if e: rev_parts.append(e)
            if rev_use_weight:
                if rev_weight_min and rev_weight_max:
                    rev_parts.append(
                        f"(#reversePickup.boxWeight > {rev_weight_min} "
                        f"and #reversePickup.boxWeight < {rev_weight_max})"
                    )
                elif rev_weight_min:
                    rev_parts.append(f"#reversePickup.boxWeight > {rev_weight_min}")
                elif rev_weight_max:
                    rev_parts.append(f"#reversePickup.boxWeight < {rev_weight_max}")
            if rev_use_state and rev_state_val.strip():
                e = format_multi_value_condition(rev_state_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode")
                if e: rev_parts.append(e)
            if rev_use_pincode and rev_pincode_val.strip():
                e = format_multi_value_condition(rev_pincode_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode")
                if e: rev_parts.append(e)
            if rev_use_city and rev_city_val.strip():
                e = format_multi_value_condition(rev_city_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.city")
                if e: rev_parts.append(e)
            if rev_use_payment and rev_payment_val:
                rev_parts.append(
                    f"#reversePickup.saleOrder.paymentMethod.code == '{rev_payment_val}'"
                )

            if not rev_parts:
                st.error("Validation Error: Please provide at least one condition for the Reverse Pickup rule.")
            else:
                final_output = "#{\n  " + " and \n  ".join(rev_parts) + "\n}"

        # ── FORWARD SHIPPING PATH ────────────────────────────────────
        else:

            if sp_use_channel and sp_channel_val.strip():
                validate_inputs(warnings_list, "Channel Code", sp_channel_val, "channel")
            if sp_use_state and sp_state_val.strip():
                validate_inputs(warnings_list, "State Code", sp_state_val, "state")
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
                st.warning("⚠️ **Please review the following before using this rule:**")
                for w in warnings_list:
                    st.markdown(f"- {w}")
                st.write("")

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
                parts.append(
                    f"#shippingPackage.saleOrder.paymentMethod.code == '{sp_payment_val}'"
                )
            if sp_use_city and sp_city_val.strip():
                e = format_multi_value_condition(sp_city_val, "#shippingPackage.shippingAddress.city")
                if e: parts.append(e)
            if sp_use_country and sp_country_val.strip():
                e = format_multi_value_condition(sp_country_val, "#shippingPackage.shippingAddress.countryCode")
                if e: parts.append(e)
            if sp_use_item_count and sp_item_count_val:
                parts.append(
                    f"#shippingPackage.saleOrderItems.size() {sp_item_count_op} {sp_item_count_val}"
                )
            if sp_use_item_tag and sp_item_tag_val.strip():
                parts.append(
                    f"#shippingPackage.saleOrderItems.^[itemType.hasAnyTag('{sp_item_tag_val.strip()}')] != null"
                )
            if sp_use_cf and sp_cf_field.strip():
                sp_fn = sp_cf_field.strip()
                sp_val = sp_cf_value.strip() if sp_cf_value else ""
                sp_getter = f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#shippingPackage.saleOrder, '{sp_fn}')"
                if sp_cf_match == "contains_safe":
                    parts.append(f"{sp_getter}?.contains('{sp_val}') ?: false")
                elif sp_cf_match == "contains_strict":
                    parts.append(f"{sp_getter} != null and {sp_getter}.contains('{sp_val}')")
                elif sp_cf_match == "equalsIgnoreCase":
                    parts.append(f"{sp_getter}.equalsIgnoreCase('{sp_val}')")
                elif sp_cf_match == "not_null":
                    parts.append(f"{sp_getter} != null")


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
        if unproc:
            deduct_part += " - #unprocessedOrderInventory"

        core_expr = f"{inv_part} {deduct_part}"

        if sub_type == "DEFAULT":
            final_output = f"#{{{core_expr}}}"
        elif sub_type == "BUFFER_3":
            final_output = f"#{{({core_expr})<=3?0:({core_expr})}}"
        elif sub_type == "BUFFER_1":
            final_output = f"#{{({core_expr})<=1?0:({core_expr})}}"
        elif sub_type == "ZERO_SYNC":
            final_output = f"#{{({core_expr})*0}}"

    # =================================================================
    # OUTPUT
    # =================================================================

    if final_output:
        st.subheader("📋 Compiled System Token String (Copy directly to Uniware)")
        st.code(final_output, language="java")
