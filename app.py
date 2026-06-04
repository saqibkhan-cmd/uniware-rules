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
    """Split comma-separated input into clean list, stripping whitespace."""
    return [x.strip() for x in raw_input.split(",") if x.strip()]


def quoted_csv(raw_input):
    """Split comma-separated input into list of single-quoted strings."""
    return [f"'{x.strip()}'" for x in raw_input.split(",") if x.strip()]


def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """
    Build a SpEL channel-code condition string.

    Single value  → var_name == 'VALUE'
                    or var_name.equalsIgnoreCase('VALUE')
    Multiple      → T(StringUtils).equalsAny(var_name, 'A', 'B', ...)
                    or equalsIgnoreCaseAny(...)

    FIX: original code was missing the single-value branch entirely,
         causing None to be returned for any single channel code input.
    """
    if not raw_input.strip():
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

    # Multiple values
    quoted = quoted_csv(raw_input)
    func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
    return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(quoted)})"


def format_multi_value_condition(raw_input, var_name):
    """
    Build T(StringUtils).equalsAny(var_name, 'A', 'B', ...) for
    state codes, pincodes, cities, country codes.
    Returns "" if input is blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    quoted = ", ".join(f"'{v}'" for v in items)
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {quoted})"


# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    # ── Row 1: Channel Code | Inventory Criteria ────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Channel Code**")
        fac_use_channel = st.checkbox("Apply Channel Code Filter", key="fac_use_channel")
        fac_channel_val = ""
        fac_channel_icase = False
        if fac_use_channel:
            fac_channel_val = st.text_input(
                "Channel Code(s)",
                key="fac_channel_val",
                placeholder="Single: SHOPIFY | Multiple: FLIPKART, AMAZON_IN"
            )
            fac_channel_icase = st.checkbox(
                "Case-Insensitive Match (equalsIgnoreCase)",
                key="fac_channel_icase"
            )

    with col2:
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
            }.get(x, x),
            key="fac_inv"
        )

    st.write("")

    # ── Row 2: State Code | Pincode ─────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**State Code**")
        fac_use_state = st.checkbox("Apply State Code Filter", key="fac_use_state")
        fac_state_val = ""
        if fac_use_state:
            fac_state_val = st.text_input(
                "State Code(s)",
                key="fac_state_val",
                placeholder="Single: MH | Multiple: MH, GJ, KA, TN"
            )

    with col4:
        st.markdown("**Pincode**")
        fac_use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode")
        fac_pincode_val = ""
        if fac_use_pincode:
            fac_pincode_val = st.text_area(
                "Pincode(s)",
                key="fac_pincode_val",
                placeholder="Single: 560001 | Multiple: 560001, 560002, 400001",
                height=100
            )

    st.write("")

    # ── Row 3: City | Payment Method ────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("**City**")
        fac_use_city = st.checkbox("Apply City Filter", key="fac_use_city")
        fac_city_val = ""
        if fac_use_city:
            fac_city_val = st.text_input(
                "City / Cities",
                key="fac_city_val",
                placeholder="Single: Mumbai | Multiple: Mumbai, Delhi, Bangalore"
            )

    with col6:
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

    # ── Row 4: Country Code | SKU Code ──────────────────────────────
    col7, col8 = st.columns(2)

    with col7:
        st.markdown("**Country Code**")
        fac_use_country = st.checkbox("Apply Country Code Filter", key="fac_use_country")
        fac_country_val = ""
        if fac_use_country:
            fac_country_val = st.text_input(
                "Country Code(s)",
                key="fac_country_val",
                placeholder="Single: IN | Multiple: IN, US"
            )

    with col8:
        st.markdown("**SKU Code**")
        fac_use_sku = st.checkbox("Apply SKU Code Filter", key="fac_use_sku")
        fac_sku_val = ""
        if fac_use_sku:
            fac_sku_val = st.text_area(
                "SKU Code(s)",
                key="fac_sku_val",
                placeholder="Single: SKU001 | Multiple: SKU001, SKU002, SKU003",
                height=100
            )

    st.write("")

    # ── Row 5: Item Tag | Brand ─────────────────────────────────────
    col9, col10 = st.columns(2)

    with col9:
        st.markdown("**Item Tag (hasAnyTag)**")
        fac_use_item_tag = st.checkbox("Apply Item Tag Filter", key="fac_use_item_tag")
        fac_item_tag_val = ""
        if fac_use_item_tag:
            fac_item_tag_val = st.text_input(
                "Item Tag Value",
                key="fac_item_tag_val",
                placeholder="e.g. SWAYAM"
            )

    with col10:
        st.markdown("**Brand (contains match)**")
        fac_use_brand = st.checkbox("Apply Brand Filter", key="fac_use_brand")
        fac_brand_val = ""
        if fac_use_brand:
            fac_brand_val = st.text_input(
                "Brand Name",
                key="fac_brand_val",
                placeholder="e.g. Trend Arrest"
            )

    st.write("")

# =====================================================================
# SHIPPING PROVIDER ALLOCATION MODULE
# =====================================================================

elif module == "SHIPPING_FWD":

    st.subheader("🚚 Shipping Provider Allocation Rule Constructor")

    # ── Reverse Pickup Toggle ────────────────────────────────────────
    st.markdown("**Rule Context**")
    is_reverse = st.checkbox(
        "This is a Reverse Pickup / Return Rule  (uses #reversePickup context)",
        key="sp_is_reverse"
    )

    st.write("")

    if is_reverse:
        # ── REVERSE PICKUP SECTION ───────────────────────────────────

        st.markdown("##### Reverse Pickup Conditions")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Return Channel Code**")
            rev_channel_val = st.text_input(
                "Return Channel Code(s)",
                key="rev_channel_val",
                placeholder="Single: SHOPIFY | Multiple: SHOPIFY, CUSTOM"
            )
            rev_channel_icase = st.checkbox(
                "Case-Insensitive Match (equalsIgnoreCase)",
                key="rev_channel_icase"
            )

        with col2:
            st.markdown("**Return Package Weight (grams)**")
            rev_use_weight = st.checkbox("Apply Box Weight Filter", key="rev_use_weight")
            rev_weight_min = ""
            rev_weight_max = ""
            if rev_use_weight:
                rev_weight_min = st.text_input(
                    "Min Weight — exclusive > (blank = no lower bound)",
                    key="rev_weight_min",
                    placeholder="e.g. 0"
                ).strip()
                rev_weight_max = st.text_input(
                    "Max Weight — exclusive < (blank = no upper bound)",
                    key="rev_weight_max",
                    placeholder="e.g. 4999"
                ).strip()

        st.write("")

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**State Code (shipping address)**")
            rev_use_state = st.checkbox("Apply State Code Filter", key="rev_use_state")
            rev_state_val = ""
            if rev_use_state:
                rev_state_val = st.text_input(
                    "State Code(s)",
                    key="rev_state_val",
                    placeholder="Single: MH | Multiple: MH, KA, UP"
                )

        with col4:
            st.markdown("**Actual Weight (shippingPackage)**")
            rev_use_actual_weight = st.checkbox(
                "Apply Actual Weight Filter (shippingPackage.actualWeight)",
                key="rev_use_actual_weight"
            )
            rev_actual_weight_min = ""
            rev_actual_weight_max = ""
            if rev_use_actual_weight:
                rev_actual_weight_min = st.text_input(
                    "Min Actual Weight — exclusive > (blank = no lower bound)",
                    key="rev_actual_weight_min",
                    placeholder="e.g. 500"
                ).strip()
                rev_actual_weight_max = st.text_input(
                    "Max Actual Weight — exclusive < (blank = no upper bound)",
                    key="rev_actual_weight_max",
                    placeholder="e.g. 1500"
                ).strip()

        st.write("")

    else:
        # ── STANDARD FORWARD SHIPPING SECTION ───────────────────────

        # ── Row 1: Channel Code | State Code ────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Channel Code**")
            sp_use_channel = st.checkbox("Apply Channel Code Filter", key="sp_use_channel")
            sp_channel_val = ""
            sp_channel_icase = False
            if sp_use_channel:
                sp_channel_val = st.text_input(
                    "Channel Code(s)",
                    key="sp_channel_val",
                    placeholder="Single: SHOPIFY | Multiple: FLIPKART, AMAZON_IN"
                )
                sp_channel_icase = st.checkbox(
                    "Case-Insensitive Match (equalsIgnoreCase)",
                    key="sp_channel_icase"
                )

        with col2:
            st.markdown("**State Code**")
            sp_use_state = st.checkbox("Apply State Code Filter", key="sp_use_state")
            sp_state_val = ""
            if sp_use_state:
                sp_state_val = st.text_input(
                    "State Code(s)",
                    key="sp_state_val",
                    placeholder="Single: MH | Multiple: MH, GJ, KA"
                )

        st.write("")

        # ── Row 2: Pincode | Payment Method ─────────────────────────
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Pincode**")
            sp_use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode")
            sp_pincode_val = ""
            if sp_use_pincode:
                sp_pincode_val = st.text_area(
                    "Pincode(s)",
                    key="sp_pincode_val",
                    placeholder="Single: 560001 | Multiple: 560001, 560002, 400001",
                    height=100
                )

        with col4:
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

        # ── Row 3: Weight | Price ────────────────────────────────────
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**Package Weight (grams)**")
            sp_use_weight = st.checkbox("Apply Weight Filter", key="sp_use_weight")
            sp_weight_min = ""
            sp_weight_max = ""
            if sp_use_weight:
                sp_weight_min = st.text_input(
                    "Min Weight — exclusive > (blank = no lower bound)",
                    key="sp_weight_min",
                    placeholder="e.g. 500"
                ).strip()
                sp_weight_max = st.text_input(
                    "Max Weight — inclusive <= (blank = no upper bound)",
                    key="sp_weight_max",
                    placeholder="e.g. 1000"
                ).strip()

        with col6:
            st.markdown("**Total Order Price**")
            sp_use_price = st.checkbox("Apply Price Filter", key="sp_use_price")
            sp_price_min = ""
            sp_price_max = ""
            if sp_use_price:
                sp_price_min = st.text_input(
                    "Min Price — exclusive > (blank = no lower bound)",
                    key="sp_price_min",
                    placeholder="e.g. 0"
                ).strip()
                sp_price_max = st.text_input(
                    "Max Price — inclusive <= (blank = no upper bound)",
                    key="sp_price_max",
                    placeholder="e.g. 6000"
                ).strip()

        st.write("")

        # ── Row 4: City | Country Code ───────────────────────────────
        col7, col8 = st.columns(2)

        with col7:
            st.markdown("**City**")
            sp_use_city = st.checkbox("Apply City Filter", key="sp_use_city")
            sp_city_val = ""
            if sp_use_city:
                sp_city_val = st.text_input(
                    "City / Cities",
                    key="sp_city_val",
                    placeholder="Single: Mumbai | Multiple: Mumbai, Delhi"
                )

        with col8:
            st.markdown("**Country Code**")
            sp_use_country = st.checkbox("Apply Country Code Filter", key="sp_use_country")
            sp_country_val = ""
            if sp_use_country:
                sp_country_val = st.text_input(
                    "Country Code(s)",
                    key="sp_country_val",
                    placeholder="Single: IN | Multiple: IN, US"
                )

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
            "These orders consume stock and are therefore DEDUCTED from the available inventory total."
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
        if fac_use_channel and fac_channel_val.strip():
            ch_expr = smart_format_string(
                fac_channel_val,
                "#saleOrder.channel.code",
                use_ignore_case=fac_channel_icase
            )
            if ch_expr:
                parts.append(ch_expr)

        # 2. Inventory criteria
        if fac_inv != "NONE":
            parts.append(f"#allocationCriteria.{fac_inv}()")

        # 3. State code
        if fac_use_state and fac_state_val.strip():
            expr = format_multi_value_condition(
                fac_state_val,
                "#saleOrderItem.shippingAddress.stateCode"
            )
            if expr:
                parts.append(expr)

        # 4. Pincode
        if fac_use_pincode and fac_pincode_val.strip():
            expr = format_multi_value_condition(
                fac_pincode_val,
                "#saleOrderItem.shippingAddress.pincode"
            )
            if expr:
                parts.append(expr)

        # 5. City
        if fac_use_city and fac_city_val.strip():
            expr = format_multi_value_condition(
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
            expr = format_multi_value_condition(
                fac_country_val,
                "#saleOrderItem.shippingAddress.countryCode"
            )
            if expr:
                parts.append(expr)

        # 8. SKU code — all items in order must match
        if fac_use_sku and fac_sku_val.strip():
            sku_items = csv_items(fac_sku_val)
            if sku_items:
                quoted = ", ".join(f"'{v}'" for v in sku_items)
                parts.append(
                    f"(#saleOrder.saleOrderItems.?["
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"itemType.skuCode, {quoted})]).size() == "
                    f"#saleOrder.saleOrderItems.size()"
                )

        # 9. Item tag
        if fac_use_item_tag and fac_item_tag_val.strip():
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.hasAnyTag('{fac_item_tag_val.strip()}')] != null"
            )

        # 10. Brand (contains match)
        if fac_use_brand and fac_brand_val.strip():
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.brand.contains('{fac_brand_val.strip()}')] != null"
            )

        if not parts:
            st.error(
                "Validation Error: Please select conditions and provide values to generate a rule."
            )
        else:
            final_output = (
                "#{\n  "
                + " and \n  ".join(parts)
                + "\n}"
            )

    # =================================================================
    # SHIPPING PROVIDER RULE COMPILER
    # =================================================================

    elif module == "SHIPPING_FWD":

        parts = []

        # ── REVERSE PICKUP PATH ──────────────────────────────────────
        if is_reverse:

            rev_parts = []

            # Channel code (reversePickup context)
            if rev_channel_val.strip():
                ch_expr = smart_format_string(
                    rev_channel_val,
                    "#reversePickup.saleOrder.channel.code",
                    use_ignore_case=rev_channel_icase
                )
                if ch_expr:
                    rev_parts.append(ch_expr)

            # Box weight (reversePickup.boxWeight — uses > min, < max exclusive both ends)
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

            # Actual weight (shippingPackage.actualWeight — exclusive both ends)
            if rev_use_actual_weight:
                if rev_actual_weight_min:
                    rev_parts.append(
                        f"#shippingPackage.actualWeight > {rev_actual_weight_min}"
                    )
                if rev_actual_weight_max:
                    rev_parts.append(
                        f"#shippingPackage.actualWeight < {rev_actual_weight_max}"
                    )

            # State code (shippingPackage shipping address)
            if rev_use_state and rev_state_val.strip():
                expr = format_multi_value_condition(
                    rev_state_val,
                    "#shippingPackage.shippingAddress.stateCode"
                )
                if expr:
                    rev_parts.append(expr)

            if not rev_parts:
                st.error(
                    "Validation Error: Please provide at least a Return Channel Code "
                    "or another condition for the Reverse Pickup rule."
                )
            else:
                final_output = (
                    "#{\n  "
                    + " and \n  ".join(rev_parts)
                    + "\n}"
                )

        # ── STANDARD FORWARD SHIPPING PATH ──────────────────────────
        else:

            # 1. Channel code
            if sp_use_channel and sp_channel_val.strip():
                ch_expr = smart_format_string(
                    sp_channel_val,
                    "#shippingPackage.saleOrder.channel.code",
                    use_ignore_case=sp_channel_icase
                )
                if ch_expr:
                    parts.append(ch_expr)

            # 2. State code
            if sp_use_state and sp_state_val.strip():
                expr = format_multi_value_condition(
                    sp_state_val,
                    "#shippingPackage.shippingAddress.stateCode"
                )
                if expr:
                    parts.append(expr)

            # 3. Pincode
            if sp_use_pincode and sp_pincode_val.strip():
                expr = format_multi_value_condition(
                    sp_pincode_val,
                    "#shippingPackage.shippingAddress.pincode"
                )
                if expr:
                    parts.append(expr)

            # 4. Weight — min exclusive (>), max inclusive (<=)
            if sp_use_weight:
                if sp_weight_min:
                    parts.append(f"#shippingPackage.actualWeight > {sp_weight_min}")
                if sp_weight_max:
                    parts.append(f"#shippingPackage.actualWeight <= {sp_weight_max}")

            # 5. Price — min exclusive (>), max inclusive (<=)
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
                expr = format_multi_value_condition(
                    sp_city_val,
                    "#shippingPackage.shippingAddress.city"
                )
                if expr:
                    parts.append(expr)

            # 8. Country code
            if sp_use_country and sp_country_val.strip():
                expr = format_multi_value_condition(
                    sp_country_val,
                    "#shippingPackage.shippingAddress.countryCode"
                )
                if expr:
                    parts.append(expr)

            if not parts:
                st.error(
                    "Validation Error: Please select conditions and provide values to generate a rule."
                )
            else:
                final_output = (
                    "#{\n  "
                    + " and \n  ".join(parts)
                    + "\n}"
                )

    # =================================================================
    # INVENTORY CALCULATION
    # =================================================================

    elif module == "INVENTORY_CALC":

        inv_part = "#inventorySnapshot.inventory"

        if v_inv:
            inv_part += " + #inventorySnapshot.virtualInventory"

        if v_nd:
            inv_part += " + #inventorySnapshot.vendorInventory"

        # FIX: original code used + #unprocessedOrderInventory which INFLATES stock.
        # Unprocessed orders consume stock and must be DEDUCTED (confirmed from Excel data).
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

        st.subheader(
            "📋 Compiled System Token String (Copy directly to Uniware)"
        )

        st.code(final_output, language="java")
