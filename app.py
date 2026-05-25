import streamlit as st

# =====================================================================
# SYSTEM CONFIGURATION & UI INITIALIZATION
# =====================================================================
st.set_page_config(
    page_title="UniCommerce Master Production Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ UniCommerce Master Production Engine")
st.caption("Version 7.0.0 | Final Unabridged Production Build | Full Logic Matrix")

# 1. Primary Module System Selection
module = st.selectbox(
    "1. Select Operational Target Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY": "Facility Allocation Engine (Warehouse Assignment / Routing Rules)",
        "SHIPPING_FWD": "Shipping Provider Allocation Engine (Courier/Logistics Partner Selection)",
        "INVENTORY_CALC": "Inventory Synchronization Calculation Formula Wrapper"
    }[x]
)

# 2. Dynamic Selection Sub-Types
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
# CORE LOGIC HELPERS (VERIFIED FOR PRODUCTION)
# =====================================================================

def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """Parses user input into SpEL StringUtils functions or direct equality."""
    if not raw_input.strip():
        return ""
    items = [f"'{i.strip()}'" for i in raw_input.split(",") if i.strip()]
    if len(items) > 1:
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(items)})"
    return f"{var_name} == {items[0]}"

def shipping_channel_or_format(raw_input):
    """Builds an explicit OR chain for shipping channels to bypass mapping bugs."""
    if not raw_input.strip():
        return ""
    items = [f"'{i.strip().upper()}'" for i in raw_input.split(",") if i.strip()]
    var = "#shippingPackage.saleOrder.channel.code"
    if len(items) > 1:
        or_chain = " or ".join([f"{var}.equalsIgnoreCase({i})" for i in items])
        return f"({or_chain})"
    return f"{var}.equalsIgnoreCase({items[0]})"

def format_pincode_array(raw_input, var_name):
    """Formats pincodes into the curly-brace array required by Uniware lookups."""
    if not raw_input.strip():
        return ""
    items = [f"'{i.strip()}'" for i in raw_input.split(",") if i.strip()]
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {{{', '.join(items)}}})"

parts = []

# =====================================================================
# --- MODULE A: FACILITY ALLOCATION LAYOUT ---
# =====================================================================
if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Core System Identifiers")

        if st.checkbox(
            "Enable Channel / Store Constraints",
            key="f_chan",
            help="Checks order source. Format: AMAZON_IN, SHOPIFY"
        ):
            c_in = st.text_input(
                "Channel Code(s):",
                placeholder="AMAZON_IN, FLIPKART, MEESHO",
                key="f_c_in"
            )
            if c_in:
                parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="f_sku"):
            s_in = st.text_input(
                "Target Item SKU(s):",
                placeholder="SKU-A, SKU-B",
                key="f_s_in"
            )
            if s_in:
                parts.append(smart_format_string(s_in, "#saleOrderItem.skuCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="f_bsku"):
            b_in = st.text_input(
                "Enter Bundle SKU(s):",
                placeholder="BUNDLE-01",
                key="f_b_in"
            )
            if b_in:
                parts.append(smart_format_string(b_in, "#saleOrderItem.bundleSkuCode"))

        if st.checkbox("Enable Regional State Groups", key="f_reg"):
            region = st.radio(
                "Select Zone:",
                ["NORTH (DL, HR, PB, RJ, UP, UT)", "SOUTH (TN, KA, KL, AP, TS)"]
            )
            states = "DL, HR, PB, RJ, UP, UT" if "NORTH" in region else "TN, KA, KL, AP, TS"
            parts.append(smart_format_string(states, "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox(
            "Enable Specific Order Tag Constraints",
            key="f_tag",
            help="TIP (?): This matches the Order JSON custom field. If JSON value = Rule value, it returns true. SpEL logic: (condition ? true : false)."
        ):
            t_in = st.text_input(
                "Tag Target String:",
                placeholder="e.g. VIP_ORDER",
                key="f_t_in"
            )
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Inventory Triggers")

        if st.checkbox("Has Physical Stock", key="f_inv"):
            parts.append("#allocationCriteria.hasInventory()")

        if st.checkbox("Short-Term Verified Stock", key="f_st_inv"):
            parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination Logistics")

        if st.checkbox("City Constraints", key="f_city"):
            ci_in = st.text_input(
                "Target City Name(s):",
                placeholder="AGRA, DELHI",
                key="f_ci_in"
            )
            if ci_in:
                parts.append(smart_format_string(ci_in.upper(), "#saleOrderItem.shippingAddress.city", True))

        if st.checkbox("State Constraints (Direct)", key="f_state"):
            st_in = st.text_input(
                "2-Letter State Code(s):",
                placeholder="DL, MH, KA",
                key="f_st_in"
            )
            if st_in:
                parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox("Pincode Grid Array", key="f_pin", help="Built-in array formatting for serviceability."):
            p_in = st.text_area(
                "Pincode List:",
                placeholder="110001, 400001",
                key="f_p_in"
            )
            if p_in:
                parts.append(
                    format_pincode_array(
                        p_in,
                        "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"
                    )
                )

        if st.checkbox("Country Validation", key="f_country"):
            co_in = st.text_input(
                "ISO Country Code:",
                placeholder="IN",
                key="f_co_in"
            )
            if co_in:
                parts.append(f"#saleOrderItem.shippingAddress.countryCode == '{co_in.strip().upper()}'")

# =====================================================================
# --- MODULE B: SHIPPING ALLOCATION LAYOUT ---
# =====================================================================
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Package-Level Parameters")

        if st.checkbox("Channel OR Logic", key="s_chan"):
            c_in = st.text_input(
                "Channel Code(s):",
                placeholder="AMAZON_IN, FLIPKART",
                key="s_c_in"
            )
            if c_in:
                parts.append(shipping_channel_or_format(c_in))

        if st.checkbox("Strict SKU Match (Whole Box)", key="s_sku", help="Only triggers if ALL items in package are in this list."):
            s_in = st.text_input(
                "Target SKU(s):",
                key="s_s_in"
            )
            if s_in:
                sl = [f"'{i.strip()}'" for i in s_in.split(",") if i.strip()]
                parts.append(
                    f"((#shippingPackage.saleOrder.saleOrderItems.?[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {', '.join(sl)})]).size() == #shippingPackage.saleOrder.saleOrderItems.size())"
                )

        if st.checkbox("Package Tag Constraints", key="s_tag", help="TIP (?): Validates custom field in shipping package. SpEL logic: (JSON_value ? true : false)."):
            t_in = st.text_input("Tag Value:", key="s_t_in")
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')")

    with col2:
        st.subheader("⚖️ Logistics & Weights")

        if st.checkbox("Weight Range (Grams)", key="s_weight"):
            min_w = st.number_input("Min:", value=0)
            max_w = st.number_input("Max:", value=5000)
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")

        if st.checkbox("Payment Mode", key="s_pay"):
            pm = st.selectbox("Select Mode:", ["COD", "PREPAID"])
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pm}'")

# =====================================================================
# --- MODULE C: INVENTORY CALCULATION LAYOUT ---
# =====================================================================
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Formula Matrix")
    v_inv = st.checkbox("Include Virtual Inventory", key="i_v")
    v_nd = st.checkbox("Include Vendor Shared Stock", key="i_vend")
    unproc = st.checkbox(
        "Include Amazon Flex (Unprocessed Pipeline)",
        key="i_u",
        help="Critical for Amazon Flex sync accuracy."
    )

st.write("---")

# =====================================================================
# 4. COMPILER & FINAL OUTPUT
# =====================================================================
if st.button("Compile Target Token Blueprint", type="primary"):
    final_output = ""

    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Please select conditions.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"

    elif module == "INVENTORY_CALC":
        inv = "#inventorySnapshot.inventory"
        if v_inv:
            inv += " + #inventorySnapshot.virtualInventory"
        if v_nd:
            inv += " + #inventorySnapshot.vendorInventory"

        deduct = "- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) - #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment"
        if unproc:
            deduct += " + #unprocessedOrderInventory"

        core = f"{inv} {deduct}"

        if sub_type == "DEFAULT":
            final_output = f"#{{{core}}}"
        elif sub_type == "BUFFER_3":
            final_output = f"#{{({core})<=3?0:({core})}}"
        elif sub_type == "BUFFER_1":
            final_output = f"#{{({core})<=1?0:({core})}}"
        elif sub_type == "ZERO_SYNC":
            final_output = f"#{{({core})*0}}"

    if final_output:
        st.subheader("📋 Compiled System Token String")
        st.code(final_output, language="java")
