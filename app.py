import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Clean, Safe Multi-Parameter Rule Compiler Matrix with Hover Tooltips")

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

# --- FACILITY ALLOCATION LAYOUT ---
if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Core System Identifiers")
        
        if st.checkbox("Enable Channel / Store Constraints", key="fac_chk_chan", 
                       help="Routes orders based on where they originated (e.g., Amazon, Shopify, Flipkart)."):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key="fac_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="fac_chk_sku", 
                       help="Routes orders containing specific inventory SKU codes to dedicated warehouses."):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key="fac_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#saleOrderItem.itemSkuCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="fac_chk_bsku", 
                       help="Checks if the item is part of a bundled kit or promo package set."):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key="fac_inp_bsku")
            if b_in: parts.append(smart_format_string(b_in, "#saleOrderItem.bundleSkuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="fac_chk_tag", 
                       help="Triggers when a custom flag or operational tag is attached to an order (e.g., VIP, HIGH_VALUE)."):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key="fac_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Warehouse Stock Status Triggers")
        
        if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="fac_chk_f_inv", 
                       help="Ensures the warehouse actually has physical inventory available right now before assigning the order."):
            parts.append("#allocationCriteria.hasInventory()")
            
        if st.checkbox("Enforce Complete Short-Term Catalog Stock Verification", key="fac_chk_f_st_inv", 
                       help="Advanced Uniware logic verifying full multi-item short term supplier stock commits."):
            parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")
        
        if st.checkbox("Enable Destination City Constraints", key="fac_chk_city", 
                       help="Routes orders to warehouses closest to the customer's city to ensure faster delivery."):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key="fac_inp_city")
            if ci_in: parts.append(smart_format_string(ci_in.upper(), "#saleOrderItem.shippingAddress.city", use_ignore_case=True))

        if st.checkbox("Enable Destination State Constraints", key="fac_chk_state", 
                       help="Filters routing boundaries using standardized 2-letter state codes."):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key="fac_inp_state")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="fac_chk_pin", 
                       help="The most precise geographical filter. Compiles automatically into a single-quoted curly bracket array string."):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key="fac_inp_pin")
            if p_in: parts.append(format_pincode_array(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox("Enable Destination Country Validation", key="fac_chk_country", 
                       help="Isolates orders using country codes (e.g., IN for India) to distinguish international from domestic orders."):
            co_in = st.text_input("Enter Destination ISO Country Code:", placeholder="Example: IN", max_chars=3, key="fac_inp_country")
            if co_in: parts.append(f"#saleOrderItem.shippingAddress.countryCode == '{co_in.strip().upper()}'")

# --- SHIPPING PROVIDER LAYOUT ---
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Package System Identifiers")
        
        if st.checkbox("Enable Channel / Store Constraints", key="shp_chk_chan", 
                       help="Allocates couriers based on the originating channel package parameters (#shippingPackage syntax)."):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key="shp_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#shippingPackage.saleOrder.channel.code.toUpperCase()"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="shp_chk_sku", 
                       help="Selects logistics partners based on specific item SKUs inside the package (useful for fragile/bulky items)."):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key="shp_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#shippingPackage.shippingPackageItems[0].channelItemCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="shp_chk_bsku", 
                       help="Applies logistics rules based on active promotional combo packages inside the box."):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key="shp_inp_bsku")
            if b_in: parts.append(smart_format_string(b_in, "#shippingPackage.shippingPackageItems[0].bundleSkuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="shp_chk_tag", 
                       help="Allocates premium/secure shipping providers for packages tagged with custom operational flags."):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key="shp_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')")

    with col2:
        st.subheader("🗺️ Destination Logistics & Weight Parameters")
        
        if st.checkbox("Enable Destination City Constraints", key="shp_chk_city", 
                       help="Assigns regional courier services dynamically based on the customer's delivery city."):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key="shp_inp_city")
            if ci_in: parts.append(smart_format_string(ci_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.city", use_ignore_case=True))

        if st.checkbox("Enable Destination State Constraints", key="shp_chk_state", 
                       help="Filters logistics and surface shipping routing configurations using state boundaries."):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key="shp_inp_state")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.stateCode"))

        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="shp_chk_pin", 
                       help="Ensures precise shipping partner serviceability checks against specific destination pincodes."):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key="shp_inp_pin")
            if p_in: parts.append(format_pincode_array(p_in, "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox("Enable Destination Country Validation", key="shp_chk_country", 
                       help="Triggers distinct international courier selection criteria based on ISO destination values."):
            co_in = st.text_input("Enter Destination ISO Country Code:", placeholder="Example: IN", max_chars=3, key="shp_inp_country")
            if co_in: parts.append(f"#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.countryCode == '{co_in.strip().upper()}'")

        st.markdown("---")
        st.subheader("⚖️ Physical Logistics Parameters")
        
        if st.checkbox("Enforce Dead Weight Range Scale Slabs", key="shp_chk_s_weight", 
                       help="Crucial for heavy shipments. Routes packages using logical math operators based on physical dead-weight in grams."):
            min_w = st.number_input("Minimum Package Weight Bound (Grams):", min_value=0, value=0, key="shp_inp_min_w")
            max_w = st.number_input("Maximum Package Weight Bound (Grams):", min_value=0, value=5000, key="shp_inp_max_w")
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            
        if st.checkbox("Enforce Transaction Payment Mode Type", key="shp_chk_s_pay", 
                       help="Filters packages by Cash on Delivery (COD) vs Prepaid to match courier cash-handling support."):
            pay_type = st.selectbox("Select Target Payment Classification Mode:", ["COD", "PREPAID"], key="shp_inp_pay")
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pay_type}'")

# --- INVENTORY CALCULATION LAYOUT ---
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Synchronizer Formula Constructor")
    
    v_inv = st.checkbox("Incorporate Virtual Allocated Stock Threshold Multipliers", key="calc_virt_inv", 
                        help="Includes your virtual inventory buffers alongside raw physical quantities during sync calculations.")
    
    v_nd = st.checkbox("Incorporate Vendor Catalog Shared Warehouse Stock Pools", key="calc_vend_inv", 
                       help="Includes drop-shipper or vendor catalog pools in the calculation matrix.")
    
    unproc = st.checkbox("Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)", key="calc_unproc_inv", 
                         help="Factors in open channel orders that haven't dropped into processing status yet (critical for Amazon Flex synchronization).")

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
