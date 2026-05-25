import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Complete Verified Multi-Parameter Rule Compiler Matrix")

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

# Parsing helpers
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

# =====================================================================
# --- FACILITY ALLOCATION LAYOUT ---
# =====================================================================
if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Core System Identifiers")
        if st.checkbox("Enable Channel / Store Constraints", key="fac_chk_chan"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="AMAZON_IN, FLIPKART", key="fac_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="fac_chk_sku"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="SKU-A, SKU-B", key="fac_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#saleOrderItem.skuCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="fac_chk_bsku"):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="BUNDLE-01", key="fac_inp_bsku")
            if b_in: parts.append(smart_format_string(b_in, "#saleOrderItem.bundleSkuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="fac_chk_tag"):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE", key="fac_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Warehouse Stock Status Triggers")
        if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="fac_chk_f_inv"):
            parts.append("#allocationCriteria.hasInventory()")
