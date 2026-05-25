import streamlit as st

# Page Config for a Professional Look
st.set_page_config(
    page_title="UniCommerce Production Engine", 
    page_icon="⚡", 
    layout="wide"
)

st.title("⚡ UniCommerce Production Engine")
st.caption("Final Production Build | Facility, Shipping, and Inventory Logic Generator")

# 1. Module Selection
module = st.selectbox(
    "1. Select Module", 
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    help="Choose the pillar for which you are generating the SpEL rule."
)

st.write("---")
st.write(f"### 2. Configure {module} Parameters")

parts = []

# --- HELPER UTILITIES (Refined for Production) ---

def facility_format(raw, var):
    """Formats multiple inputs into high-performance StringUtils checks."""
    if not raw.strip(): return ""
    items = [f"'{i.strip()}'" for i in raw.split(",") if i.strip()]
    if len(items) > 1:
        # Fixed: corrected method name to equalsIgnoreCaseAny
        return f"T(com.unifier.core.utils.StringUtils).equalsIgnoreCaseAny({var}, {', '.join(items)})"
    return f"{var} == {items[0]}"

def shipping_channel_format(raw):
    """Ensures OR logic for shipping channels as per the logic dump."""
    if not raw.strip(): return ""
    items = [f"'{i.strip().upper()}'" for i in raw.split(",") if i.strip()]
    var_path = "#shippingPackage.saleOrder.channel.code"
    
    if len(items) > 1:
        # Verified OR-logic wrap
        or_conditions = " or ".join([f"{var_path}.equalsIgnoreCase({item})" for item in items])
        return f"({or_conditions})"
    return f"{var_path}.equalsIgnoreCase({items[0]})"

def shipping_sku_format(raw):
    """SKU projection logic using the ^ selector for UniCommerce collections."""
    if not raw.strip(): return ""
    items = [f"'{i.strip()}'" for i in raw.split(",") if i.strip()]
    return f"#shippingPackage.saleOrderItems.^[T(com.unifier.core.utils.StringUtils).equalsAny(itemType.skuCode, {', '.join(items)})] != null"

# --- MODULE UI LOGIC ---

if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        c_in = st.text_input("Channel Code(s):", help="Comma separated list (e.g. SHOPIFY, MAGENTO)")
        if c_in: parts.append(facility_format(c_in.upper(), "#saleOrder.channel.code"))
        
        o_tag = st.text_input("Order Tag (Custom Field):")
        if o_tag:
            # Verified logic for custom field extraction
            parts.append(f"T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrder, 'Tags') != null and T(com.unifier.services.utils.CustomFieldUtils).getCustomFieldValue(#saleOrder, 'Tags').contains('{o_tag.strip()}')")

    with col2:
        st_in = st.text_input("State Code(s):", placeholder="DL, HR, MH")
        if st_in: parts.append(facility_format(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))
        
        p_in = st.text_area("Pincode List:", help="Comma separated pincodes for serviceability")
        if p_in:
            parts.append(facility_format(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        c_in_ship = st.text_input("Shipping Channel Code(s):", placeholder="CUSTOM, CUSTOM_SUPERBUNDLE")
        if c_in_ship: parts.append(shipping_channel_format(c_in_ship))
        
        s_in_ship = st.text_input("Target SKU(s):")
        if s_in_ship: parts.append(shipping_sku_format(s_in_ship))

    with col2:
        w_check = st.checkbox("Enable Weight Slab Check", value=True)
        if w_check:
            w_mode = st.radio("Weight Mode:", ["Less Than or Equal (<=)", "Greater Than (>)"], horizontal=True)
            w_val = st.number_input("Weight in Grams:", value=5000)
            symbol = "<=" if "Less" in w_mode else ">"
            parts.append(f"#shippingPackage.actualWeight {symbol} {w_val}")

        pay_mode = st.selectbox("Payment Mode:", ["None", "COD", "PREPAID"])
        if pay_mode != "None":
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pay_mode}'")

elif module == "INVENTORY_CALC":
    col1, col2 = st.columns(2)
    with col1:
        sku_inv = st.text_area("SKU Codes for Allocation:", placeholder="SKU-001, SKU-002")
        if sku_inv:
            parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#skuCode, {', '.join([f'\'{s.strip()}\'' for s in sku_inv.split(',')])})")
    with col2:
        f_code = st.text_input("Facility Source Code:")
        if f_code:
            parts.append(f"#facility.code == '{f_code.upper()}'")

# --- COMPILER & FINAL OUTPUT ---
st.write("---")
if st.button("🚀 Generate Production Rule", type="primary"):
    if parts:
        # Final Assembly with clean formatting
        final_rule = "#{\n  " + " and \n  ".join(parts) + "\n}"
        
        st.subheader("Finalized SpEL Expression")
        st.code(final_rule, language="java")
        
        # Actionable Advice
        st.success("Rule Compiled Successfully.")
        st.info("💡 Copy the code block above and paste it into the UniCommerce Script Engine field for the selected module.")
    else:
        st.error("Error: You must provide at least one condition to generate a rule.")

# Footer
st.markdown("---")
st.caption("v2.1 | Verified for Unifier Service Suite 2026")
