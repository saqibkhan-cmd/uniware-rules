import streamlit as st

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
    """Split comma-separated input, strip whitespace, drop empty entries."""
    return [x.strip() for x in raw_input.split(",") if x.strip()]


def quoted_csv(raw_input):
    """Split comma-separated input into single-quoted strings."""
    return [f"'{x.strip()}'" for x in raw_input.split(",") if x.strip()]


def smart_format_channel(raw_input, var_name, use_ignore_case=False):
    """
    Build a channel-code condition.

    Single value  -> equality:    var_name == 'VALUE'
                                  or var_name.equalsIgnoreCase('VALUE')
    Multiple      -> equalsAny:   T(...StringUtils).equalsAny(var_name, 'A', 'B')
                                  or equalsIgnoreCaseAny(...)
    Returns "" if blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = [x.strip() for x in raw_input.split(",") if x.strip()]
    if not items:
        return ""
    if len(items) == 1:
        val = items[0]
        if use_ignore_case:
            return f"{var_name}.equalsIgnoreCase('{val}')"
        else:
            return f"{var_name} == '{val}'"
    else:
        quoted = ", ".join(f"'{v}'" for v in items)
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {quoted})"


def format_multi_value(raw_input, var_name):
    """
    Build a T(StringUtils).equalsAny(var_name, 'A', 'B', ...) expression.
    Returns "" if blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = [x.strip() for x in raw_input.split(",") if x.strip()]
    if not items:
        return ""
    quoted = ", ".join(f"'{v}'" for v in items)
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {quoted})"


def assemble_rule(parts):
    """Join a list of condition strings into a #{...} SpEL expression."""
    return "#{\n  " + " and\n  ".join(parts) + "\n}"


# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    # ── Channel Code ────────────────────────────────────────────────
    st.markdown("**Channel Code**")
    fac_channel_mode = st.radio(
        "Channel Code Match Mode",
        ["NONE", "EQUALS", "EQUALS_IGNORE_CASE", "NOT_EQUALS"],
        horizontal=True,
        key="fac_channel_mode",
        format_func=lambda x: {
            "NONE":               "— No Channel Filter —",
            "EQUALS":             "Exact Match  (==)",
            "EQUALS_IGNORE_CASE": "Case-Insensitive Match",
            "NOT_EQUALS":         "Exclude Channel  (!=)"
        }[x]
    )
    fac_channel_val = ""
    if fac_channel_mode != "NONE":
        fac_channel_val = st.text_input(
            "Channel Code(s) — comma-separated for multiple",
            key="fac_channel_val",
            placeholder="e.g. SHOPIFY  or  FLIPKART, AMAZON_IN"
        )

    st.write("")

    # ── Inventory Criteria ───────────────────────────────────────────
    st.markdown("**Inventory Allocation Criteria**")
    fac_inv = st.selectbox(
        "Inventory Criteria",
        [
            "NONE",
            "hasShortTermInventory",
            "hasCompleteShortTermInventory",
            "hasCompleteLongTermInventory",
            "hasCompleteInventory",
            "hasFulfillableInventory",
            "hasInventory",
            "hasLiveInventory",
            "hasLongTermInventory",
            "hasCompleteMidTermInventory",
            "hasAllocationWithinMaxOrderCapacity",
        ],
        format_func=lambda x: {
            "NONE":                              "— No Inventory Filter —",
            "hasShortTermInventory":             "Has Short Term Inventory",
            "hasCompleteShortTermInventory":     "Has Complete Short Term Inventory",
            "hasCompleteLongTermInventory":      "Has Complete Long Term Inventory",
            "hasCompleteInventory":              "Has Complete Inventory",
            "hasFulfillableInventory":           "Has Fulfillable Inventory",
            "hasInventory":                      "Has Inventory",
            "hasLiveInventory":                  "Has Live Inventory",
            "hasLongTermInventory":              "Has Long Term Inventory",
            "hasCompleteMidTermInventory":       "Has Complete Mid Term Inventory",
            "hasAllocationWithinMaxOrderCapacity": "Has Allocation Within Max Order Capacity",
        }.get(x, x),
        key="fac_inv"
    )

    st.write("")

    # ── State Code ───────────────────────────────────────────────────
    st.markdown("**State Code**")
    fac_use_state = st.checkbox("Apply State Code Filter", key="fac_use_state")
    fac_state_val = ""
    if fac_use_state:
        fac_state_val = st.text_input(
            "State Code(s) — comma-separated",
            key="fac_state_val",
            placeholder="e.g. MH, GJ, KA, TN"
        )

    st.write("")

    # ── Pincode ──────────────────────────────────────────────────────
    st.markdown("**Pincode**")
    fac_use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode")
    fac_pincode_val = ""
    fac_pincode_field = "pincode"
    if fac_use_pincode:
        fac_pincode_field = st.radio(
            "Pincode Field Variant",
            ["pincode", "Pincode"],
            horizontal=True,
            key="fac_pincode_field",
            help="Some tenants store pincodes under 'Pincode' (capital P). Match the variant used in your facility rules."
        )
        fac_pincode_val = st.text_area(
            "Pincode(s) — comma-separated",
            key="fac_pincode_val",
            placeholder="e.g. 560001, 560002, 400001"
        )

    st.write("")

    # ── City ─────────────────────────────────────────────────────────
    st.markdown("**City**")
    fac_use_city = st.checkbox("Apply City Filter", key="fac_use_city")
    fac_city_val = ""
    if fac_use_city:
        fac_city_val = st.text_input(
            "City / Cities — comma-separated",
            key="fac_city_val",
            placeholder="e.g. Mumbai, Delhi, Bangalore"
        )

    st.write("")

    # ── Payment Method ───────────────────────────────────────────────
    st.markdown("**Payment Method**")
    fac_use_payment = st.checkbox("Apply Payment Method Filter", key="fac_use_payment")
    fac_payment_val = ""
    if fac_use_payment:
        fac_payment_val = st.selectbox(
            "Payment Method",
            ["PREPAID", "COD"],
            key="fac_payment_val"
        )

    st.write("")

    # ── Country Code ─────────────────────────────────────────────────
    st.markdown("**Country Code**")
    fac_use_country = st.checkbox("Apply Country Code Filter", key="fac_use_country")
    fac_country_mode = "EQUALS"
    fac_country_val = ""
    if fac_use_country:
        fac_country_mode = st.radio(
            "Country Code Mode",
            ["EQUALS", "NOT_EQUALS"],
            horizontal=True,
            key="fac_country_mode"
        )
        fac_country_val = st.text_input(
            "Country Code(s) — comma-separated",
            key="fac_country_val",
            placeholder="e.g. IN  or  IN, US"
        )

    st.write("")

    # ── Item Tag ─────────────────────────────────────────────────────
    st.markdown("**Item Tag (hasAnyTag)**")
    fac_use_item_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_item_tag")
    fac_item_tag_val = ""
    if fac_use_item_tag:
        fac_item_tag_val = st.text_input(
            "Item Tag Value (single tag)",
            key="fac_item_tag_val",
            placeholder="e.g. SWAYAM  or  Infinity_Goodies"
        )

    st.write("")

    # ── SKU Code ─────────────────────────────────────────────────────
    st.markdown("**SKU Code Filter**")
    fac_use_sku = st.checkbox("Apply SKU Code Filter (all items in order must match)", key="fac_use_sku")
    fac_sku_val = ""
    if fac_use_sku:
        fac_sku_val = st.text_area(
            "SKU Code(s) — comma-separated",
            key="fac_sku_val",
            placeholder="e.g. SKU001, SKU002, SKU003"
        )

    st.write("")

    # ── Brand ────────────────────────────────────────────────────────
    st.markdown("**Brand Filter**")
    fac_use_brand = st.checkbox("Apply Brand Filter", key="fac_use_brand")
    fac_brand_val = ""
    if fac_use_brand:
        fac_brand_val = st.text_input(
            "Brand Name (contains match)",
            key="fac_brand_val",
            placeholder="e.g. Trend Arrest"
        )

    st.write("")

# =====================================================================
# SHIPPING PROVIDER ALLOCATION MODULE
# =====================================================================

elif module == "SHIPPING_FWD":

    st.subheader("🚚 Shipping Provider Allocation Rule Constructor")

    # ── Channel Code ────────────────────────────────────────────────
    st.markdown("**Channel Code**")
    sp_channel_mode = st.radio(
        "Channel Code Match Mode",
        ["NONE", "EQUALS", "EQUALS_IGNORE_CASE"],
        horizontal=True,
        key="sp_channel_mode",
        format_func=lambda x: {
            "NONE":               "— No Channel Filter —",
            "EQUALS":             "Exact Match  (==)",
            "EQUALS_IGNORE_CASE": "Case-Insensitive  (equalsIgnoreCase)"
        }[x]
    )
    sp_channel_val = ""
    if sp_channel_mode != "NONE":
        sp_channel_val = st.text_input(
            "Channel Code(s) — comma-separated for multiple",
            key="sp_channel_val",
            placeholder="e.g. SHOPIFY  or  FLIPKART, AMAZON_IN"
        )

    st.write("")

    # ── State Code ───────────────────────────────────────────────────
    st.markdown("**State Code**")
    sp_use_state = st.checkbox("Apply State Code Filter", key="sp_use_state")
    sp_state_val = ""
    if sp_use_state:
        sp_state_val = st.text_input(
            "State Code(s) — comma-separated",
            key="sp_state_val",
            placeholder="e.g. MH, GJ, KA, TN"
        )

    st.write("")

    # ── Pincode ──────────────────────────────────────────────────────
    st.markdown("**Pincode**")
    sp_use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode")
    sp_pincode_val = ""
    if sp_use_pincode:
        sp_pincode_val = st.text_area(
            "Pincode(s) — comma-separated",
            key="sp_pincode_val",
            placeholder="e.g. 560001, 560002, 400001"
        )

    st.write("")

    # ── Weight ───────────────────────────────────────────────────────
    st.markdown("**Package Weight (grams)**")
    sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight")
    sp_weight_min = ""
    sp_weight_max = ""
    if sp_use_weight:
        col1, col2 = st.columns(2)
        with col1:
            sp_weight_min = st.text_input(
                "Min Weight — exclusive (leave blank = no lower bound)",
                key="sp_weight_min",
                placeholder="e.g. 500"
            ).strip()
        with col2:
            sp_weight_max = st.text_input(
                "Max Weight — inclusive (leave blank = no upper bound)",
                key="sp_weight_max",
                placeholder="e.g. 1000"
            ).strip()

    st.write("")

    # ── Total Price ──────────────────────────────────────────────────
    st.markdown("**Order Total Price**")
    sp_use_price = st.checkbox("Apply Total Price Filter", key="sp_use_price")
    sp_price_min = ""
    sp_price_max = ""
    if sp_use_price:
        col1, col2 = st.columns(2)
        with col1:
            sp_price_min = st.text_input(
                "Min Price — exclusive (leave blank = no lower bound)",
                key="sp_price_min",
                placeholder="e.g. 0"
            ).strip()
        with col2:
            sp_price_max = st.text_input(
                "Max Price — inclusive (leave blank = no upper bound)",
                key="sp_price_max",
                placeholder="e.g. 6000"
            ).strip()

    st.write("")

    # ── Payment Method ───────────────────────────────────────────────
    st.markdown("**Payment Method**")
    sp_use_payment = st.checkbox("Apply Payment Method Filter", key="sp_use_payment")
    sp_payment_val = ""
    if sp_use_payment:
        sp_payment_val = st.selectbox(
            "Payment Method",
            ["COD", "PREPAID"],
            key="sp_payment_val"
        )

    st.write("")

    # ── City ─────────────────────────────────────────────────────────
    st.markdown("**City**")
    sp_use_city = st.checkbox("Apply City Filter", key="sp_use_city")
    sp_city_val = ""
    if sp_use_city:
        sp_city_val = st.text_input(
            "City / Cities — comma-separated",
            key="sp_city_val",
            placeholder="e.g. Mumbai, Delhi"
        )

    st.write("")

    # ── Country Code ─────────────────────────────────────────────────
    st.markdown("**Country Code**")
    sp_use_country = st.checkbox("Apply Country Code Filter", key="sp_use_country")
    sp_country_val = ""
    if sp_use_country:
        sp_country_val = st.text_input(
            "Country Code(s) — comma-separated",
            key="sp_country_val",
            placeholder="e.g. IN  or  IN, US"
        )

    st.write("")

    # ── Facility Code ────────────────────────────────────────────────
    st.markdown("**Facility Code**")
    sp_use_facility = st.checkbox("Apply Facility Code Filter", key="sp_use_facility")
    sp_facility_val = ""
    if sp_use_facility:
        sp_facility_val = st.text_input(
            "Facility Code (exact match)",
            key="sp_facility_val",
            placeholder="e.g. emporioselect"
        ).strip()

    st.write("")

    # ── SKU Code ─────────────────────────────────────────────────────
    st.markdown("**SKU Code Filter**")
    sp_use_sku = st.checkbox("Apply SKU Code Filter", key="sp_use_sku")
    sp_sku_val = ""
    if sp_use_sku:
        sp_sku_val = st.text_area(
            "SKU Code(s) — comma-separated",
            key="sp_sku_val",
            placeholder="e.g. BBSL1001A-00, BBSL1001H-00"
        )

    st.write("")

    # ── Item Count ───────────────────────────────────────────────────
    st.markdown("**Number of Items in Package**")
    sp_use_items = st.checkbox("Apply Item Count Filter", key="sp_use_items")
    sp_items_mode = ">="
    sp_items_val = ""
    if sp_use_items:
        sp_items_mode = st.radio(
            "Comparison",
            [">=", ">", "<=", "<", "=="],
            horizontal=True,
            key="sp_items_mode"
        )
        sp_items_val = st.text_input(
            "Item Count Threshold",
            key="sp_items_val",
            placeholder="e.g. 10"
        ).strip()

    st.write("")

    # ── Reverse Pickup / Return ──────────────────────────────────────
    st.markdown("**Reverse Pickup / Return Channel**")
    sp_use_reverse = st.checkbox(
        "This rule is for Reverse Pickup (uses #reversePickup context)",
        key="sp_use_reverse"
    )
    sp_reverse_channel_val = ""
    if sp_use_reverse:
        sp_reverse_channel_val = st.text_input(
            "Return Channel Code (equalsIgnoreCase match)",
            key="sp_reverse_channel_val",
            placeholder="e.g. SHOPIFY_AURELIA"
        ).strip()

    st.write("")

# =====================================================================
# INVENTORY CALCULATION MODULE
# =====================================================================

elif module == "INVENTORY_CALC":

    st.subheader("🛠️ Global Synchronizer Formula Constructor")

    v_inv = st.checkbox(
        "Incorporate Virtual Allocated Stock Threshold Multipliers",
        key="calc_v_inv",
        help="Includes virtual inventory along with physical inventory during calculation."
    )

    v_nd = st.checkbox(
        "Incorporate Vendor Catalog Shared Warehouse Stock Pools",
        key="calc_v_nd",
        help="Includes vendor / drop-ship inventory in stock calculation."
    )

    unproc = st.checkbox(
        "Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)",
        key="calc_unproc",
        help=(
            "Includes marketplace orders that have not yet entered processing state. "
            "Critical for Amazon Flex calculations. "
            "These orders consume stock and are therefore DEDUCTED from available inventory."
        )
    )

st.write("")

# =====================================================================
# FINAL COMPILER
# =====================================================================

if st.button("Compile Target Token Blueprint", type="primary"):

    final_output = ""

    # =================================================================
    # FACILITY RULE COMPILER
    # =================================================================

    if module == "FACILITY":

        parts = []

        # 1. Channel code
        if fac_channel_mode != "NONE" and fac_channel_val.strip():
            items = [x.strip() for x in fac_channel_val.split(",") if x.strip()]
            if fac_channel_mode == "NOT_EQUALS":
                # Each excluded channel becomes a separate != clause
                for ch in items:
                    parts.append(f"#saleOrder.channel.code != '{ch}'")
            else:
                ch_expr = smart_format_channel(
                    fac_channel_val,
                    "#saleOrder.channel.code",
                    use_ignore_case=(fac_channel_mode == "EQUALS_IGNORE_CASE")
                )
                if ch_expr:
                    parts.append(ch_expr)

        # 2. Inventory criteria
        if fac_inv != "NONE":
            parts.append(f"#allocationCriteria.{fac_inv}()")

        # 3. State code
        if fac_use_state and fac_state_val.strip():
            expr = format_multi_value(
                fac_state_val,
                "#saleOrderItem.shippingAddress.stateCode"
            )
            if expr:
                parts.append(expr)

        # 4. Pincode  (capital-P variant used by some tenants)
        if fac_use_pincode and fac_pincode_val.strip():
            field = f"#saleOrderItem.shippingAddress.{fac_pincode_field}"
            expr = format_multi_value(fac_pincode_val, field)
            if expr:
                parts.append(expr)

        # 5. City
        if fac_use_city and fac_city_val.strip():
            expr = format_multi_value(
                fac_city_val,
                "#saleOrderItem.shippingAddress.city"
            )
            if expr:
                parts.append(expr)

        # 6. Payment method
        if fac_use_payment and fac_payment_val:
            parts.append(
                f"T(com.unifier.core.utils.StringUtils).equalsAny("
                f"#saleOrder.paymentMethod.code, '{fac_payment_val}')"
            )

        # 7. Country code
        if fac_use_country and fac_country_val.strip():
            items = [x.strip() for x in fac_country_val.split(",") if x.strip()]
            if items:
                if fac_country_mode == "NOT_EQUALS":
                    for c in items:
                        parts.append(f"#saleOrderItem.shippingAddress.countryCode != '{c}'")
                else:
                    quoted = ", ".join(f"'{v}'" for v in items)
                    parts.append(
                        f"T(com.unifier.core.utils.StringUtils).equalsAny("
                        f"#saleOrderItem.shippingAddress.countryCode, {quoted})"
                    )

        # 8. Item tag
        if fac_use_item_tag and fac_item_tag_val.strip():
            tag = fac_item_tag_val.strip()
            parts.append(
                f"#saleOrder.saleOrderItems.^[itemType.hasAnyTag('{tag}')] != null"
            )

        # 9. SKU code (all order items must match)
        if fac_use_sku and fac_sku_val.strip():
            sku_items = [x.strip() for x in fac_sku_val.split(",") if x.strip()]
            if sku_items:
                quoted = ", ".join(f"'{v}'" for v in sku_items)
                parts.append(
                    f"(#saleOrder.saleOrderItems.?["
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"itemType.skuCode, {quoted})]).size() == "
                    f"#saleOrder.saleOrderItems.size()"
                )

        # 10. Brand (contains match)
        if fac_use_brand and fac_brand_val.strip():
            brand = fac_brand_val.strip()
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.brand.contains('{brand}')] != null"
            )

        # ── Validate & emit ──────────────────────────────────────────
        if not parts:
            st.error(
                "Validation Error: Please select at least one condition "
                "and provide a value to generate a rule."
            )
        else:
            final_output = assemble_rule(parts)

    # =================================================================
    # SHIPPING PROVIDER RULE COMPILER
    # =================================================================

    elif module == "SHIPPING_FWD":

        parts = []

        # ── Reverse-pickup path (different root variable) ────────────
        if sp_use_reverse:
            if sp_reverse_channel_val:
                final_output = (
                    f"#{{#reversePickup.saleOrder.channel.code."
                    f"equalsIgnoreCase('{sp_reverse_channel_val}')}}"
                )
            else:
                st.error(
                    "Validation Error: Please enter a Return Channel Code "
                    "for Reverse Pickup rules."
                )
        else:
            # ── Standard shipping-package path ───────────────────────

            # 1. Channel code
            if sp_channel_mode != "NONE" and sp_channel_val.strip():
                ch_expr = smart_format_channel(
                    sp_channel_val,
                    "#shippingPackage.saleOrder.channel.code",
                    use_ignore_case=(sp_channel_mode == "EQUALS_IGNORE_CASE")
                )
                if ch_expr:
                    parts.append(ch_expr)

            # 2. State code
            if sp_use_state and sp_state_val.strip():
                expr = format_multi_value(
                    sp_state_val,
                    "#shippingPackage.shippingAddress.stateCode"
                )
                if expr:
                    parts.append(expr)

            # 3. Pincode
            if sp_use_pincode and sp_pincode_val.strip():
                expr = format_multi_value(
                    sp_pincode_val,
                    "#shippingPackage.shippingAddress.pincode"
                )
                if expr:
                    parts.append(expr)

            # 4. Weight  (min is exclusive >, max is inclusive <=)
            if sp_use_weight:
                if sp_weight_min:
                    parts.append(f"#shippingPackage.actualWeight > {sp_weight_min}")
                if sp_weight_max:
                    parts.append(f"#shippingPackage.actualWeight <= {sp_weight_max}")

            # 5. Total price  (min is exclusive >, max is inclusive <=)
            if sp_use_price:
                if sp_price_min:
                    parts.append(f"#shippingPackage.totalPrice > {sp_price_min}")
                if sp_price_max:
                    parts.append(f"#shippingPackage.totalPrice <= {sp_price_max}")

            # 6. Payment method
            if sp_use_payment and sp_payment_val:
                parts.append(
                    f"#shippingPackage.saleOrder.paymentMethod.code == '{sp_payment_val}'"
                )

            # 7. City
            if sp_use_city and sp_city_val.strip():
                expr = format_multi_value(
                    sp_city_val,
                    "#shippingPackage.shippingAddress.city"
                )
                if expr:
                    parts.append(expr)

            # 8. Country code
            if sp_use_country and sp_country_val.strip():
                expr = format_multi_value(
                    sp_country_val,
                    "#shippingPackage.shippingAddress.countryCode"
                )
                if expr:
                    parts.append(expr)

            # 9. Facility code
            if sp_use_facility and sp_facility_val:
                parts.append(
                    f"#shippingPackage.saleOrder.facility.code == '{sp_facility_val}'"
                )

            # 10. SKU code (at least one item in package must match)
            if sp_use_sku and sp_sku_val.strip():
                sku_items = [x.strip() for x in sp_sku_val.split(",") if x.strip()]
                if sku_items:
                    quoted = ", ".join(f"'{v}'" for v in sku_items)
                    parts.append(
                        f"#shippingPackage.saleOrderItems.^["
                        f"T(com.unifier.core.utils.StringUtils).equalsAny("
                        f"itemType.skuCode, {quoted})] != null"
                    )

            # 11. Item count
            if sp_use_items and sp_items_val:
                parts.append(
                    f"#shippingPackage.noOfItems {sp_items_mode} {sp_items_val}"
                )

            # ── Validate & emit ──────────────────────────────────────
            if not parts:
                st.error(
                    "Validation Error: Please select at least one condition "
                    "and provide a value to generate a rule."
                )
            else:
                final_output = assemble_rule(parts)

    # =================================================================
    # INVENTORY CALCULATION COMPILER
    # =================================================================

    elif module == "INVENTORY_CALC":

        inv_part = "#inventorySnapshot.inventory"

        if v_inv:
            inv_part += " + #inventorySnapshot.virtualInventory"

        if v_nd:
            inv_part += " + #inventorySnapshot.vendorInventory"

        # Deductions: unprocessed orders are DEDUCTED (they consume stock)
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
