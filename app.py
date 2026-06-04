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
        "FACILITY": "Facility Allocation Engine (Warehouse Assignment / Routing Rules)",
        "SHIPPING_FWD": "Shipping Provider Allocation Engine (Courier / Logistics Partner Selection)",
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
            "DEFAULT": "Standard Global Marketplace Sync Formula",
            "BUFFER_3": "Safety Buffer Guard (Syncs 0 if Stock <= 3)",
            "BUFFER_1": "Safety Buffer Guard (Syncs 0 if Stock <= 1)",
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
    Single value  -> equality check:  var_name == 'VALUE'
                     or case-insensitive: var_name.equalsIgnoreCase('VALUE')
    Multiple values -> T(StringUtils).equalsAny / equalsIgnoreCaseAny
    Returns "" if blank.
    """
    if not raw_input.strip():
        return ""

    items = csv_items(raw_input)

    if not items:
        return ""

    # FIX: original code missing the single-value branch — added here
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


# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    use_channel = st.checkbox("Apply Channel Code Filter", key="fac_use_channel")
    channel_val = ""
    channel_ignore_case = False
    if use_channel:
        channel_val = st.text_input(
            "Channel Code(s) — comma-separated for multiple",
            key="fac_channel",
            placeholder="e.g. SHOPIFY  or  FLIPKART, AMAZON_IN"
        )
        channel_ignore_case = st.checkbox(
            "Case-Insensitive Match (equalsIgnoreCase)",
            key="fac_channel_icase"
        )

    inv_criteria = st.selectbox(
        "Inventory Allocation Criteria",
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

    use_state = st.checkbox("Apply State Code Filter", key="fac_use_state")
    state_val = ""
    if use_state:
        state_val = st.text_input(
            "State Code(s) — comma-separated",
            key="fac_state",
            placeholder="e.g. MH, GJ, KA"
        )

    use_pincode = st.checkbox("Apply Pincode Filter", key="fac_use_pincode")
    pincode_val = ""
    if use_pincode:
        pincode_val = st.text_area(
            "Pincode(s) — comma-separated",
            key="fac_pincode",
            placeholder="e.g. 560001, 560002, 400001"
        )

    use_city = st.checkbox("Apply City Filter", key="fac_use_city")
    city_val = ""
    if use_city:
        city_val = st.text_input(
            "City / Cities — comma-separated",
            key="fac_city",
            placeholder="e.g. Mumbai, Delhi"
        )

    use_payment = st.checkbox("Apply Payment Method Filter", key="fac_use_payment")
    payment_val = ""
    if use_payment:
        payment_val = st.selectbox(
            "Payment Method",
            ["PREPAID", "COD"],
            key="fac_payment"
        )

    use_country = st.checkbox("Apply Country Code Filter", key="fac_use_country")
    country_val = ""
    if use_country:
        country_val = st.text_input(
            "Country Code(s) — comma-separated",
            key="fac_country",
            placeholder="e.g. IN  or  IN, US"
        )

    use_sku = st.checkbox("Apply SKU Code Filter", key="fac_use_sku")
    sku_val = ""
    if use_sku:
        sku_val = st.text_area(
            "SKU Code(s) — comma-separated",
            key="fac_sku",
            placeholder="e.g. SKU001, SKU002"
        )

    use_item_tag = st.checkbox("Apply Item Tag Filter (hasAnyTag)", key="fac_use_item_tag")
    item_tag_val = ""
    if use_item_tag:
        item_tag_val = st.text_input(
            "Item Tag Value",
            key="fac_item_tag",
            placeholder="e.g. SWAYAM"
        )

    st.write("")

# =====================================================================
# SHIPPING PROVIDER ALLOCATION MODULE
# =====================================================================

elif module == "SHIPPING_FWD":

    st.subheader("🚚 Shipping Provider Allocation Rule Constructor")

    use_channel = st.checkbox("Apply Channel Code Filter", key="sp_use_channel")
    channel_val = ""
    channel_ignore_case = False
    if use_channel:
        channel_val = st.text_input(
            "Channel Code(s) — comma-separated for multiple",
            key="sp_channel",
            placeholder="e.g. SHOPIFY  or  FLIPKART, AMAZON_IN"
        )
        channel_ignore_case = st.checkbox(
            "Case-Insensitive Match (equalsIgnoreCase)",
            key="sp_channel_icase"
        )

    use_state = st.checkbox("Apply State Code Filter", key="sp_use_state")
    state_val = ""
    if use_state:
        state_val = st.text_input(
            "State Code(s) — comma-separated",
            key="sp_state",
            placeholder="e.g. MH, GJ, KA"
        )

    use_pincode = st.checkbox("Apply Pincode Filter", key="sp_use_pincode")
    pincode_val = ""
    if use_pincode:
        pincode_val = st.text_area(
            "Pincode(s) — comma-separated",
            key="sp_pincode",
            placeholder="e.g. 560001, 560002, 400001"
        )

    use_weight = st.checkbox("Apply Package Weight Filter (grams)", key="sp_use_weight")
    weight_min = ""
    weight_max = ""
    if use_weight:
        col1, col2 = st.columns(2)
        with col1:
            weight_min = st.text_input(
                "Min Weight — exclusive > (blank = no lower bound)",
                key="sp_weight_min",
                placeholder="e.g. 500"
            ).strip()
        with col2:
            weight_max = st.text_input(
                "Max Weight — inclusive <= (blank = no upper bound)",
                key="sp_weight_max",
                placeholder="e.g. 1000"
            ).strip()

    use_price = st.checkbox("Apply Total Price Filter", key="sp_use_price")
    price_min = ""
    price_max = ""
    if use_price:
        col1, col2 = st.columns(2)
        with col1:
            price_min = st.text_input(
                "Min Price — exclusive > (blank = no lower bound)",
                key="sp_price_min",
                placeholder="e.g. 0"
            ).strip()
        with col2:
            price_max = st.text_input(
                "Max Price — inclusive <= (blank = no upper bound)",
                key="sp_price_max",
                placeholder="e.g. 6000"
            ).strip()

    use_payment = st.checkbox("Apply Payment Method Filter", key="sp_use_payment")
    payment_val = ""
    if use_payment:
        payment_val = st.selectbox(
            "Payment Method",
            ["COD", "PREPAID"],
            key="sp_payment"
        )

    use_city = st.checkbox("Apply City Filter", key="sp_use_city")
    city_val = ""
    if use_city:
        city_val = st.text_input(
            "City / Cities — comma-separated",
            key="sp_city",
            placeholder="e.g. Mumbai, Delhi"
        )

    use_country = st.checkbox("Apply Country Code Filter", key="sp_use_country")
    country_val = ""
    if use_country:
        country_val = st.text_input(
            "Country Code(s) — comma-separated",
            key="sp_country",
            placeholder="e.g. IN  or  IN, US"
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
        help="""
Includes virtual inventory along with physical inventory during calculation.
"""
    )

    v_nd = st.checkbox(
        "Incorporate Vendor Catalog Shared Warehouse Stock Pools",
        key="calc_v_nd",
        help="""
Includes vendor / drop-ship inventory in stock calculation.
"""
    )

    unproc = st.checkbox(
        "Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)",
        key="calc_unproc",
        help="""
Includes marketplace orders that have not yet entered processing state.

Critical for Amazon Flex calculations.
"""
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

        # Channel code condition
        if use_channel and channel_val.strip():
            ch_expr = smart_format_string(
                channel_val,
                "#saleOrder.channel.code",
                use_ignore_case=channel_ignore_case
            )
            if ch_expr:
                parts.append(ch_expr)

        # Inventory criteria
        if inv_criteria != "NONE":
            parts.append(f"#allocationCriteria.{inv_criteria}()")

        # State code condition
        if use_state and state_val.strip():
            state_items = csv_items(state_val)
            if state_items:
                quoted = ", ".join(f"'{v}'" for v in state_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#saleOrderItem.shippingAddress.stateCode, {quoted})"
                )

        # Pincode condition
        if use_pincode and pincode_val.strip():
            pin_items = csv_items(pincode_val)
            if pin_items:
                quoted = ", ".join(f"'{v}'" for v in pin_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#saleOrderItem.shippingAddress.pincode, {quoted})"
                )

        # City condition
        if use_city and city_val.strip():
            city_items = csv_items(city_val)
            if city_items:
                quoted = ", ".join(f"'{v}'" for v in city_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#saleOrderItem.shippingAddress.city, {quoted})"
                )

        # Payment method condition
        if use_payment and payment_val:
            parts.append(
                f"T(com.unifier.core.utils.StringUtils).equalsAny("
                f"#saleOrder.paymentMethod.code, '{payment_val}')"
            )

        # Country code condition
        if use_country and country_val.strip():
            country_items = csv_items(country_val)
            if country_items:
                quoted = ", ".join(f"'{v}'" for v in country_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#saleOrderItem.shippingAddress.countryCode, {quoted})"
                )

        # SKU code condition
        if use_sku and sku_val.strip():
            sku_items = csv_items(sku_val)
            if sku_items:
                quoted = ", ".join(f"'{v}'" for v in sku_items)
                parts.append(
                    f"(#saleOrder.saleOrderItems.?["
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"itemType.skuCode, {quoted})]).size() == "
                    f"#saleOrder.saleOrderItems.size()"
                )

        # Item tag condition
        if use_item_tag and item_tag_val.strip():
            parts.append(
                f"#saleOrder.saleOrderItems.^["
                f"itemType.hasAnyTag('{item_tag_val.strip()}')] != null"
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

        # Channel code condition
        if use_channel and channel_val.strip():
            ch_expr = smart_format_string(
                channel_val,
                "#shippingPackage.saleOrder.channel.code",
                use_ignore_case=channel_ignore_case
            )
            if ch_expr:
                parts.append(ch_expr)

        # State code condition
        if use_state and state_val.strip():
            state_items = csv_items(state_val)
            if state_items:
                quoted = ", ".join(f"'{v}'" for v in state_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#shippingPackage.shippingAddress.stateCode, {quoted})"
                )

        # Pincode condition
        if use_pincode and pincode_val.strip():
            pin_items = csv_items(pincode_val)
            if pin_items:
                quoted = ", ".join(f"'{v}'" for v in pin_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#shippingPackage.shippingAddress.pincode, {quoted})"
                )

        # Weight conditions — min exclusive (>), max inclusive (<=)
        if use_weight:
            if weight_min:
                parts.append(f"#shippingPackage.actualWeight > {weight_min}")
            if weight_max:
                parts.append(f"#shippingPackage.actualWeight <= {weight_max}")

        # Price conditions — min exclusive (>), max inclusive (<=)
        if use_price:
            if price_min:
                parts.append(f"#shippingPackage.totalPrice > {price_min}")
            if price_max:
                parts.append(f"#shippingPackage.totalPrice <= {price_max}")

        # Payment method condition
        if use_payment and payment_val:
            parts.append(
                f"#shippingPackage.saleOrder.paymentMethod.code == '{payment_val}'"
            )

        # City condition
        if use_city and city_val.strip():
            city_items = csv_items(city_val)
            if city_items:
                quoted = ", ".join(f"'{v}'" for v in city_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#shippingPackage.shippingAddress.city, {quoted})"
                )

        # Country code condition
        if use_country and country_val.strip():
            country_items = csv_items(country_val)
            if country_items:
                quoted = ", ".join(f"'{v}'" for v in country_items)
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny("
                    f"#shippingPackage.shippingAddress.countryCode, {quoted})"
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
    # INVENTORY CALCULATION
    # =================================================================

    elif module == "INVENTORY_CALC":

        inv_part = "#inventorySnapshot.inventory"

        if v_inv:
            inv_part += " + #inventorySnapshot.virtualInventory"

        if v_nd:
            inv_part += " + #inventorySnapshot.vendorInventory"

        deduct_part = (
            "- #inventorySnapshot.openSale "
            "- #pendency "
            "- (#failedOrderInventory?:0) "
            "- #inventoryBlockedOnOtherChannels "
            "- #inventorySnapshot.pendingInventoryAssessment"
        )

        # FIX: unprocessed orders CONSUME stock — must be DEDUCTED (was wrongly + in original)
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
