import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Complete Multi-Parameter Rule Compiler Matrix with Simple Explanations")

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

# =====================================================================
# --- FACILITY ALLOCATION LAYOUT ---
# =====================================================================
if module == "FACILITY":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Core System Identifiers")
        
        if st.checkbox("Enable Channel / Store Constraints", key="fac_chk_chan", 
                       help="Checks where the order came from (like Amazon or Shopify) to pick the warehouse. \n\nHow to type it:\n- For 1 store: AMAZON_IN\n- For multiple stores use commas: AMAZON_IN, FLIPKART, MEESHO"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key="fac_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#saleOrder.channel.code"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="fac_chk_sku", 
                       help="Checks the item product code (SKU) to assign it to a specific warehouse.\n\nHow to type it:\n- For 1 item: SKU-XYZ\n- For multiple items use commas: SKU-A, SKU-B, SKU-C"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key="fac_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#saleOrderItem.itemSkuCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="fac_chk_bsku", 
                       help="Checks if the item is part of a special kit, combo set, or multi-pack bundle.\n\nHow to type it:\n- For 1 bundle: BUNDLE-01\n- For multiple bundles use commas: BUNDLE-A, BUNDLE-B"):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key="fac_inp_bsku")
            if b_in: parts.append(smart_format_string(b_in, "#saleOrderItem.bundleSkuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="fac_chk_tag", 
                       help="Checks for custom flags or text labels manually or automatically placed on an order.\n\nHow to type it:\n- Type exactly how your label is spelled, for example: HIGH_VALUE or VIP_ORDER"):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key="fac_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.tag, '{t_in.strip()}')")

        st.markdown("---")
        st.subheader("📈 Warehouse Stock Status Triggers")
        
        if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="fac_chk_f_inv", 
                       help="The system will only use this rule if the selected warehouse actually has real, physical stock available on the shelf right now."):
            parts.append("#allocationCriteria.hasInventory()")
            
        if st.checkbox("Enforce Complete Short-Term Catalog Stock Verification", key="fac_chk_f_st_inv", 
                       help="The system checks and ensures that all upcoming short-term stock updates are fully verified before routing this order."):
            parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")
        
        if st.checkbox("Enable Destination City Constraints", key="fac_chk_city", 
                       help="Checks the customer's delivery city name to route the order to the closest warehouse.\n\nHow to type it:\n- For 1 city: AGRA\n- For multiple cities use commas: AGRA, NEW DELHI, FARIDABAD"):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key="fac_inp_city")
            if ci_in: parts.append(smart_format_string(ci_in.upper(), "#saleOrderItem.shippingAddress.city", use_ignore_case=True))

        if st.checkbox("Enable Destination State Constraints", key="fac_chk_state", 
                       help="Filters routing using the customer's short 2-letter delivery state code.\n\nHow to type it:\n- For 1 state: DL\n- For multiple states use commas: DL, HR, UP"):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key="fac_inp_state")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#saleOrderItem.shippingAddress.stateCode"))

        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="fac_chk_pin", 
                       help="The most exact delivery filter. Type your list of pincodes separated by commas, and the app will automatically build a safe bracket list format for Uniware.\n\nHow to type it:\n- Example: 110001, 110002, 400001"):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key="fac_inp_pin")
            if p_in: parts.append(format_pincode_array(p_in, "#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox("Enable Destination Country Validation", key="fac_chk_country", 
                       help="Filters orders by the destination country initials to keep domestic and international shipments separated.\n\nHow to type it:\n- Example: IN (for India) or US (for United States)"):
            co_in = st.text_input("Enter Destination ISO Country Code:", placeholder="Example: IN", max_chars=3, key="fac_inp_country")
            if co_in: parts.append(f"#saleOrderItem.shippingAddress.countryCode == '{co_in.strip().upper()}'")


# =====================================================================
# --- SHIPPING PROVIDER LAYOUT ---
# =====================================================================
elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📦 Package System Identifiers")
        
        if st.checkbox("Enable Channel / Store Constraints", key="shp_chk_chan", 
                       help="Assigns courier partners based on which store the package was sold from.\n\nHow to type it:\n- For 1 store: AMAZON_IN\n- For multiple stores use commas: AMAZON_IN, FLIPKART, MEESHO"):
            c_in = st.text_input("Enter Channel Code(s):", placeholder="Single: AMAZON_IN   |   Multiple: AMAZON_IN, FLIPKART, MEESHO", key="shp_inp_chan")
            if c_in: parts.append(smart_format_string(c_in.upper(), "#shippingPackage.saleOrder.channel.code.toUpperCase()"))

        if st.checkbox("Enable SKU / Catalog Constraints", key="shp_chk_sku", 
                       help="Assigns couriers based on the actual items sitting inside the package box (great for separating heavy or fragile items).\n\nHow to type it:\n- For 1 item: SKU-XYZ\n- For multiple items use commas: SKU-A, SKU-B, SKU-C"):
            s_in = st.text_input("Enter Target Item SKU(s):", placeholder="Single: SKU-XYZ   |   Multiple: SKU-A, SKU-B, SKU-C", key="shp_inp_sku")
            if s_in: parts.append(smart_format_string(s_in, "#shippingPackage.shippingPackageItems[0].channelItemCode"))

        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="shp_chk_bsku", 
                       help="Assigns couriers based on active promotional combo kits or multi-packs inside the package.\n\nHow to type it:\n- For 1 bundle: BUNDLE-01\n- For multiple bundles use commas: BUNDLE-A, BUNDLE-B"):
            b_in = st.text_input("Enter Bundle SKU(s):", placeholder="Single: BUNDLE-01   |   Multiple: BUNDLE-A, BUNDLE-B", key="shp_inp_bsku")
            if b_in: parts.append(smart_format_string(b_in, "#shippingPackage.shippingPackageItems[0].bundleSkuCode"))

        if st.checkbox("Enable Specific Order Tag Constraints", key="shp_chk_tag", 
                       help="Routes packages using specific couriers based on custom labels added to the order.\n\nHow to type it:\n- Type the exact name of the label, for example: VIP_ORDER or FRAGILE"):
            t_in = st.text_input("Enter Order Tag Target String:", placeholder="Example: HIGH_VALUE_B2B", key="shp_inp_tag")
            if t_in: parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#shippingPackage.saleOrder.tag, '{t_in.strip()}')")

    with col2:
        st.subheader("🗺️ Destination Logistics & Weight Parameters")
        
        if st.checkbox("Enable Destination City Constraints", key="shp_chk_city", 
                       help="Selects couriers based on the customer's delivery city name.\n\nHow to type it:\n- For 1 city: AGRA\n- For multiple cities use commas: AGRA, NEW DELHI, FARIDABAD"):
            ci_in = st.text_input("Enter City Target Name(s):", placeholder="Single: AGRA   |   Multiple: AGRA, NEW DELHI, FARIDABAD", key="shp_inp_city")
            if ci_in: parts.append(smart_format_string(ci_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.city", use_ignore_case=True))

        if st.checkbox("Enable Destination State Constraints", key="shp_chk_state", 
                       help="Selects couriers based on the customer's 2-letter delivery state code.\n\nHow to type it:\n- For 1 state: DL\n- For multiple states use commas: DL, HR, UP"):
            st_in = st.text_input("Enter 2-Letter State Code(s):", placeholder="Single: DL   |   Multiple: DL, HR, UP", key="shp_inp_state")
            if st_in: parts.append(smart_format_string(st_in.upper(), "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.stateCode"))

        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="shp_chk_pin", 
                       help="Filters courier allocation against specific delivery pincodes. Paste numbers separated by commas, and the app formats them safely.\n\nHow to type it:\n- Example: 110001, 110002, 400001"):
            p_in = st.text_area("Enter Pincode List:", placeholder="Example: 110001, 110002, 400001", key="shp_inp_pin")
            if p_in: parts.append(format_pincode_array(p_in, "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode"))

        if st.checkbox("Enable Destination Country Validation", key="shp_chk_country", 
                       help="Assigns international vs domestic couriers using country initials.\n\nHow to type it:\n- Example: IN (for India)"):
            co_in = st.text_input("Enter Destination ISO Country Code:", placeholder="Example: IN", max_chars=3, key="shp_inp_country")
            if co_in: parts.append(f"#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.countryCode == '{co_in.strip().upper()}'")

        st.markdown("---")
        st.subheader("⚖️ Physical Logistics Parameters")
        
        if st.checkbox("Enforce Dead Weight Range Scale Slabs", key="shp_chk_s_weight", 
                       help="Splits courier allocation based on package scale weight measured in grams.\n\nHow to use it:\n- Min: 0, Max: 5000 will automatically route packages that weigh between 0 grams and 5 kilograms."):
            min_w = st.number_input("Minimum Package Weight Bound (Grams):", min_value=0, value=0, key="shp_inp_min_w")
            max_w = st.number_input("Maximum Package Weight Bound (Grams):", min_value=0, value=5000, key="shp_inp_max_w")
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            
        if st.checkbox("Enforce Transaction Payment Mode Type", key="shp_chk_s_pay", 
                       help="Separates courier choices based on how the buyer paid for the order.\n\nHow to select it:\n- Pick COD if the courier needs to collect cash, or PREPAID if the order is already paid."):
            pay_type = st.selectbox("Select Target Payment Classification Mode:", ["COD", "PREPAID"], key="shp_inp_pay")
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pay_type}'")


# =====================================================================
# --- INVENTORY CALCULATION LAYOUT ---
# =====================================================================
elif module == "INVENTORY_CALC":
    st.subheader("🛠️ Global Synchronizer Formula Constructor")
    
    v_inv = st.checkbox("Incorporate Virtual Allocated Stock Threshold Multipliers", key="calc_virt_inv", 
                        help="Include virtual inventory buffers alongside raw physical quantities during sync calculations.")
    
    v_nd = st.checkbox("Incorporate Vendor Catalog Shared Warehouse Stock Pools", key="calc_vend_inv", 
                       help="Include shared vendor or drop-shipper stock quantities in the calculation pool.")
    
    unproc = st.checkbox("Incorporate Unprocessed Channel Pipeline Item Counts (Amazon Flex Slabs)", key="calc_unproc_inv", 
                         help="Count orders that have been placed on marketplaces but haven't dropped into processing status yet (critical for Amazon Flex sync calculations).")

st.write("")

# =====================================================================
# 4. Central Rule Compiler Pipeline Execution Engine
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
