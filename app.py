import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Clean, Memory-Isolated Multi-Parameter Rule Compiler Matrix")

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

# Parsing helpers that intelligently format strings based on user entries
def smart_format_string(raw_input, var_name, use_ignore_case=False):
    if not raw_input.strip():
        return ""
    if "," in raw_input:
        items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
        joined_items = ", ".join(items)
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {joined_items})"
    else:
        return f"{var_name} == '{raw_input.strip()}'"

def format_pincode_array(raw_input, var_name):
    if not raw_input.strip():
        return ""
    items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
    joined_items = "{" + ", ".join(items) + "}"
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {joined_items})"

parts = []

if module in ["FACILITY", "SHIPPING_FWD"]:
    # Define exact syntax mapping fields based on current selected framework target
    prefix = "#saleOrder" if module == "FACILITY" else "#shippingPackage.saleOrder"
    item_prefix = "#saleOrderItem" if module == "FACILITY" else "#shippingPackage.shippingPackageItems[0]"
    address_prefix = "#saleOrderItem.shippingAddress" if module == "FACILITY" else "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress"
    
    chan_var = f"{prefix}.channel.code" if module == "FACILITY" else f"{prefix}.channel.code.toUpperCase()"
    sku_var = f"{item_prefix}.itemSkuCode" if module == "FACILITY" else f"{item_prefix}.channelItemCode"

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Core System Identifiers")
        
        # Channel Match (Isolated Keys prevent cross-contamination)
        if st.checkbox("Enable Channel / Store Constraints", key=f"chk_chan_{module}"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key=f"inp_chan_{module}")
            if c_in:
                parts.append(smart_format_string(c_in.upper(), chan_var))

        # SKU Match
        if st.checkbox("Enable SKU / Catalog Constraints", key=f"chk_sku_{module}"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key=f"inp_sku_{module}")
            if s_in:
                parts.append(smart_format_string(s_in, sku_var))

        # Bundle SKU Match
        if st.checkbox("Enable Combo / Bundle SKU Constraints", key=f"chk_bsku_{module}"):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key=f"inp_bsku_{module}")
            if b_in:
                parts.append(smart_format_string(b_in, f"{item_prefix}.bundleSkuCode"))

        # Order Tag Match
        if st.checkbox("Enable Specific Order Tag Constraints", key=f"chk_tag_{module}"):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key=f"inp_tag_{module}")
            if t_in:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({prefix}.tag, '{t_in.strip()}')")

        # Inventory Availability Triggers (Facility Routing Specific Metrics)
        if module == "FACILITY":
            st.markdown("---")
            st.subheader("📈 Warehouse Stock Status Triggers")
            if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="chk_f_inv_isolated"):
                parts.append("#allocationCriteria.hasInventory()")
            if st.checkbox("Enforce Complete Short-Term Catalog Stock Verification", key="chk_f_st_inv_isolated"):
                parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")
        
        # City Match
        if st.checkbox("Enable Destination City Constraints", key=f"chk_city_{module}"):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key=f"inp_city_{module}")
            if ci_in:
                parts.append(smart_format_string(ci_in.upper(), f"{address_prefix}.city", use_ignore_case=True))

        # State Match
        if st.checkbox("Enable Destination State Constraints", key=f"chk_state_{module}"):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key=f"inp_state_{module}")
            if st_in:
                parts.append(smart_format_string(st_in.upper(), f"{address_prefix}.stateCode"))

        # Pincode Match 
        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key=f"chk_pin_{module}"):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key=f"inp_pin_{module}")
            if p_in:
                pin_target_var = f"{prefix}.saleOrderItems.iterator().next().shippingAddress.pincode" if module == "FACILITY" else f"{address_prefix}.pincode"
                parts.append(format_pincode_array(p_in, pin_target_var))

        #
