import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Clean, Safe Multi-Parameter Rule Compiler Matrix")

# --- SMART RE-RUN & STATE RESET BLOCKS ---
# Automatically flushes old checked inputs when changing target engines
if "last_module" not in st.session_state:
    st.session_state.last_module = "FACILITY"

def handle_module_change():
    if st.session_state.module_selector != st.session_state.last_module:
        st.session_state.last_module = st.session_state.module_selector
        # Clear out any stale input states across the framework execution
        for key in list(st.session_state.keys()):
            if key not in ["last_module", "module_selector"]:
                del st.session_state[key]

# 1. Primary Module System Selection
module = st.selectbox(
    "1. Select Operational Target Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY": "Facility Allocation Engine (Warehouse Assignment / Routing Rules)",
        "SHIPPING_FWD": "Shipping Provider Allocation Engine (Courier/Logistics Partner Selection)",
        "INVENTORY_CALC": "Inventory Synchronization Calculation Formula Wrapper"
    }[x],
    key="module_selector",
    on_change=handle_module_change
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

# Parsing helpers that intelligently format strings based on user entries
def smart_format_string(raw_input, var_name, use_ignore_case=False):
    if not raw_input.strip():
        return ""
    # If the user put a comma, automatically treat as multiple values
    if "," in raw_input:
        items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
        joined_items = ", ".join(items)
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {joined_items})"
    else:
        # Single standard item match
        return f"{var_name} == '{raw_input.strip()}'"

def format_pincode_array(raw_input, var_name):
    if not raw_input.strip():
        return ""
    items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
    joined_items = "{" + ", ".join(items) + "}"
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {joined_items})"

parts = []

if module in ["FACILITY", "SHIPPING_FWD"]:
    # Setup structural naming variables automatically based on selection
    prefix = "#saleOrder" if module == "FACILITY" else "#shippingPackage.saleOrder"
    item_prefix = "#saleOrderItem" if module == "FACILITY" else "#shippingPackage.shippingPackageItems[0]"
    address_prefix = "#saleOrderItem.shippingAddress" if module == "FACILITY" else "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress"
    
    chan_var = f"{prefix}.channel.code" if module == "FACILITY" else f"{prefix}.channel.code.toUpperCase()"
    sku_var = f"{item_prefix}.itemSkuCode" if module == "FACILITY" else f"{item_prefix}.channelItemCode"

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Core System Identifiers")
        
        # Channel Match
        if st.checkbox("Enable Channel / Store Constraints", key="chk_chan"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key="inp_chan")
            if c_in:
                parts.append(smart_format_string(c_in.upper(), chan_var))

        # SKU Match
        if st.checkbox("Enable SKU / Catalog Constraints", key="chk_sku"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key="inp_sku")
            if s_in:
                parts.append(smart_format_string(s_in, sku_var))

        # Bundle SKU Match
        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="chk_bsku"):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key="inp_bsku")
            if b_in:
                parts.append(smart_format_string(b_in, f"{item_prefix}.bundleSkuCode"))

        # Tag Match
        if st.checkbox("Enable Specific Order Tag Constraints", key="chk_tag"):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key="inp_tag")
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({prefix}.tag, '{t_in.strip()}')")

        # Inventory Availability Triggers (Facility Only)
        if module == "FACILITY":
            st.markdown("---")
            st.subheader("📈 Warehouse Stock Status Triggers")
            if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="chk_f_inv"):
                parts.append("#allocationCriteria.hasInventory()")
            if st.checkbox("Enforce Complete Short-Term Catalog Stock Verification", key="chk_f_st_inv"):
                parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")
        
        # City Match
        if st.checkbox("Enable Destination City Constraints", key="chk_city"):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key="inp_city")
            if ci_in:
                parts.append(smart_format_string(ci_in.upper(), f"{address_prefix}.city", use_ignore_case=True))

        # State Match
        if st.checkbox("Enable Destination State Constraints", key="chk_state"):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key="inp_state")
            if st_in:
                parts.append(smart_format_string(st_in.upper(), f"{address_prefix}.stateCode"))

        # Pincode Match (Always formats with curly bracket array rules)
        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="chk_pin"):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key="inp_pin")
            if p_in:
                pin_target_var = f"{prefix}.saleOrderItems.iterator().next().shippingAddress.pincode" if module == "FACILITY" else f"{address_prefix}.pincode"
                parts.append(format_pincode_array(p_in, pin_target_var))

        # Country Validation
        if st.checkbox("Enable Destination Country Validation", key="chk_country"):
            co_in = st.text_input("Enter Destination ISO Country Code:", placeholder="Example: IN", max_chars=3, key="inp_country")
            if co_in:
                parts.append(f"{address_prefix}.countryCode == '{co_in.strip().upper()}'")

        # Physical Shipment Variables (Shipping Only)
        if module == "SHIPPING_FWD":
            st.markdown("---")
            st.subheader("⚖️ Physical Logistics Parameters")
            if st.checkbox("Enforce Dead Weight Range Scale Slabs", key="chk_s_weight"):
                min_w = st.number_input("Minimum Package Weight Bound (Grams):", min_value=0, value=0, key="inp_min_w")
                max_w = st.number_input("Maximum Package Weight Bound (Grams):", min_value=0, value=5000, key="inp_max_w")
                parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            if st.checkbox("Enforce Transaction Payment Mode Type", key="chk_s_pay"):
                pay_type = st.selectbox("Select Target Payment Classification Mode:", ["COD", "PREPAID"], key="inp_pay")
                parts.append(f"{prefix}.paymentMethod.code == '{pay_type}'")

elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Synchronizer Formula Constructor")
    v_inv = st.checkbox("Incorporate Virtual Allocated Stock Threshold Multipliers", key="calc_virt_inv")
    v_nd = st.checkbox("Incorporate Vendor Catalog Shared Warehouse Stock Pools", key="calc_vend_inv")
    unproc = st.checkbox("Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)", key="calc_unproc_inv")

st.write("")

# 4. Central Rule Compiler Pipeline Execution Engine
if st.button("Compile Target Token Blueprint", type="primary"):
    final_output = ""
    
    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Validation Error: Please select checkboxes and type values to generate a rule sequence.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"
            
    elif module == "INVENTORY_CALC":
        inv_part = "#inventorySnapshot.inventory"
        if v_inv: inv_part += " + #inventorySnapshot.virtualInventory"
        if v_nd:  inv_part += " + #inventorySnapshot.vendorInventory"
        
        deduct_part = "- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) - #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment"
        if unproc: deduct_part += " + #unprocessedOrderInventory"
        
        core_expr = f"{inv_part} {deduct_part}"
        
        if sub_type == "DEFAULT": final_output = f"#{{{core_expr}}}"
        elif sub_type == "BUFFER_3": final_output = f"#{{({core_expr})<=3?0:({core_expr})}}"
        elif sub_type == "BUFFER_1": final_output = f"#{{({core_expr})<=1?0:({core_expr})}}"
        elif sub_type == "ZERO_SYNC": final_output = f"#{{({core_expr})*0}}"

    if final_output:
        st.subheader("📋 Compiled System Token String (Copy directly to Uniware)")
        st.code(final_output, language="java")
