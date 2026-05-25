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
st.caption("Version 7.0.0 | Complete Verified Multi-Parameter Rule Compiler Matrix")

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
# DYNAMIC SUB-TYPE SELECTION
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
# CORE HELPER METHODS
# =====================================================================

def _q(item: str) -> str:
    return f"'{item.strip()}'"


def _csv_items(raw_input: str):
    return [item.strip() for item in raw_input.split(",") if item.strip()]


def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """
    Converts user input into Uniware-compatible SpEL expressions.
    - Single value -> direct equality
    - Multiple comma-separated values -> StringUtils.equalsAny / equalsIngoreCaseAny
    """
    if not raw_input or not raw_input.strip():
        return ""

    items = _csv_items(raw_input)
    quoted = [_q(item) for item in items]

    if len(quoted) > 1:
        func = "equalsIngoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(quoted)})"

    if use_ignore_case:
        return f"{var_name}.equalsIgnoreCase({quoted[0]})"

    return f"{var_name} == {quoted[0]}"


def channel_format(raw_input, var_name):
    """
    Builds a compact channel condition that stays close to dump-style rules.
    """
    if not raw_input or not raw_input.strip():
        return ""

    items = [item.strip().upper() for item in raw_input.split(",") if item.strip()]
    if len(items) > 1:
        quoted = ", ".join([_q(item) for item in items])
        return f"T(com.unifier.core.utils.StringUtils).equalsIngoreCaseAny({var_name}, {quoted})"
    return f"{var_name}.equalsIgnoreCase({_q(items[0])}"


def format_pincode_array(raw_input, var_name):
    """
    Formats pincodes into the curly-brace array required by Uniware lookups.
    """
    if not raw_input or not raw_input.strip():
        return ""

    items = [_q(item) for item in _csv_items(raw_input)]
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {{{', '.join(items)}}})"


def inventory_method_expression(method_key: str) -> str:
    method_map = {
        "PHYSICAL": "#allocationCriteria.hasInventory()",
        "FULFILLABLE": "#allocationCriteria.hasFulfillableInventory()",
        "LIVE": "#allocationCriteria.hasLiveInventory()",
        "LIVE_LOWER": "#allocationCriteria.hasliveInventory()",
        "SHORT_TERM": "#allocationCriteria.hasShortTermInventory()",
        "SHORT_TERM_COMPLETE": "#allocationCriteria.hasCompleteShortTermInventory()",
        "COMPLETE": "#allocationCriteria.hasCompleteInventory()",
        "MID_TERM_COMPLETE": "#allocationCriteria.hasCompleteMidTermInventory()",
        "LONG_TERM_COMPLETE": "#allocationCriteria.hasCompleteLongTermInventory()",
        "LONG_TERM": "#allocationCriteria.hasLongTermInventory()",
    }
    return method_map.get(method_key, "")

parts = []

# =====================================================================
# FACILITY ALLOCATION MODULE
# =====================================================================
if module == "FACILITY":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Core System Identifiers")

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
                parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

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
                parts.append(smart_format_string(s_in, "#saleOrderItem.skuCode"))

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
                parts.append(smart_format_string(b_in, "#saleOrderItem.bundleSkuCode"))

        if st.checkbox(
            "Enable Regional State Group Routing",
            key="fac_chk_region",
            help="""
Creates predefined regional warehouse routing logic.

Useful for:
- North vs South warehouse separation
- Faster regional fulfillment
- Zonal allocation policies
"""
        ):
            region = st.radio(
                "Select Region Group:",
                ["NORTH (DL, HR, PB, RJ, UP, UT)", "SOUTH (TN, KA, KL, AP, TS)"],
                key="fac_region_radio"
            )
            states = "DL, HR, PB, RJ, UP, UT" if "NORTH" in region else "TN, KA, KL, AP, TS"
            parts.append(smart_format_string(states, "#saleOrderItem.shippingAddress.stateCode", use_ignore_case=True))

        if st.checkbox(
            "Enable Specific Order Tag Constraints",
            key="fac_chk_tag",
            help="""
Matches custom order tags added through integrations, workflows, or manual tagging.

Examples:
- HIGH_VALUE
- VIP_ORDER
- B2B_PRIORITY

Rule returns TRUE when the order tag matches the configured value.
"""
        ):
            t_in = st.text_input(
                "Enter Order Tag Target String:",
                placeholder="Example: HIGH_VALUE_B2B",
                key="fac_inp_tag"
            )
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Warehouse Stock Status Triggers")

        if st.checkbox(
            "Enable Inventory Method Constraints",
            key="fac_chk_inv_method",
            help="""
Pick the stock-status rule used by the allocation dump.

Examples:
- Physical stock only
- Short-term stock
- Complete short-term stock
- Fulfillable / live / complete inventory
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
                    ("LONG_TERM", "Long-Term Inventory"),
                ],
                format_func=lambda x: x[1],
                key="fac_inv_method"
            )
            parts.append(inventory_method_expression(inv_method[0]))

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")

        if st.checkbox(
            "Enable Destination City Constraints",
            key="fac_chk_city",
            help="""
Routes orders based on destination city.

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
                parts.append(smart_format_string(ci_in.upper(), "#saleOrderItem.shippingAddress.city", use_ignore_case=True))

        if st.checkbox(
            "Enable Destination State Constraints",
            key="fac_chk_state",
            help="""
Filters orders using destination state codes.

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
                parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode", use_ignore_case=True))

        if st.checkbox(
            "Enable Destination Pincode Grid Array Constraints",
            key="fac_chk_pin",
            help="""
Highly granular routing using destination pincodes.

Examples:
110001, 110002, 400001

The system automatically formats the array into Uniware-compatible syntax.
"""
        ):
            p_in = st.text_area(
                "Enter Pincode List:",
                placeholder="Example: 110001, 110002, 400001",
                key="fac_inp_pin"
            )
            if p_in:
                parts.append(format_pincode_array(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox(
            "Enable Destination Country Validation",
            key="fac_chk_country",
            help="""
Separates domestic and international order routing using ISO country codes.

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
                parts.append(f"#saleOrderItem.shippingAddress.countryCode == '{co_in.strip().upper()}'")

# =====================================================================
# SHIPPING PROVIDER MODULE
# =====================================================================
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📦 Package System Identifiers")

        reverse_mode = st.checkbox(
            "Use Reverse Pickup Channel Context",
            key="shp_chk_reverse",
            help="""
Switches the channel source to reverse pickup rules.

Use this when the dump uses:
#reversePickup.saleOrder.channel.code
"""
        )

        channel_var = "#reversePickup.saleOrder.channel.code" if reverse_mode else "#shippingPackage.saleOrder.channel.code"

        if st.checkbox(
            "Enable Channel / Store Constraints",
            key="shp_chk_chan",
            help="""
Assigns courier partners based on which store the package was sold from.

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
                parts.append(channel_format(c_in, channel_var))

        if st.checkbox(
            "Enable SKU / Catalog Constraints",
            key="shp_chk_sku",
            help="""
Assigns couriers based on the actual items sitting inside the package box.

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
                sku_items = [f"'{i.strip()}'" for i in s_in.split(",") if i.strip()]
                if len(sku_items) > 1:
                    joined_items = ", ".join(sku_items)
                    parts.append(
                        f"((#shippingPackage.saleOrder.saleOrderItems.?[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {joined_items})]).size() == #shippingPackage.saleOrder.saleOrderItems.size())"
                    )
                elif sku_items:
                    parts.append(
                        f"((#shippingPackage.saleOrder.saleOrderItems.?[itemType.skuCode == {sku_items[0]}]).size() == #shippingPackage.saleOrder.saleOrderItems.size())"
                    )

        if st.checkbox(
            "Enable Combo / Bundle SKU Constraints",
            key="shp_chk_bsku",
            help="""
Assigns couriers based on active promotional combo kits or multi-packs inside the package.

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
                parts.append(smart_format_string(b_in, "#shippingPackage.shippingPackageItems[0].bundleSkuCode"))

        if st.checkbox(
            "Enable Shipping Package Type Constraints",
            key="shp_chk_pkg_type",
            help="""
Matches the package type code used by the allocation engine.

This is not the shipment ID.
Use it when the dump routes by:
- package type
- box type
- parcel type
"""
        ):
            pkg_type = st.text_input(
                "Enter Shipping Package Type Code(s):",
                placeholder="Single: A3   |   Multiple: A3, A15, T-RJ",
                key="shp_inp_pkg_type"
            )
            if pkg_type:
                parts.append(smart_format_string(pkg_type, "#shippingPackage.shippingPackageType.code", use_ignore_case=True))

        if st.checkbox(
            "Enable Specific Order Tag Constraints",
            key="shp_chk_tag",
            help="""
Routes packages using specific couriers based on custom labels added to the order.

Examples:
- VIP_ORDER
- FRAGILE
- EXPRESS_ONLY
"""
        ):
            t_in = st.text_input(
                "Enter Order Tag Target String:",
                placeholder="Example: HIGH_VALUE_B2B",
                key="shp_inp_tag"
            )
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')")

    with col2:
        st.subheader("🗺️ Destination Logistics & Weight Parameters")

        if st.checkbox(
            "Enable Destination City Constraints",
            key="shp_chk_city",
            help="""
Selects couriers based on the customer's delivery city.

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
                parts.append(smart_format_string(ci_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.city", use_ignore_case=True))

        if st.checkbox(
            "Enable Destination State Constraints",
            key="shp_chk_state",
            help="""
Selects couriers based on the customer's 2-letter delivery state code.

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
                parts.append(smart_format_string(st_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.stateCode", use_ignore_case=True))

        if st.checkbox(
            "Enable Destination Pincode Grid Array Constraints",
            key="shp_chk_pin",
            help="""
Filters courier allocation against specific delivery pincodes.

Examples:
110001, 110002, 400001

The system automatically formats the array into Uniware-compatible syntax.
"""
        ):
            p_in = st.text_area(
                "Enter Pincode List:",
                placeholder="Example: 110001, 110002, 400001",
                key="shp_inp_pin"
            )
            if p_in:
                parts.append(format_pincode_array(p_in, "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox(
            "Enable Destination Country Validation",
            key="shp_chk_country",
            help="""
Assigns international vs domestic couriers using country initials.

Examples:
- IN (for India)
- US (for United States)
"""
        ):
            co_in = st.text_input(
                "Enter Destination ISO Country Code:",
                placeholder="Example: IN",
                max_chars=3,
                key="shp_inp_country"
            )
            if co_in:
                parts.append(f"#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.countryCode == '{co_in.strip().upper()}'")

        st.markdown("---")
        st.subheader("⚖️ Physical Logistics Parameters")

        if st.checkbox(
            "Enforce Dead Weight Range Scale Slabs",
            key="shp_chk_s_weight",
            help="""
Splits courier allocation based on package scale weight measured in grams.

How to use it:
- Min: 0, Max: 5000 will automatically route packages that weigh between 0 grams and 5 kilograms.
"""
        ):
            min_w = st.number_input(
                "Minimum Package Weight Bound (Grams):",
                min_value=0,
                value=0,
                key="shp_inp_min_w"
            )
            max_w = st.number_input(
                "Maximum Package Weight Bound (Grams):",
                min_value=0,
                value=5000,
                key="shp_inp_max_w"
            )
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")

        if st.checkbox(
            "Enforce Transaction Payment Mode Type",
            key="shp_chk_s_pay",
            help="""
Separates courier choices based on how the buyer paid for the order.

How to select it:
- Pick COD if the courier needs to collect cash, or PREPAID if the order is already paid.
"""
        ):
            pay_type = st.selectbox(
                "Select Target Payment Classification Mode:",
                ["COD", "PREPAID"],
                key="shp_inp_pay"
            )
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pay_type}'")

# =====================================================================
# INVENTORY CALCULATION MODULE
# =====================================================================
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Synchronizer Formula Constructor")

    v_inv = st.checkbox(
        "Incorporate Virtual Allocated Stock Threshold Multipliers",
        key="calc_virt_inv",
        help="""
Include virtual stock quantities along with physical warehouse inventory during calculations.
"""
    )

    v_nd = st.checkbox(
        "Incorporate Vendor Catalog Shared Warehouse Stock Pools",
        key="calc_vend_inv",
        help="""
Include shared vendor or drop-shipper stock quantities in the calculation pool.
"""
    )

    unproc = st.checkbox(
        "Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)",
        key="calc_unproc_inv",
        help="""
Count orders that have been placed on marketplaces but haven't dropped into processing status yet.

Critical for Amazon Flex sync calculations and delayed ingestion scenarios.
"""
    )

st.write("")

# =====================================================================
# COMPILER & FINAL OUTPUT
# =====================================================================
if st.button("Compile Target Token Blueprint", type="primary"):
    final_output = ""

    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Validation Error: Please select checkboxes and type values to generate a rule sequence.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"

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

    if final_output:
        st.subheader("📋 Compiled System Token String (Copy directly to Uniware)")
        st.code(final_output, language="java")
