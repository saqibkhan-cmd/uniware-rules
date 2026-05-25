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

    if not raw_input.strip():
        return ""

    items = quoted_csv(raw_input)

    if len(items) > 1:
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(items)})"

    if use_ignore_case:
        return f"{var_name}.equalsIgnoreCase({items[0]})"

    return f"{var_name} == {items[0]}"

def shipping_channel_or_format(raw_input, channel_var):

    if not raw_input.strip():
        return ""

    items = csv_items(raw_input)

    if len(items) > 1:
        return "(" + " or ".join([
            f"{channel_var}.equalsIgnoreCase('{x.upper()}')"
            for x in items
        ]) + ")"

    return f"{channel_var}.equalsIgnoreCase('{items[0].upper()}')"

def format_pincode_array(raw_input, var_name):

    if not raw_input.strip():
        return ""

    items = quoted_csv(raw_input)

    return (
        f"T(com.unifier.core.utils.StringUtils).equalsAny"
        f"({var_name}, {{{', '.join(items)}}})"
    )

def inventory_method_expression(method_key):

    inventory_methods = {
        "PHYSICAL":
            "#allocationCriteria.hasInventory()",

        "FULFILLABLE":
            "#allocationCriteria.hasFulfillableInventory()",

        "LIVE":
            "#allocationCriteria.hasLiveInventory()",

        "LIVE_LOWER":
            "#allocationCriteria.hasliveInventory()",

        "SHORT_TERM":
            "#allocationCriteria.hasShortTermInventory()",

        "SHORT_TERM_COMPLETE":
            "#allocationCriteria.hasCompleteShortTermInventory()",

        "COMPLETE":
            "#allocationCriteria.hasCompleteInventory()",

        "MID_TERM_COMPLETE":
            "#allocationCriteria.hasCompleteMidTermInventory()",

        "LONG_TERM_COMPLETE":
            "#allocationCriteria.hasCompleteLongTermInventory()",

        "LONG_TERM":
            "#allocationCriteria.hasLongTermInventory()"
    }

    return inventory_methods.get(method_key, "")

parts = []

# =====================================================================
# FACILITY MODULE
# =====================================================================

if module == "FACILITY":

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("📦 Core System Identifiers")

        # ==============================================================
        # CHANNEL
        # ==============================================================

        if st.checkbox(
            "Enable Channel / Store Constraints",
            key="fac_chk_chan",
            help="""
Checks where the order originated from and routes it to specific warehouses.

Examples:
- Single Channel: AMAZON_IN
- Multiple Channels: AMAZON_IN, FLIPKART, MEESHO
"""
        ):

            c_in = st.text_input(
                "Enter Channel Code(s):",
                placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO",
                key="fac_inp_chan"
            )

            if c_in:
                parts.append(
                    smart_format_string(
                        c_in.upper(),
                        "#saleOrder.channel.code"
                    )
                )

        # ==============================================================
        # SKU
        # ==============================================================

        if st.checkbox(
            "Enable SKU / Catalog Constraints",
            key="fac_chk_sku",
            help="""
Checks the product SKU and routes matching items to specific facilities.

Examples:
- Single SKU: SKU-XYZ
- Multiple SKUs: SKU-A, SKU-B, SKU-C
"""
        ):

            s_in = st.text_input(
                "Enter Target Item SKU(s):",
                placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C",
                key="fac_inp_sku"
            )

            if s_in:
                parts.append(
                    smart_format_string(
                        s_in,
                        "#saleOrderItem.skuCode"
                    )
                )

        # ==============================================================
        # BUNDLE SKU
        # ==============================================================

        if st.checkbox(
            "Enable Combo / Bundle SKU Constraints",
            key="fac_chk_bsku",
            help="""
Checks whether the item belongs to a combo, kit, or bundle SKU.

Examples:
- Single Bundle: BUNDLE-01
- Multiple Bundles: BUNDLE-A, BUNDLE-B
"""
        ):

            b_in = st.text_input(
                "Enter Bundle SKU(s):",
                placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B",
                key="fac_inp_bsku"
            )

            if b_in:
                parts.append(
                    smart_format_string(
                        b_in,
                        "#saleOrderItem.bundleSkuCode"
                    )
                )

        # ==============================================================
        # TAG
        # ==============================================================

        if st.checkbox(
            "Enable Specific Order Tag Constraints",
            key="fac_chk_tag",
            help="""
Tip:
For this rule to work properly:

- The tag in the Order JSON
- The custom field name
- The value entered in this rule

must all match exactly.
"""
        ):

            t_in = st.text_input(
                "Enter Order Tag Target String:",
                placeholder="Example: HIGH_VALUE_B2B",
                key="fac_inp_tag"
            )

            if t_in:
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')"
                )

        st.markdown("---")
        st.subheader("📈 Warehouse Stock Status Triggers")

        # ==============================================================
        # INVENTORY METHODS
        # ==============================================================

        if st.checkbox(
            "Enable Inventory Method Constraints",
            key="fac_chk_inv_method",
            help="""
Select the inventory method used in the allocation dump.

Examples:
- Physical Inventory
- Fulfillable Inventory
- Live Inventory
- Complete Short-Term Inventory
- Long-Term Inventory
"""
        ):

            inv_method = st.selectbox(
                "Select Inventory Method:",
                [
                    ("PHYSICAL", "Physical Warehouse Inventory"),
                    ("FULFILLABLE", "Fulfillable Inventory"),
                    ("LIVE", "Live Inventory"),
                    ("LIVE_LOWER", "Live Inventory (Lowercase Variant)"),
                    ("SHORT_TERM", "Short-Term Inventory"),
                    ("SHORT_TERM_COMPLETE", "Complete Short-Term Inventory"),
                    ("COMPLETE", "Complete Inventory"),
                    ("MID_TERM_COMPLETE", "Complete Mid-Term Inventory"),
                    ("LONG_TERM_COMPLETE", "Complete Long-Term Inventory"),
                    ("LONG_TERM", "Long-Term Inventory")
                ],
                format_func=lambda x: x[1],
                key="fac_inv_method"
            )

            parts.append(
                inventory_method_expression(inv_method[0])
            )

    # =================================================================
    # RIGHT COLUMN
    # =================================================================

    with col2:

        st.subheader("🗺️ Destination & Shipment Rules")

        # ==============================================================
        # CITY
        # ==============================================================

        if st.checkbox(
            "Enable Destination City Constraints",
            key="fac_chk_city",
            help="""
Routes orders using destination city names.

Examples:
- Single City: AGRA
- Multiple Cities: AGRA, NEW DELHI, FARIDABAD
"""
        ):

            ci_in = st.text_input(
                "Enter City Target Name(s):",
                placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD",
                key="fac_inp_city"
            )

            if ci_in:
                parts.append(
                    smart_format_string(
                        ci_in.upper(),
                        "#saleOrderItem.shippingAddress.city",
                        use_ignore_case=True
                    )
                )

        # ==============================================================
        # STATE
        # ==============================================================

        if st.checkbox(
            "Enable Destination State Constraints",
            key="fac_chk_state",
            help="""
Filters routing using destination state codes.

Examples:
- Single State: DL
- Multiple States: DL, HR, UP
"""
        ):

            st_in = st.text_input(
                "Enter 2-Letter State Code(s):",
                placeholder="Single: DL   |   Multiple: DL, HR, UP",
                key="fac_inp_state"
            )

            if st_in:
                parts.append(
                    smart_format_string(
                        st_in.upper(),
                        "#saleOrderItem.shippingAddress.stateCode",
                        use_ignore_case=True
                    )
                )

        # ==============================================================
        # PINCODE
        # ==============================================================

        if st.checkbox(
            "Enable Destination Pincode Grid Array Constraints",
            key="fac_chk_pin",
            help="""
Most precise delivery filter.

Examples:
110001, 110002, 400001

The system automatically converts this into Uniware-compatible array syntax.
"""
        ):

            p_in = st.text_area(
                "Enter Pincode List:",
                placeholder="Example: 110001, 110002, 400001",
                key="fac_inp_pin"
            )

            if p_in:
                parts.append(
                    format_pincode_array(
                        p_in,
                        "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"
                    )
                )

        # ==============================================================
        # COUNTRY
        # ==============================================================

        if st.checkbox(
            "Enable Destination Country Validation",
            key="fac_chk_country",
            help="""
Separates domestic and international routing using ISO country codes.

Examples:
- IN = India
- US = United States
"""
        ):

            co_in = st.text_input(
                "Enter Destination ISO Country Code:",
                placeholder="Example: IN",
                max_chars=3,
                key="fac_inp_country"
            )

            if co_in:
                parts.append(
                    f"#saleOrderItem.shippingAddress.countryCode == '{co_in.strip().upper()}'"
                )

# =====================================================================
# SHIPPING MODULE
# =====================================================================

elif module == "SHIPPING_FWD":

    col1, col2 = st.columns(2)

    # =================================================================
    # CONTEXT SELECTOR
    # =================================================================

    rule_context = st.selectbox(
        "Select Shipment Evaluation Context",
        ["FORWARD", "REVERSE"],
        help="""
Choose which allocation engine context this rule should target.

FORWARD:
Standard shipping package allocation rules.

REVERSE:
Reverse pickup allocation rules.
"""
    )

    is_reverse = rule_context == "REVERSE"

    channel_var = (
        "#reversePickup.saleOrder.channel.code"
        if is_reverse
        else "#shippingPackage.saleOrder.channel.code"
    )

    weight_var = (
        "#reversePickup.actualWeight"
        if is_reverse
        else "#shippingPackage.actualWeight"
    )

    payment_var = (
        "#reversePickup.saleOrder.paymentMethod.code"
        if is_reverse
        else "#shippingPackage.saleOrder.paymentMethod.code"
    )

    with col1:

        st.subheader("📦 Package System Identifiers")

        # ==============================================================
        # CHANNEL
        # ==============================================================

        if st.checkbox(
            "Enable Channel / Store Constraints",
            key="shp_chk_chan",
            help="""
Assigns courier partners based on sales channel.

Examples:
- Single Channel: AMAZON_IN
- Multiple Channels: AMAZON_IN, FLIPKART, MEESHO
"""
        ):

            c_in = st.text_input(
                "Enter Channel Code(s):",
                placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO",
                key="shp_inp_chan"
            )

            if c_in:
                parts.append(
                    shipping_channel_or_format(
                        c_in,
                        channel_var
                    )
                )

        # ==============================================================
        # SKU
        # ==============================================================

        if st.checkbox(
            "Enable SKU / Catalog Constraints",
            key="shp_chk_sku",
            help="""
Matches packages where ANY item SKU matches the configured list.

Examples:
- Single SKU: SKU-XYZ
- Multiple SKUs: SKU-A, SKU-B, SKU-C
"""
        ):

            s_in = st.text_input(
                "Enter Target Item SKU(s):",
                placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C",
                key="shp_inp_sku"
            )

            if s_in:

                sku_items = [
                    f"'{i.strip()}'"
                    for i in s_in.split(",")
                    if i.strip()
                ]

                joined_items = ", ".join(sku_items)

                parts.append(
                    f"#shippingPackage.saleOrderItems.^[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode,{joined_items})]!=null"
                )

        # ==============================================================
        # BUNDLE SKU
        # ==============================================================

        if st.checkbox(
            "Enable Combo / Bundle SKU Constraints",
            key="shp_chk_bsku",
            help="""
Matches package bundle / combo SKUs.

Examples:
- Single Bundle: BUNDLE-01
- Multiple Bundles: BUNDLE-A, BUNDLE-B
"""
        ):

            b_in = st.text_input(
                "Enter Bundle SKU(s):",
                placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B",
                key="shp_inp_bsku"
            )

            if b_in:
                parts.append(
                    smart_format_string(
                        b_in,
                        "#shippingPackage.shippingPackageItems[0].bundleSkuCode"
                    )
                )

        # ==============================================================
        # PACKAGE TYPE
        # ==============================================================

        if not is_reverse:

            if st.checkbox(
                "Enable Shipping Package Type Constraints",
                key="shp_chk_pkg_type",
                help="""
Matches shipping package / parcel type codes.

Examples:
- Single Type: A3
- Multiple Types: A3, T-RJ, BX15
"""
            ):

                pkg_type = st.text_input(
                    "Enter Shipping Package Type Code(s):",
                    placeholder="Single: A3   |   Multiple: A3, T-RJ, BX15",
                    key="shp_inp_pkg_type"
                )

                if pkg_type:
                    parts.append(
                        smart_format_string(
                            pkg_type,
                            "#shippingPackage.shippingPackageType.code",
                            use_ignore_case=True
                        )
                    )

        else:
            st.info(
                "Shipping Package Type Constraints are unavailable in Reverse Pickup mode."
            )

        # ==============================================================
        # TAG
        # ==============================================================

        if st.checkbox(
            "Enable Specific Order Tag Constraints",
            key="shp_chk_tag",
            help="""
Tip:
For this rule to work properly:

- The tag in the Order JSON
- The custom field name
- The value entered in this rule

must all match exactly.
"""
        ):

            t_in = st.text_input(
                "Enter Order Tag Target String:",
                placeholder="Example: HIGH_VALUE_B2B",
                key="shp_inp_tag"
            )

            if t_in:
                parts.append(
                    f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')"
                )

    # =================================================================
    # RIGHT COLUMN
    # =================================================================

    with col2:

        st.subheader("🗺️ Destination Logistics & Weight Parameters")

        # ==============================================================
        # CITY
        # ==============================================================

        if st.checkbox(
            "Enable Destination City Constraints",
            key="shp_chk_city",
            help="""
Routes courier allocation using customer destination city.

Examples:
- Single City: AGRA
- Multiple Cities: AGRA, NEW DELHI, FARIDABAD
"""
        ):

            ci_in = st.text_input(
                "Enter City Target Name(s):",
                placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD",
                key="shp_inp_city"
            )

            if ci_in:
                parts.append(
                    smart_format_string(
                        ci_in.upper(),
                        "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.city",
                        use_ignore_case=True
                    )
                )

        # ==============================================================
        # STATE
        # ==============================================================

        if st.checkbox(
            "Enable Destination State Constraints",
            key="shp_chk_state",
            help="""
Routes courier allocation using customer destination state.

Examples:
- Single State: DL
- Multiple States: DL, HR, UP
"""
        ):

            st_in = st.text_input(
                "Enter 2-Letter State Code(s):",
                placeholder="Single: DL   |   Multiple: DL, HR, UP",
                key="shp_inp_state"
            )

            if st_in:
                parts.append(
                    smart_format_string(
                        st_in.upper(),
                        "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.stateCode",
                        use_ignore_case=True
                    )
                )

        # ==============================================================
        # PINCODE
        # ==============================================================

        if st.checkbox(
            "Enable Destination Pincode Grid Array Constraints",
            key="shp_chk_pin",
            help="""
Highly granular courier routing using delivery pincodes.

Examples:
110001, 110002, 400001
"""
        ):

            p_in = st.text_area(
                "Enter Pincode List:",
                placeholder="Example: 110001, 110002, 400001",
                key="shp_inp_pin"
            )

            if p_in:
                parts.append(
                    format_pincode_array(
                        p_in,
                        "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"
                    )
                )

        # ==============================================================
        # COUNTRY
        # ==============================================================

        if st.checkbox(
            "Enable Destination Country Validation",
            key="shp_chk_country",
            help="""
Separates domestic and international courier routing.

Examples:
- IN = India
- US = United States
"""
        ):

            co_in = st.text_input(
                "Enter Destination ISO Country Code:",
                placeholder="Example: IN",
                max_chars=3,
                key="shp_inp_country"
            )

            if co_in:
                parts.append(
                    f"#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.countryCode == '{co_in.strip().upper()}'"
                )

        st.markdown("---")
        st.subheader("⚖️ Physical Logistics Parameters")

        # ==============================================================
        # WEIGHT
        # ==============================================================

        if st.checkbox(
            "Enforce Dead Weight Range Scale Slabs",
            key="shp_chk_weight",
            help="""
Routes packages using actual shipment weight in grams.

Example:
0 to 5000 = 0g to 5kg
"""
        ):

            min_w = st.number_input(
                "Minimum Package Weight Bound (Grams):",
                min_value=0,
                value=0,
                key="shp_min_w"
            )

            max_w = st.number_input(
                "Maximum Package Weight Bound (Grams):",
                min_value=0,
                value=5000,
                key="shp_max_w"
            )

            parts.append(
                f"{weight_var} > {min_w} and {weight_var} < {max_w}"
            )

        # ==============================================================
        # PAYMENT
        # ==============================================================

        if st.checkbox(
            "Enforce Transaction Payment Mode Type",
            key="shp_chk_pay",
            help="""
Routes shipments based on payment type.

Options:
- COD
- PREPAID
"""
        ):

            pay_type = st.selectbox(
                "Select Target Payment Classification Mode:",
                ["COD", "PREPAID"],
                key="shp_pay"
            )

            parts.append(
                f"{payment_var} == '{pay_type}'"
            )

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
    # RULE MODULES
    # =================================================================

    if module in ["FACILITY", "SHIPPING_FWD"]:

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

        if unproc:
            deduct_part += " + #unprocessedOrderInventory"

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
