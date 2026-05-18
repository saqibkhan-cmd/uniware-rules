import streamlit as st

st.set_page_config(page_title="UniCommerce Production Engine Suite", layout="wide")

st.title("⚡ UniCommerce Production Engine Suite")
st.caption("Advanced Operational Tokenized Rule Matrix Builder")

# 1. Module Selector
module = st.selectbox(
    "1. System Rule Module",
    ["FACILITY", "SHIPPING_FWD", "INVENTORY_CALC"],
    format_func=lambda x: {
        "FACILITY": "Facility Allocation Matrix (Warehouse Routing Rules)",
        "SHIPPING_FWD": "Shipping Provider Allocation (Forward Logistics Rules)",
        "INVENTORY_CALC": "Inventory Update Calculation Formula"
    }[x]
)

# 2. Render Sub-types dynamically based on selection
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
    sub_type = st.selectbox(
        "2. Formula & Condition Sub-type", 
        ["STANDARD_COMBINATIONS"], 
        format_func=lambda x: "Custom Multi-Parameter Condition Combinator"
    )

st.write("---")
st.write("### 3. Structural Parameters & Matrix Values")

parts = []

# --- MULTI-PARAMETER INJECTION ENGINE ---
if module == "FACILITY":
    col1, col2 = st.columns(2)
    
    with col1:
        if st.checkbox("Channel Based Match", key="f_chan_b"):
            chan_val = st.text_input("Target Channel Code:", value="AMAZON_IN", key="f_chan_val").strip().upper()
            parts.append(f"#saleOrder.channel.code == '{chan_val}'")
            
        if st.checkbox("SKU / Product Based Match", key="f_sku_b"):
            sku_val = st.text_input("Target SKU Code:", value="SKU-XYZ", key="f_sku_val").strip()
            parts.append(f"#saleOrderItem.itemSkuCode == '{sku_val}'")
            
        if st.checkbox("State / Location Based Match", key="f_state_b"):
            state_val = st.text_input("Target State Code (2 Letters):", value="DL", key="f_state_val").strip().upper()
            parts.append(f"#saleOrderItem.shippingAddress.stateCode == '{state_val}'")

        if st.checkbox("Pincode / Location Array Match", key="f_pin_b"):
            pin_input = st.text_area("Enter Pincodes (separated by commas):", value="110001, 110002, 400001", key="f_pin_val")
            parsed_pins = ", ".join([f"'{p.strip()}'" for p in pin_input.split(",") if p.strip()])
            if parsed_pins:
                parts.append(f"T(com.unifier.core.utils.StringUtils).equalsAny(#saleOrder.saleOrderItems.iterator().next().shippingAddress.pincode, {{{parsed_pins}}})")

    with col2:
        if st.checkbox("Order Type Based Match", key="f_otype_b"):
            otype_val = st.text_input("Order Type (e.g., NORMAL, B2B):", value="NORMAL", key="f_otype_val").strip().upper()
            parts.append(f"#saleOrder.deliveryType == '{otype_val}'")

        if st.checkbox("Payment Method Based Match", key="f_pay_b"):
            pay_val = st.selectbox("Payment Mode Status:", ["COD", "PREPAID"], key="f_pay_val")
            parts.append(f"#saleOrder.paymentMethod.code == '{pay_val}'")
            
        if st.checkbox("Priority Based Match", key="f_prior_b"):
            prior_val = st.number_input("Minimum Rule Priority Level:", min_value=1, max_value=10, value=1, key="f_prior_val")
            parts.append(f"#saleOrder.priority == {prior_val}")

        if st.checkbox("Time / Date Window Cut-off Basis", key="f_time_b"):
            time_val = st.slider("Target Dispatch Processing Hour Cutoff:", 0, 23, 18, key="f_time_val")
            parts.append(f"T(java.util.Calendar).getInstance().get(T(java.util.Calendar).HOUR_OF_DAY) <= {time_val}")
            
        if st.checkbox("Courier / Shipping Provider Match", key="f_ship_b"):
            ship_val = st.text_input("Courier Code Binding:", value="DELHIVERY", key="f_ship_val").strip().upper()
            parts.append(f"#saleOrder.shippingMethod == '{ship_val}'")

elif module == "SHIPPING_FWD":
    col1, col2 = st.columns(2)
    
    with col1:
        if st.checkbox("Channel Based Route Match", key="s_chan_b"):
            chan_val = st.text_input("Target Channel Code:", value="ECOM", key="s_chan_val").strip().upper()
            parts.append(f"#shippingPackage.saleOrder.channel.code.toUpperCase() == '{chan_val}'")
            
        if st.checkbox("SKU / Product Based Match", key="s_sku_b"):
            sku_val = st.text_input("Target SKU Code:", value="SKU-XYZ", key="s_sku_val").strip()
            # Shipping looks up item code parameters at the pack item layout level
            parts.append(f"#shippingPackage.shippingPackageItems[0].channelItemCode == '{sku_val}'")

        if st.checkbox("Weight Metric Range Boundaries", key="s_weight_b"):
            min_w = st.number_input("Min Weight (Grams):", min_value=0, value=500, key="s_min_w")
            max_w = st.number_input("Max Weight (Grams):", min_value=0, value=50000, key="s_max_w")
            parts.append(f"#shippingPackage.actualWeight > {min_w} and #shippingPackage.actualWeight < {max_w}")
            
        if st.checkbox("State / Location Based Match", key="s_state_b"):
            state_val = st.text_input("Target State Code (2 Letters):", value="DL", key="s_state_val").strip().upper()
            parts.append(f"#shippingPackage.saleOrder.saleOrderItems.iterator().next().shippingAddress.stateCode == '{state_val}'")

    with col2:
        if st.checkbox("Order Type Based Match", key="s_otype_b"):
            otype_val = st.text_input("Order Type Parameter:", value="NORMAL", key="s_otype_val").strip().upper()
            parts.append(f"#shippingPackage.saleOrder.deliveryType == '{otype_val}'")

        if st.checkbox("Payment Method Based Match", key="s_pay_b"):
            pay_val = st.selectbox("Payment Mode Code:", ["COD", "PREPAID"], key="s_pay_val")
            parts.append(f"#shippingPackage.saleOrder.paymentMethod.code == '{pay_val}'")
            
        if st.checkbox("Priority Level Match", key="s_prior_b"):
            prior_val = st.number_input("Minimum Rule Priority Level:", min_value=1, max_value=10, value=1, key="s_prior_val")
            parts.append(f"#shippingPackage.saleOrder.priority == {prior_val}")

        if st.checkbox("Time / Date Processing Window Lock", key="s_time_b"):
            time_val = st.slider("Processing Cut-off Hour:", 0, 23, 15, key="s_time_val")
            parts.append(f"T(java.util.Calendar).getInstance().get(T(java.util.Calendar).HOUR_OF_DAY) <= {time_val}")

elif module == "INVENTORY_CALC":
    v_inv = st.checkbox("Add Virtual Inventory Multiplier", key="calc_virt_inv")
    v_nd = st.checkbox("Add Vendor Catalog Inventory Pool", key="calc_vend_inv")
    unproc = st.checkbox("Add Unprocessed Order Inventory Count (Amazon Flex)", key="calc_unproc_inv")

st.write("")

# 4. Compiler Execution Engine
if st.button("Generate Centralized Formula Code", type="primary"):
    final_output = ""
    
    if module in ["FACILITY", "SHIPPING_FWD"]:
        if not parts:
            st.error("Please configure and check at least one basis parameter combination above.")
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
        st.subheader("📋 Output Syntax Blueprint (Copy directly into Uniware)")
        st.code(final_output, language="java")
