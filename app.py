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
    """Split comma-separated input into a clean list, stripping whitespace."""
    return [x.strip() for x in raw_input.split(",") if x.strip()]


def quoted_csv(raw_input):
    """Split comma-separated input into a list of single-quoted strings."""
    return [f"'{x.strip()}'" for x in raw_input.split(",") if x.strip()]


def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """
    Automatically switches between equality and equalsAny based on input count.

    Single value  → var_name == 'VALUE'
                    or var_name.equalsIgnoreCase('VALUE')

    Multiple CSV  → T(com.unifier.core.utils.StringUtils).equalsAny(var_name, 'A', 'B', ...)
                    or equalsIgnoreCaseAny(...)

    Returns "" if input is blank.
    """
    if not raw_input or not raw_input.strip():
        return ""
    items = csv_items(raw_input)
    if not items:
        return ""
    if len(items) == 1:
        val = items[0]
        if use_ignore_case:
            # Single value + case-insensitive: method call on the field itself
            return f"{var_name}.equalsIgnoreCase('{val}')"
        else:
            # Single value + exact: simple equality
            return f"{var_name} == '{val}'"
    else:
        # Multiple values: use StringUtils equalsAny / equalsIgnoreCaseAny
        quoted = ", ".join(f"'{v}'" for v in items)
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {quoted})"


def format_multi_value_condition(raw_input, var_name):
    """
    Builds the correct SpEL condition for state codes, pincodes, cities,
    country codes, payment method, and SKU codes.

    Single value  → var_name == 'VALUE'
    Multiple CSV  → T(com.unifier.core.utils.StringUtils).equalsAny(var_name, 'A', 'B', ...)

    Returns "" if input is blank.
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
# FACILITY ALLOCATION MODULE
# =====================================================================

if module == "FACILITY":

    st.subheader("🏭 Facility Allocation Rule Constructor")

    # ── Row 1: Channel Code | Inventory Criteria ────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Channel Code**")
        fac_use_channel = st.checkbox(
            "Apply Channel Code Filter",
            key="fac_use_channel",
            help=(
                "Filter allocation rules by sales channel code.\n\n"
                "**Single value** → generates exact equality: `#saleOrder.channel.code == 'SHOPIFY'`\n\n"
                "**Multiple values (comma-separated)** → generates equalsAny: "
                "`T(StringUtils).equalsAny(#saleOrder.channel.code, 'FLIPKART', 'AMAZON_IN')`\n\n"
                "Enable case-insensitive toggle below if channel codes may have mixed casing."
            )
        )
        fac_channel_val = ""
        fac_channel_icase = False
        if fac_use_channel:
            fac_channel_val = st.text_input(
                "Channel Code(s)",
                key="fac_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN"
            )
            fac_channel_icase = st.checkbox(
                "Case-Insensitive Match (equalsIgnoreCase)",
                key="fac_channel_icase",
                help=(
                    "Uses `.equalsIgnoreCase()` for single values or `equalsIgnoreCaseAny()` "
                    "for multiple values. Use when channel codes in Uniware may have inconsistent casing."
                )
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
            key="fac_inv",
            help=(
                "Checks whether the facility holds sufficient inventory of the required type "
                "before allocating the order item to it.\n\n"
                "• **hasShortTermInventory** — stock available for near-term fulfilment\n"
                "• **hasCompleteShortTermInventory** — all items in the order have short-term stock\n"
                "• **hasCompleteLongTermInventory** — all items have long-term stock\n"
                "• **hasCompleteInventory** — complete stock for all order items\n"
                "• **hasFulfillableInventory** — stock is in a fulfillable (non-blocked) state\n"
                "• **hasInventory** — any inventory exists for the item\n"
                "• **hasLiveInventory** — inventory is live and available to sell\n"
                "• **hasAllocationWithinMaxOrderCapacity** — facility has not exceeded its order cap"
            )
        )

    st.write("")

    # ── Row 2: State Code | Pincode ─────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**State Code**")
        fac_use_state = st.checkbox(
            "Apply State Code Filter",
            key="fac_use_state",
            help=(
                "Restricts allocation to orders shipping to specific Indian state codes.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrderItem.shippingAddress.stateCode, ...)`.\n\n"
                "**Single:** MH  |  **Multiple:** MH, GJ, KA, TN"
            )
        )
        fac_state_val = ""
        if fac_use_state:
            fac_state_val = st.text_input(
                "State Code(s)",
                key="fac_state_val",
                placeholder="Single: MH  |  Multiple: MH, GJ, KA, TN"
            )

    with col4:
        st.markdown("**Pincode**")
        fac_use_pincode = st.checkbox(
            "Apply Pincode Filter",
            key="fac_use_pincode",
            help=(
                "Restricts allocation to orders shipping to specific pincodes.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrderItem.shippingAddress.pincode, ...)`.\n\n"
                "**Single:** 560001  |  **Multiple:** 560001, 560002, 400001\n\n"
                "Enter pincodes as strings (quoted in the output automatically)."
            )
        )
        fac_pincode_val = ""
        if fac_use_pincode:
            fac_pincode_val = st.text_area(
                "Pincode(s)",
                key="fac_pincode_val",
                placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001",
                height=100
            )

    st.write("")

    # ── Row 3: City | Payment Method ────────────────────────────────
    col5, col6 = st.columns(2)

    with col5:
        st.markdown("**City**")
        fac_use_city = st.checkbox(
            "Apply City Filter",
            key="fac_use_city",
            help=(
                "Restricts allocation to orders shipping to specific cities.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrderItem.shippingAddress.city, ...)`.\n\n"
                "**Single:** Mumbai  |  **Multiple:** Mumbai, Delhi, Bangalore"
            )
        )
        fac_city_val = ""
        if fac_use_city:
            fac_city_val = st.text_input(
                "City / Cities",
                key="fac_city_val",
                placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi, Bangalore"
            )

    with col6:
        st.markdown("**Payment Method**")
        fac_use_payment = st.checkbox(
            "Apply Payment Method Filter",
            key="fac_use_payment",
            help=(
                "Restricts allocation based on the order's payment method.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrder.paymentMethod.code, 'COD')` or `'PREPAID'`.\n\n"
                "Useful for routing COD orders to specific facilities."
            )
        )
        fac_payment_val = ""
        if fac_use_payment:
            fac_payment_val = st.selectbox(
                "Payment Method",
                ["PREPAID", "COD"],
                key="fac_payment_val",
                help="PREPAID = online paid orders. COD = cash-on-delivery orders."
            )

    st.write("")

    # ── Row 4: Country Code | SKU Code ──────────────────────────────
    col7, col8 = st.columns(2)

    with col7:
        st.markdown("**Country Code**")
        fac_use_country = st.checkbox(
            "Apply Country Code Filter",
            key="fac_use_country",
            help=(
                "Restricts allocation based on the destination country.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrderItem.shippingAddress.countryCode, ...)`.\n\n"
                "**Single:** IN  |  **Multiple:** IN, US, AE\n\n"
                "Commonly used to separate domestic and international order routing."
            )
        )
        fac_country_val = ""
        if fac_use_country:
            fac_country_val = st.text_input(
                "Country Code(s)",
                key="fac_country_val",
                placeholder="Single: IN  |  Multiple: IN, US, AE"
            )

    with col8:
        st.markdown("**SKU Code**")
        fac_use_sku = st.checkbox(
            "Apply SKU Code Filter",
            key="fac_use_sku",
            help=(
                "Restricts allocation to orders whose items match specific SKU codes.\n\n"
                "Uses `T(StringUtils).equalsAny(#saleOrderItem.skuCode, ...)` — "
                "checks each individual order item's SKU against the list.\n\n"
                "**Single:** SKU001  |  **Multiple:** SKU001, SKU002, SKU003\n\n"
                "Note: Does NOT add a `.size()` check — matches any item in the order with that SKU."
            )
        )
        fac_sku_val = ""
        if fac_use_sku:
            fac_sku_val = st.text_area(
                "SKU Code(s)",
                key="fac_sku_val",
                placeholder="Single: SKU001  |  Multiple: SKU001, SKU002, SKU003",
                height=100
            )

    st.write("")

    # ── Row 5: Item Tag | Brand ─────────────────────────────────────
    col9, col10 = st.columns(2)

    with col9:
        st.markdown("**Item Tag (hasAnyTag)**")
        fac_use_item_tag = st.checkbox(
            "Apply Item Tag Filter",
            key="fac_use_item_tag",
            help=(
                "Checks if any item in the order has a specific tag assigned in the item master.\n\n"
                "Uses `#saleOrder.saleOrderItems.^[itemType.hasAnyTag('TAG')] != null`.\n\n"
                "Enter a single tag value. Used to route orders containing tagged products "
                "(e.g. hazardous, fragile, brand-specific) to designated facilities."
            )
        )
        fac_item_tag_val = ""
        if fac_use_item_tag:
            fac_item_tag_val = st.text_input(
                "Item Tag Value",
                key="fac_item_tag_val",
                placeholder="e.g. SWAYAM  or  Infinity_Goodies"
            )

    with col10:
        st.markdown("**Brand (contains match)**")
        fac_use_brand = st.checkbox(
            "Apply Brand Filter",
            key="fac_use_brand",
            help=(
                "Checks if any item in the order belongs to a specific brand (partial/contains match).\n\n"
                "Uses `#saleOrder.saleOrderItems.^[itemType.brand.contains('BRAND')] != null`.\n\n"
                "Enter a single brand name. Useful for brand-segregated warehouse routing."
            )
        )
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
        key="sp_is_reverse",
        help=(
            "Toggle this ON for return/reverse-pickup shipping provider rules.\n\n"
            "When enabled, the rule uses the `#reversePickup` SpEL variable instead of "
            "`#shippingPackage`, and weight is evaluated against `#reversePickup.boxWeight`.\n\n"
            "Leave OFF for all standard forward-shipment courier selection rules."
        )
    )

    st.write("")

    # ==================================================================
    # REVERSE PICKUP SECTION
    # ==================================================================

    if is_reverse:

        st.markdown("##### Reverse Pickup Conditions")

        # ── Row R1: Channel Code | Box Weight ───────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Return Channel Code**")
            rev_channel_val = st.text_input(
                "Return Channel Code(s)",
                key="rev_channel_val",
                placeholder="Single: SHOPIFY  |  Multiple: SHOPIFY, CUSTOM",
                help=(
                    "The sales channel code on the original order being returned.\n\n"
                    "**Single value** → `#reversePickup.saleOrder.channel.code.equalsIgnoreCase('SHOPIFY')`\n\n"
                    "**Multiple values** → `T(StringUtils).equalsAny(#reversePickup.saleOrder.channel.code, 'A', 'B')`\n\n"
                    "Case-insensitive match is used by default for reverse pickup channel codes "
                    "as confirmed in production data."
                )
            )

        with col2:
            st.markdown("**Box Weight (grams)**")
            rev_use_weight = st.checkbox(
                "Apply Box Weight Filter",
                key="rev_use_weight",
                help=(
                    "Filters by the physical box weight of the return package.\n\n"
                    "Uses `#reversePickup.boxWeight` with exclusive bounds on both ends:\n"
                    "Min → `> value`  |  Max → `< value`\n\n"
                    "Example: Min=0, Max=4999 generates "
                    "`(#reversePickup.boxWeight > 0 and #reversePickup.boxWeight < 4999)`"
                )
            )
            rev_weight_min = ""
            rev_weight_max = ""
            if rev_use_weight:
                rev_weight_min = st.text_input(
                    "Min Box Weight — exclusive > (blank = no lower bound)",
                    key="rev_weight_min",
                    placeholder="e.g. 0"
                ).strip()
                rev_weight_max = st.text_input(
                    "Max Box Weight — exclusive < (blank = no upper bound)",
                    key="rev_weight_max",
                    placeholder="e.g. 4999"
                ).strip()

        st.write("")

        # ── Row R2: State Code | Pincode ─────────────────────────────
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**State Code**")
            rev_use_state = st.checkbox(
                "Apply State Code Filter",
                key="rev_use_state",
                help=(
                    "Restricts the reverse pickup rule to specific state codes.\n\n"
                    "Uses `T(StringUtils).equalsAny(#reversePickup.saleOrder.shippingPackage."
                    "shippingAddress.stateCode, ...)` — the state on the original shipment.\n\n"
                    "**Single:** MH  |  **Multiple:** MH, KA, UP, WB"
                )
            )
            rev_state_val = ""
            if rev_use_state:
                rev_state_val = st.text_input(
                    "State Code(s)",
                    key="rev_state_val",
                    placeholder="Single: MH  |  Multiple: MH, KA, UP, WB"
                )

        with col4:
            st.markdown("**Pincode**")
            rev_use_pincode = st.checkbox(
                "Apply Pincode Filter",
                key="rev_use_pincode",
                help=(
                    "Restricts the reverse pickup rule to specific pickup pincodes.\n\n"
                    "Uses `T(StringUtils).equalsAny(#reversePickup.saleOrder.shippingPackage."
                    "shippingAddress.pincode, ...)`.\n\n"
                    "**Single:** 560001  |  **Multiple:** 560001, 560002, 400001"
                )
            )
            rev_pincode_val = ""
            if rev_use_pincode:
                rev_pincode_val = st.text_area(
                    "Pincode(s)",
                    key="rev_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001",
                    height=100
                )

        st.write("")

        # ── Row R3: City | Country Code ──────────────────────────────
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**City**")
            rev_use_city = st.checkbox(
                "Apply City Filter",
                key="rev_use_city",
                help=(
                    "Restricts the reverse pickup rule to specific pickup cities.\n\n"
                    "Uses `T(StringUtils).equalsAny(#reversePickup.saleOrder.shippingPackage."
                    "shippingAddress.city, ...)`.\n\n"
                    "**Single:** Mumbai  |  **Multiple:** Mumbai, Delhi"
                )
            )
            rev_city_val = ""
            if rev_use_city:
                rev_city_val = st.text_input(
                    "City / Cities",
                    key="rev_city_val",
                    placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi"
                )

        with col6:
            st.markdown("**Payment Method**")
            rev_use_payment = st.checkbox(
                "Apply Payment Method Filter",
                key="rev_use_payment",
                help=(
                    "Filters reverse pickup rules by the original order's payment method.\n\n"
                    "Uses `#reversePickup.saleOrder.paymentMethod.code == 'COD'` or `'PREPAID'`."
                )
            )
            rev_payment_val = ""
            if rev_use_payment:
                rev_payment_val = st.selectbox(
                    "Payment Method",
                    ["COD", "PREPAID"],
                    key="rev_payment_val",
                    help="COD = cash-on-delivery. PREPAID = prepaid/online paid."
                )

        st.write("")

    # ==================================================================
    # FORWARD SHIPPING SECTION
    # ==================================================================

    else:

        # ── Row 1: Channel Code | State Code ────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Channel Code**")
            sp_use_channel = st.checkbox(
                "Apply Channel Code Filter",
                key="sp_use_channel",
                help=(
                    "Filter courier rules by the sales channel code on the shipping package.\n\n"
                    "**Single value** → `#shippingPackage.saleOrder.channel.code == 'SHOPIFY'`\n\n"
                    "**Multiple values** → `T(StringUtils).equalsAny(#shippingPackage.saleOrder"
                    ".channel.code, 'FLIPKART', 'AMAZON_IN')`\n\n"
                    "Enable case-insensitive toggle if channel codes may have mixed casing."
                )
            )
            sp_channel_val = ""
            sp_channel_icase = False
            if sp_use_channel:
                sp_channel_val = st.text_input(
                    "Channel Code(s)",
                    key="sp_channel_val",
                    placeholder="Single: SHOPIFY  |  Multiple: FLIPKART, AMAZON_IN"
                )
                sp_channel_icase = st.checkbox(
                    "Case-Insensitive Match (equalsIgnoreCase)",
                    key="sp_channel_icase",
                    help=(
                        "Uses `.equalsIgnoreCase()` for single values or `equalsIgnoreCaseAny()` "
                        "for multiple. Recommended when channel codes may have mixed casing in Uniware."
                    )
                )

        with col2:
            st.markdown("**State Code**")
            sp_use_state = st.checkbox(
                "Apply State Code Filter",
                key="sp_use_state",
                help=(
                    "Restricts courier selection to shipments going to specific state codes.\n\n"
                    "Uses `T(StringUtils).equalsAny(#shippingPackage.shippingAddress.stateCode, ...)`.\n\n"
                    "**Single:** MH  |  **Multiple:** MH, GJ, KA"
                )
            )
            sp_state_val = ""
            if sp_use_state:
                sp_state_val = st.text_input(
                    "State Code(s)",
                    key="sp_state_val",
                    placeholder="Single: MH  |  Multiple: MH, GJ, KA"
                )

        st.write("")

        # ── Row 2: Pincode | Payment Method ─────────────────────────
        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**Pincode**")
            sp_use_pincode = st.checkbox(
                "Apply Pincode Filter",
                key="sp_use_pincode",
                help=(
                    "Restricts courier selection to shipments going to specific pincodes.\n\n"
                    "Uses `T(StringUtils).equalsAny(#shippingPackage.shippingAddress.pincode, ...)`.\n\n"
                    "**Single:** 560001  |  **Multiple:** 560001, 560002, 400001"
                )
            )
            sp_pincode_val = ""
            if sp_use_pincode:
                sp_pincode_val = st.text_area(
                    "Pincode(s)",
                    key="sp_pincode_val",
                    placeholder="Single: 560001  |  Multiple: 560001, 560002, 400001",
                    height=100
                )

        with col4:
            st.markdown("**Payment Method**")
            sp_use_payment = st.checkbox(
                "Apply Payment Method Filter",
                key="sp_use_payment",
                help=(
                    "Restricts courier selection based on payment method.\n\n"
                    "Uses `#shippingPackage.saleOrder.paymentMethod.code == 'COD'` or `'PREPAID'`.\n\n"
                    "Useful for assigning dedicated COD couriers or blocking COD on specific routes."
                )
            )
            sp_payment_val = ""
            if sp_use_payment:
                sp_payment_val = st.selectbox(
                    "Payment Method",
                    ["COD", "PREPAID"],
                    key="sp_payment_val",
                    help="COD = cash-on-delivery. PREPAID = online/prepaid orders."
                )

        st.write("")

        # ── Row 3: Weight | Price ────────────────────────────────────
        col5, col6 = st.columns(2)

        with col5:
            st.markdown("**Package Weight (grams)**")
            sp_use_weight = st.checkbox(
                "Apply Weight Filter",
                key="sp_use_weight",
                help=(
                    "Restricts courier selection by the actual package weight in grams.\n\n"
                    "Uses `#shippingPackage.actualWeight`.\n\n"
                    "Min bound is **exclusive** (`>`), Max bound is **inclusive** (`<=`).\n\n"
                    "Example: Min=500, Max=1000 → "
                    "`#shippingPackage.actualWeight > 500 and #shippingPackage.actualWeight <= 1000`"
                )
            )
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
            sp_use_price = st.checkbox(
                "Apply Price Filter",
                key="sp_use_price",
                help=(
                    "Restricts courier selection by the total declared order value.\n\n"
                    "Uses `#shippingPackage.totalPrice`.\n\n"
                    "Min bound is **exclusive** (`>`), Max bound is **inclusive** (`<=`).\n\n"
                    "Example: Max=6000 → `#shippingPackage.totalPrice <= 6000`"
                )
            )
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
            sp_use_city = st.checkbox(
                "Apply City Filter",
                key="sp_use_city",
                help=(
                    "Restricts courier selection to shipments going to specific cities.\n\n"
                    "Uses `T(StringUtils).equalsAny(#shippingPackage.shippingAddress.city, ...)`.\n\n"
                    "**Single:** Mumbai  |  **Multiple:** Mumbai, Delhi"
                )
            )
            sp_city_val = ""
            if sp_use_city:
                sp_city_val = st.text_input(
                    "City / Cities",
                    key="sp_city_val",
                    placeholder="Single: Mumbai  |  Multiple: Mumbai, Delhi"
                )

        with col8:
            st.markdown("**Country Code**")
            sp_use_country = st.checkbox(
                "Apply Country Code Filter",
                key="sp_use_country",
                help=(
                    "Restricts courier selection by destination country code.\n\n"
                    "Uses `T(StringUtils).equalsAny(#shippingPackage.shippingAddress.countryCode, ...)`.\n\n"
                    "**Single:** IN  |  **Multiple:** IN, US, AE"
                )
            )
            sp_country_val = ""
            if sp_use_country:
                sp_country_val = st.text_input(
                    "Country Code(s)",
                    key="sp_country_val",
                    placeholder="Single: IN  |  Multiple: IN, US, AE"
                )

        st.write("")


        # ── Row 5: Item Count ────────────────────────────────────────────
        col9, col10 = st.columns(2)

        with col9:
            st.markdown("**Number of Items in Package**")
            sp_use_item_count = st.checkbox(
                "Apply Item Count Filter",
                key="sp_use_item_count",
                help=(
                    "Restricts courier selection by the number of line items in the package.\n\n"
                    "Uses `#shippingPackage.saleOrderItems.size()` with your chosen operator.\n\n"
                    "Example: operator `<=`, value `12` \u2192 "
                    "`#shippingPackage.saleOrderItems.size() <= 12`\n\n"
                    "Use this to assign different couriers for single-item vs multi-item shipments."
                )
            )
            sp_item_count_op = "<="
            sp_item_count_val = ""
            if sp_use_item_count:
                sp_item_count_op = st.selectbox(
                    "Operator",
                    ["<=", "<", ">=", ">", "=="],
                    format_func=lambda x: {
                        "<=": "<= (Up to N items — e.g. single or small shipments)",
                        "<":  "<  (Fewer than N items — strictly less)",
                        ">=": ">= (At least N items — e.g. bulk shipments)",
                        ">":  ">  (More than N items — strictly greater)",
                        "==": "== (Exactly N items)"
                    }[x],
                    key="sp_item_count_op",
                    help=(
                        "Comparison operator applied to `#shippingPackage.saleOrderItems.size()`.\n\n"
                        "• `<=` — package has **up to N** items (e.g. `<= 1` for single-item only)\n"
                        "• `<`  — package has **fewer than N** items (strictly less)\n"
                        "• `>=` — package has **at least N** items (e.g. bulk courier threshold)\n"
                        "• `>`  — package has **more than N** items (strictly greater)\n"
                        "• `==` — package has **exactly N** items"
                    )
                )
                sp_item_count_val = st.text_input(
                    "Item Count Threshold",
                    key="sp_item_count_val",
                    placeholder="e.g. 12"
                ).strip()

        with col10:
            st.write("")  # intentionally empty

        st.write("")

# =====================================================================
# INVENTORY CALCULATION MODULE
# =====================================================================

elif module == "INVENTORY_CALC":

    st.subheader("🛠️ Global Synchronizer Formula Constructor")

    v_inv = st.checkbox(
        "Incorporate Virtual Allocated Stock Threshold Multipliers",
        key="calc_v_inv",
        help=(
            "Adds `#inventorySnapshot.virtualInventory` to the base formula.\n\n"
            "Virtual inventory represents stock allocated via virtual/buffer mechanisms "
            "(e.g. safety stock reservations). Enable when your channel sync should "
            "include this virtual pool in the available quantity calculation."
        )
    )

    v_nd = st.checkbox(
        "Incorporate Vendor Catalog Shared Warehouse Stock Pools",
        key="calc_v_nd",
        help=(
            "Adds `#inventorySnapshot.vendorInventory` to the base formula.\n\n"
            "Vendor/drop-ship inventory is stock held at vendor warehouses that is "
            "included in the available-to-sell calculation. Enable for channels that "
            "can fulfil from vendor/drop-ship locations."
        )
    )

    unproc = st.checkbox(
        "Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)",
        key="calc_unproc",
        help=(
            "Deducts `#unprocessedOrderInventory` from the formula.\n\n"
            "Unprocessed orders have been placed on the channel but have not yet "
            "entered Uniware's processing pipeline. They still consume physical stock, "
            "so this value is **subtracted** from available inventory.\n\n"
            "Critical for Amazon Flex and similar slab-based channel integrations "
            "where orders arrive in batches before processing."
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

        # 1. Channel code — auto single/multi via smart_format_string
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

        # 6. Payment method — uses equalsAny as per production data pattern
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

        # 8. SKU code — single → ==, multiple → equalsAny
        if fac_use_sku and fac_sku_val.strip():
            expr = format_multi_value_condition(
                fac_sku_val,
                "#saleOrderItem.skuCode"
            )
            if expr:
                parts.append(expr)

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

        # ── REVERSE PICKUP PATH ──────────────────────────────────────
        if is_reverse:

            rev_parts = []

            # 1. Channel code on reversePickup context
            #    Single → equalsIgnoreCase (dominant pattern in production data)
            #    Multiple → equalsAny
            if rev_channel_val.strip():
                ch_expr = smart_format_string(
                    rev_channel_val,
                    "#reversePickup.saleOrder.channel.code",
                    use_ignore_case=True   # always case-insensitive for reverse pickup
                )
                if ch_expr:
                    rev_parts.append(ch_expr)

            # 2. Box weight on reversePickup.boxWeight (both bounds exclusive)
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

            # 3. State code — reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode
            if rev_use_state and rev_state_val.strip():
                expr = format_multi_value_condition(
                    rev_state_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.stateCode"
                )
                if expr:
                    rev_parts.append(expr)

            # 4. Pincode — reversePickup.saleOrder.shippingPackage.shippingAddress.pincode
            if rev_use_pincode and rev_pincode_val.strip():
                expr = format_multi_value_condition(
                    rev_pincode_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.pincode"
                )
                if expr:
                    rev_parts.append(expr)

            # 5. City — reversePickup.saleOrder.shippingPackage.shippingAddress.city
            if rev_use_city and rev_city_val.strip():
                expr = format_multi_value_condition(
                    rev_city_val,
                    "#reversePickup.saleOrder.shippingPackage.shippingAddress.city"
                )
                if expr:
                    rev_parts.append(expr)

            # 6. Payment method — reversePickup.saleOrder.paymentMethod.code
            if rev_use_payment and rev_payment_val:
                rev_parts.append(
                    f"#reversePickup.saleOrder.paymentMethod.code == '{rev_payment_val}'"
                )

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

        # ── FORWARD SHIPPING PATH ────────────────────────────────────
        else:

            parts = []

            # 1. Channel code — auto single/multi via smart_format_string
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

            # 6. Payment method — direct equality as per production data
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

            # 9. Item count — #shippingPackage.saleOrderItems.size()
            if sp_use_item_count and sp_item_count_val:
                parts.append(
                    f"#shippingPackage.saleOrderItems.size() {sp_item_count_op} {sp_item_count_val}"
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

        # Unprocessed orders CONSUME stock — must be DEDUCTED (original had + which was wrong)
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
