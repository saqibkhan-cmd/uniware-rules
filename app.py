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
st.caption("Version 6.0.4 | Final Verified Production Suite | Full Logic Integration")

# 1. Primary Module System Selection
# This defines the SpEL context (Facility vs Shipping vs Inventory)
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
    if not raw_input.strip(): return ""
    items = [f"'{i.strip()}'" for i in raw_input.split(",") if i.strip()]
    if len(items) > 1:
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(items)})"
    return f"{var_name} == {items[0]}"

def shipping_channel_or_format(raw_input):
    """Builds an explicit OR chain for shipping channels to bypass mapping bugs."""
    if not raw_input.strip(): return ""
    items = [f"'{i.strip().upper()}'" for i in raw_input.split(",") if i.strip()]
    var = "#shippingPackage.saleOrder.channel.code"
    if len(items) > 1:
        or_chain = " or ".join([f"{var}.equalsIgnoreCase({i})" for i in items])
        return f"({or_chain})"
    return f"{var}.equalsIgnoreCase({items[0]})"

def format_pincode_array(raw_input, var_name):
    """Formats pincodes into the curly-brace array required by Uniware lookups."""
    if not raw_input.strip(): return ""
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
        
        if st.checkbox("Enable Channel / Store Constraints", key="fac_chk_chan", 
                       help="Checks the order source code. \nExample: AMAZON_IN, FLIPKART"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="AMAZON_IN, SHOPIFY, MEESHO", key="fac_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="fac_chk_sku"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="SKU-1, SKU-2", key="fac_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#saleOrderItem.skuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="fac_chk_tag", 
                       help="TIP: Matches the Order JSON custom field value. If the JSON value matches this text, it returns true. SpEL logic evaluates as (condition ? true : false)."):
            t_in = st.text_input("Enter Tag Target String:", placeholder="e.g. VIP_ORDER", key="fac_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Inventory Availability Triggers")
        if st.checkbox("Enforce Direct Warehouse Stock Match", key="fac_chk_f_inv"):
            parts.append("#allocationCriteria.hasInventory()")
            
        if st.checkbox("Enforce Short-Term Inventory Verification", key="fac_chk_f_st_inv"):
            parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination Logistics")
        if st.checkbox("Enable City Constraints", key="fac_chk_city"):
            ci_in = st.text_input("Target City Name(s):", placeholder="DELHI, MUMBAI", key="fac_inp_city")
            if ci_in: parts.append(smart_format_string(ci_in.upper(), "#saleOrderItem.shippingAddress.city", True))

        if st.checkbox("Enable State Constraints", key="fac_chk_state"):
            st_in = st.text_input("Target State Code(s):", placeholder="DL, HR, MH", key="fac_inp_state")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox("Enable Pincode Grid Array", key="fac_chk_pin", 
                       help="Converts list into the high-performance curly brace array format."):
            p_in = st.text_area("Pincode List:", placeholder="110001, 400001", key="fac_inp_pin")
            if p_in: parts.append(format_pincode_array(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

# =====================================================================
# --- MODULE B: SHIPPING ALLOCATION LAYOUT ---
# =====================================================================
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Package-Level Parameters")
        
        if st.checkbox("Enable Channel OR Logic", key="shp_chk_chan"):
            c_in = st.text_input("Channel Code(s):", placeholder="AMAZON_IN, FLIPKART", key="shp_inp_chan")
            if c_in: parts.append(shipping_channel_or_format(c_in))

        if st.checkbox("Enable Strict SKU Match (Full Package)", key="shp_chk_sku", 
                       help="Assigns courier only if EVERY item in the package is in this list."):
            s_in = st.text_input("Target SKU(s):", key="shp_inp_sku")
            if s_in:
                sl = [f"'{i.strip()}'" for i in s_in.split(",") if i.strip()]
                parts.append(f"((#shippingPackage.saleOrder.saleOrderItems.?[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {', '.join(sl)})]).size() == #shippingPackage.saleOrder.saleOrderItems.size())")

        if st.checkbox("Enable Tag Constraints", key="shp_chk_tag", 
                       help="TIP: Validates package-level metadata. SpEL logic: (JSON_value ? true : false)."):
            t_in = st.text_input("Tag Value:", key="shp_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')")

    with col2:
        st.subheader("⚖️ Logistics & Weight Slabs")
        if st.checkbox("Weight Range (Grams)", key="shp_chk_s_weight"):
            min_w = st.number_input("Min Weight:", value=0, key="shp_min")
            max_w = st.number_input("Max Weight:", value=5000, key="shp_max")
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            
        if st.checkbox("Payment Mode Constraints", key="shp_chk_s_pay"):
            pm = st.selectbox("Select Mode:", ["COD", "PREPAID"], key="shp_inp_pay")
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pm}'")

# =====================================================================
# --- MODULE C: INVENTORY CALCULATION LAYOUT ---
# =====================================================================
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Formula Matrix")
    v_inv = st.checkbox("Incorporate Virtual Inventory", key="c_v")
    v_nd = st.checkbox("Incorporate Vendor Shared Stock", key="c_vend")
    unproc = st.checkbox("Incorporate Amazon Flex (Unprocessed Pipeline)", key="c_u", 
                         help="Adds #unprocessedOrderInventory to the calculation pool.")

st.write("---")

# =====================================================================
# 4. COMPILER & FINAL OUTPUT GENERATOR
# =====================================================================
if st.button("Compile Target Token Blueprint", type="primary"):
    final_output = ""
    
    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Please select at least one condition to generate the rule.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"
            
    elif module == "INVENTORY_CALC":
        inv = "#inventorySnapshot.inventory"
        if v_inv: inv += " + #inventorySnapshot.virtualInventory"
        if v_nd:  inv += " + #inventorySnapshot.vendorInventory"
        
        deduct = "- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) - #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment"
        if unproc: deduct += " + #unprocessedOrderInventory"
        
        core = f"{inv} {deduct}"
        if sub_type == "DEFAULT": final_output = f"#{{{core}}}"
        elif sub_type == "BUFFER_3": final_output = f"#{{({core})<=3?0:({core})}}"
        elif sub_type == "BUFFER_1": final_output = f"#{{({core})<=1?0:({core})}}"
        elif sub_type == "ZERO_SYNC": final_output = f"#{{({core})*0}}"

    if final_output:
        st.subheader("📋 Compiled System Token String")
        st.info("Copy the block below and paste directly into the Uniware Rule field.")
        st.code(final_output, language="java")
