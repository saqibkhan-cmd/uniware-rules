import streamlit as st

# Setup page for wide layout to handle the matrix view
st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Final Production Build | Version 3.0 (All Logic Flaws Corrected)")

# 1. Primary Module System Selection
module = st.selectbox(
    "1. Select Operational Target Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY": "Facility Allocation Engine (Warehouse Assignment)",
        "SHIPPING_FWD": "Shipping Provider Allocation Engine (Courier Selection)",
        "INVENTORY_CALC": "Inventory Synchronization Calculation Wrapper"
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
            "ZERO_SYNC": "Absolute Forced Stock Suppress Override"
        }[x]
    )
else:
    sub_type = st.selectbox("2. Rule Evaluation Type", ["STANDARD_COMBINATIONS"])

st.write("---")
st.write("### 3. Active Parameter Conditions Layer")

# --- CORE LOGIC HELPERS ---

def smart_format_string(raw_input, var_name, use_ignore_case=False):
    """Handles single or multiple values using StringUtils."""
    if not raw_input.strip(): return ""
    items = [f"'{i.strip()}'" for i in raw_input.split(",") if i.strip()]
    if len(items) > 1:
        func = "equalsIgnoreCaseAny" if use_ignore_case else "equalsAny"
        return f"T(com.unifier.core.utils.StringUtils).{func}({var_name}, {', '.join(items)})"
    return f"{var_name} == {items[0]}"

def shipping_channel_or_format(raw_input):
    """Implements the specific OR logic chain for shipping channels."""
    if not raw_input.strip(): return ""
    items = [f"'{i.strip().upper()}'" for i in raw_input.split(",") if i.strip()]
    var = "#shippingPackage.saleOrder.channel.code"
    if len(items) > 1:
        return "(" + " or ".join([f"{var}.equalsIgnoreCase({i})" for i in items]) + ")"
    return f"{var}.equalsIgnoreCase({items[0]})"

def format_pincode_array(raw_input, var_name):
    """Formats pincodes into the curly-brace array format required by Uniware."""
    if not raw_input.strip(): return ""
    items = [f"'{i.strip()}'" for i in raw_input.split(",") if i.strip()]
    return f"T(com.unifier.core.utils.StringUtils).equalsAny({var_name}, {{{', '.join(items)}}})"

parts = []

# =====================================================================
# --- FACILITY ALLOCATION MODULE ---
# =====================================================================
if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Core Identifiers")
        if st.checkbox("Channel Constraints", key="f_chan"):
            c_in = st.text_input("Channel Code(s):", key="f_c_in")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Order Tag (Ternary Logic)", key="f_tag"):
            t_in = st.text_input("Tag Value:", placeholder="VIP_ORDER", key="f_t_in")
            if t_in:
                # INTEGRATED FIX: Added requested ternary ? true : false
                parts.append(f"(T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}') ? true : false)")

        if st.checkbox("SKU/Bundle Check", key="f_sku"):
            s_in = st.text_input("SKU(s):", key="f_s_in")
            if s_in: parts.append(smart_format_string(s_in, "#saleOrderItem.skuCode"))

    with col2:
        st.subheader("🗺️ Logistics & Stock")
        if st.checkbox("State Constraints", key="f_state"):
            st_in = st.text_input("State Code(s):", placeholder="DL, HR, MH", key="f_st_in")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox("Pincode Array", key="f_pin"):
            p_in = st.text_area("Pincodes:", key="f_p_in")
            if p_in: parts.append(format_pincode_array(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox("Inventory Verification", key="f_inv"):
            parts.append("#allocationCriteria.hasInventory()")

# =====================================================================
# --- SHIPPING ALLOCATION MODULE ---
# =====================================================================
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 System Rules")
        if st.checkbox("Channel OR Logic", key="s_chan"):
            c_in = st.text_input("Channel Code(s):", key="s_c_in")
            if c_in: parts.append(shipping_channel_or_format(c_in))

        if st.checkbox("Full Package SKU Match", key="s_sku"):
            s_in = st.text_input("SKU(s):", key="s_s_in")
            if s_in:
                items = [f"'{i.strip()}'" for i in s_in.split(",") if i.strip()]
                parts.append(f"((#shippingPackage.saleOrder.saleOrderItems.?[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {', '.join(items)})]).size() == #shippingPackage.saleOrder.saleOrderItems.size())")

    with col2:
        st.subheader("⚖️ Slabs & Payments")
        if st.checkbox("Weight Range (Grams)", key="s_weight"):
            min_w = st.number_input("Min:", value=0)
            max_w = st.number_input("Max:", value=5000)
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")

        if st.checkbox("Payment Mode", key="s_pay"):
            p_mode = st.selectbox("Mode:", ["COD", "PREPAID"])
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{p_mode}'")

# =====================================================================
# --- INVENTORY CALC MODULE ---
# =====================================================================
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Formula Constructor")
    v_inv = st.checkbox("Virtual Inventory", key="i_v")
    v_nd = st.checkbox("Vendor Inventory", key="i_vend")
    unproc = st.checkbox("Unprocessed Pipeline (Amazon Flex)", key="i_u")

# =====================================================================
# 4. FINAL COMPILER
# =====================================================================
st.write("---")
if st.button("Compile Target Token Blueprint", type="primary"):
    final_output = ""
    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts: st.
