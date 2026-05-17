import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="centered")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Secure Internal Tokenized Rule Blueprint Generator")

# 1. Module Selector
module = st.selectbox(
    "1. System Rule Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY": "Facility Allocation (Warehouse Routing)",
        "SHIPPING_FWD": "Shipping Provider Allocation (Forward Logistics)",
        "INVENTORY_CALC": "Inventory Update Calculation Formula"
    }[x]
)

# 2. Render Sub-types dynamically
if module == "INVENTORY_CALC":
    sub_type = st.selectbox(
        "2. Formula & Condition Sub-type",
        ["DEFAULT", "BUFFER_3", "BUFFER_1", "ZERO_SYNC"],
        format_func=lambda x: {
            "DEFAULT": "Default Inventory Formula",
            "BUFFER_3": "Safeguard Buffering Rule (<= 3 Syncs 0)",
            "BUFFER_1": "Safeguard Buffering Rule (<= 1 Syncs 0)",
            "ZERO_SYNC": "Force Zero Stock Sync Override"
        }[x]
    )
else:
    sub_type = st.selectbox("2. Formula & Condition Sub-type", ["STANDARD"], format_func=lambda x: "Standard Production Matrix")

st.write("---")
st.write("### 3. Structural Fields to Add")

parts = []

# 3. Handle parameters per module securely
if module == "FACILITY":
    if st.checkbox("Channel Identifier Match (CHANNEL)"):
        parts.append("#saleOrder.channel.code == 'CHANNEL'")
    if st.checkbox("Live Available Inventory Snapshot"):
        parts.append("#allocationCriteria.hasInventory()")
    if st.checkbox("Short Term Operational Inventory Check"):
        parts.append("#allocationCriteria.hasShortTermInventory()")
    if st.checkbox("Complete Short Term Stock Check"):
        parts.append("#allocationCriteria.hasCompleteShortTermInventory()")
    if st.checkbox("State Restriction Rule (STATE)"):
        parts.append("#saleOrderItem.shippingAddress.stateCode == 'STATE'")
    if st.checkbox("Multi-Pincode Parsing Array (PINCODES)"):
        parts.append("T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode, PINCODES)")

elif module == "SHIPPING_FWD":
    if st.checkbox("Channel Flow Route (CHANNEL)"):
        parts.append("#shippingPackage.saleOrder.channel.code.toUpperCase() == 'CHANNEL'")
    if st.checkbox("Weight Metric Range Boundaries"):
        parts.append("#shippingPackage.actualWeight > MIN_WEIGHT and #shippingPackage.actualWeight < MAX_WEIGHT")
    if st.checkbox("Strict COD Payment Method Condition"):
        parts.append("#shippingPackage.saleOrder.paymentMethod.code == 'COD'")
    if st.checkbox("Strict Prepaid Payment Method Condition"):
        parts.append("#shippingPackage.saleOrder.paymentMethod.code == 'PREPAID'")

elif module == "INVENTORY_CALC":
    v_inv = st.checkbox("Add Virtual Inventory Multiplier")
    v_nd = st.checkbox("Add Vendor Catalog Inventory Pool")
    unproc = st.checkbox("Add Unprocessed Order Inventory Count (Amazon Flex)")

# 4. Compiler logic Execution
if st.button("Generate Formula Code", type="primary"):
    final_output = ""
    
    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Please select at least one structural field variable.")
        else:
            final_output = "#{\n  " + " and \n  ".join(parts) + "\n}"
            
    elif module == "INVENTORY_CALC":
        inv_part = "#inventorySnapshot.inventory"
        if v_inv: inv_part += " + #inventorySnapshot.virtualInventory"
        if v_nd:  inv_part += " + #inventorySnapshot.vendorInventory"
        
        deduct_part = "- #inventorySnapshot.openSale - #pendency - (#failedOrderInventory?:0) - #inventoryBlockedOnOtherChannels - #inventorySnapshot.pendingInventoryAssessment"
        if unproc: deduct_part += " + #unprocessedOrderInventory"
        
        core_expr = f"{inv_part} {deduct_part}"
        
        if sub_type == "DEFAULT":
            final_output = f"#{{{core_expr}}}"
        elif sub_type == "BUFFER_3":
            final_output = f"#{{({core_expr})<=3?0:({core_expr})}}"
        elif sub_type == "BUFFER_1":
            final_output = f"#{{({core_expr})<=1?0:({core_expr})}}"
        elif sub_type == "ZERO_SYNC":
            final_output = f"#{{({core_expr})*0}}"

    if final_output:
        st.subheader("Production Target Token String")
        st.code(final_output, language="java")
