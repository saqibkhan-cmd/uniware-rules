import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Advanced Multi-Parameter Rule Compiler & Syntax Blueprint Matrix")

# Standardized string parser helpers to guarantee safe token building
def format_string_utils_args(raw_input):
    if not raw_input.strip():
        return ""
    items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
    return ", ".join(items)

def format_array_brackets(raw_input):
    if not raw_input.strip():
        return ""
    items = [f"'{item.strip()}'" for item in raw_input.split(",") if item.strip()]
    return "{" + ", ".join(items) + "}"

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

parts = []

if module in ["FACILITY", "SHIPPING_FWD"]:
    # Establish correct backend variable syntax prefixes based on the selected target system
    prefix = "#saleOrder" if module == "FACILITY" else "#shippingPackage.saleOrder"
    item_prefix = "#saleOrderItem" if module == "FACILITY" else "#shippingPackage.shippingPackageItems[0]"
    address_prefix = "#saleOrderItem.shippingAddress" if module == "FACILITY" else "#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress"
    chan_var = f"{prefix}.channel.code" if module == "FACILITY" else f"{prefix}.channel.code.toUpperCase()"
    sku_var = f"{item_prefix}.itemSkuCode" if module == "FACILITY" else f"{item_prefix}.channelItemCode"

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Core System Identifiers")
        
        # Channel Logic Row
        if st.checkbox("Enable Channel / Store Constraints", key="matrix_chan"):
            c_mode = st.radio("Channel Configuration Mode:", ["Single Value Match", "Multi-List Array Match"], key="c_mode", horizontal=True)
            c_in = st.text_input("Enter Channel Code(s):", value="AMAZON_IN", help="Example: AMAZON_IN or for lists: AMAZON_IN, FLIPKART, MEESHO", key="c_in")
            if c_mode == "Single Value Match":
                parts.append(f"{chan_var} == '{c_in.strip().upper()}'")
            else:
                formatted = format_string_utils_args(c_in.upper())
                if formatted:
                    parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({chan_var}, {formatted})")

        # SKU Logic Row
        if st.checkbox("Enable SKU / Catalog Constraints", key="matrix_sku"):
            s_mode = st.radio("SKU Configuration Mode:", ["Single SKU", "Multi-SKU Array Match"], key="s_mode", horizontal=True)
            s_in = st.text_input("Enter Target Item SKU(s):", value="SKU-XYZ-BLUE", help="Example: SKU-XYZ-BLUE or for lists: SKU-A, SKU-B, SKU-C", key="s_in")
            if s_mode == "Single SKU":
                parts.append(f"{sku_var} == '{s_in.strip()}'")
            else:
                formatted = format_string_utils_args(s_in)
                if formatted:
                    parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({sku_var}, {formatted})")

        # Bundle SKU Logic Row
        if st.checkbox("Enable Combo / Bundle SKU Constraints", key="matrix_bsku"):
            b_mode = st.radio("Bundle Configuration Mode:", ["Single Combo Bundle", "Multi-Bundle Array Match"], key="b_mode", horizontal=True)
            b_in = st.text_input("Enter Bundle SKU(s):", value="BUNDLE-COMBO-3PACK", help="Example: BUNDLE-01 or for lists: BUNDLE-A, BUNDLE-B", key="b_in")
            if b_mode == "Single Combo Bundle":
                parts.append(f"{item_prefix}.bundleSkuCode == '{b_in.strip()}'")
            else:
                formatted = format_string_utils_args(b_in)
                if formatted:
                    parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({item_prefix}.bundleSkuCode, {formatted})")

        # Order Tag Constraint
        if st.checkbox("Enable Specific Order Tag Constraints", key="matrix_tag"):
            t_in = st.text_input("Enter Order Tag Target String:", value="HIGH_VALUE_B2B", help="Type exactly how the Tag is labeled in your Uniware environment.", key="t_in")
            parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({prefix}.tag, '{t_in.strip()}')")

        # Inventory Availability Triggers (Facility Only Metric)
        if module == "FACILITY":
            st.markdown("---")
            st.subheader("📈 Stock Status Triggers")
            if st.checkbox("Enforce Direct Active Warehouse Inventory Match", key="f_inv_live"):
                parts.append("#allocationCriteria.hasInventory()")
            if st.checkbox("Enforce Complete Short-Term Catalog Stock Verification", key="f_inv_short"):
                parts.append("#allocationCriteria.hasCompleteShortTermInventory()")

    with col2:
        st.subheader("🗺️ Destination & Shipment Rules")
        
        # City Matching Logic
        if st.checkbox("Enable Destination City Constraints", key="matrix_city"):
            ci_mode = st.radio("City Selection Mode:", ["Single City Match", "Multi-City List Match"], key="ci_mode", horizontal=True)
            ci_in = st.text_area("Enter City Target Name(s):", value="AGRA, NEW DELHI, MUMBAI", help="Separate multiple values using commas.", key="ci_in")
            if ci_mode == "Single City Match":
                parts.append(f"{address_prefix}.city.toUpperCase() == '{ci_in.strip().upper()}'")
            else:
                formatted = format_string_utils_args(ci_in.upper())
                if formatted:
                    parts.append(f"T(com.unifier.core.utils.StringUtils).equalsIgnoreCaseAny({address_prefix}.city, {formatted})")

        # State Matching Logic
        if st.checkbox("Enable Destination State Constraints", key="matrix_state"):
            st_mode = st.radio("State Selection Mode:", ["Single State Match", "Multi-State List Match"], key="st_mode", horizontal=True)
            st_in = st.text_input("Enter 2-Letter State Code(s):", value="DL, HR, UP", help="Example: DL or for lists: DL, HR, MH", key="st_in")
            if st_mode == "Single State Match":
                parts.append(f"{address_prefix}.stateCode == '{st_in.strip().upper()}'")
            else:
                formatted = format_string_utils_args(st_in.upper())
                if formatted:
                    parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({address_prefix}.stateCode, {formatted})")

        # Pincode Matching Logic (Always outputs array braces format)
        if st.checkbox("Enable Destination Pincode Grid Array Constraints", key="matrix_pin"):
            p_in = st.text_area("Enter Pincode Lists:", value="110001, 110002, 400001", help="Separate values with commas. Evaluated as an explicitly bracketed SpEL array string.", key="p_in")
            formatted = format_array_brackets(p_in)
            if formatted:
                pin_target_var = f"{prefix}.saleOrderItems.iterator().next().shippingAddress.pincode" if module == "FACILITY" else f"{address_prefix}.pincode"
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny({pin_target_var}, {formatted})")

        # Country Code Validation
        if st.checkbox("Enable Destination Country Validation", key="matrix_country"):
            co_in = st.text_input("Enter Destination ISO Country Code:", value="IN", max_chars=3, key="co_in")
            parts.append(f"{address_prefix}.countryCode == '{co_in.strip().upper()}'")

        # Physical Shipment Variables (Shipping Module Only Metric)
        if module == "SHIPPING_FWD":
            st.markdown("---")
            st.subheader("⚖️ Physical Logistics Parameters")
            if st.checkbox("Enforce Dead Weight Range Scale Slabs", key="s_weight_slab"):
                min_w = st.number_input("Minimum Package Weight Bound (Grams):", min_value=0, value=0)
                max_w = st.number_input("Maximum Package Weight Bound (Grams):", min_value=0, value=5000)
                parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            if st.checkbox("Enforce Transaction Payment Mode Type", key="s_pay_slab"):
                pay_type = st.selectbox("Select Target Payment Classification Mode:", ["COD", "PREPAID"])
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
            st.error("Validation Error: Please select and configure at least one active structural checkbox parameter above.")
        else:
            # Build unified rule wrapped in standard SpEL container notation format
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
        st.subheader("📋 Complied System Token String (Copy directly to Uniware Rule Editor)")
        st.code(final_output, language="java")
