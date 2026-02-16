import streamlit as st
import pandas as pd
from processor import WhatsAppOrderProcessor  # Updated import

# Configuration
st.set_page_config(
    page_title="WhatsApp Order Verification",
    page_icon="✅",
    layout="wide"
)

# Custom Styles
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #25D366;
        color: white;
        width: 100%;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #128C7E;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">WhatsApp Order Verification</h1>', unsafe_allow_html=True)
    
    with st.expander("ℹ️ How to use", expanded=False):
        st.markdown("""
        1. **Upload** your order Excel file.
        2. **Map Columns** if not automatically detected.
        3. **Process** to generate verification links.
        4. **Download** the result.
        """)
    
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
    
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(col).strip() for col in df.columns]
            
            # Data Preview
            st.caption("Data Preview (First 3 rows)")
            st.dataframe(df.head(3), height=150)
            
            st.subheader("⚙️ Column Mapping")
            
            # Intelligent Defaults
            mapping = {
                'required': {
                    'phone_col': ['phone (billing)', 'mobile', 'contact', 'cell', 'phone'],
                    'name_col': ['full name (billing)', 'customer name', 'receiver', 'full name', 'name'],
                    'order_id_col': ['order id', 'order no', 'invoice', '#'],
                    'product_col': ['product name (main)', 'product', 'item', 'goods'],
                    'quantity_col': ['quantity', 'qty', 'count'],
                    'price_col': ['item cost', 'order line subtotal', 'price', 'amount', 'rate', 'cost'],
                    'order_total_col': ['order total amount', 'total', 'payable', 'amount to pay'],
                },
                'optional': {
                    'address_col': ['address 1&2 (billing)', 'address', 'shipping', 'street'],
                    'sku_col': ['sku', 'code'],
                    'payment_method_col': ['payment method title', 'payment', 'method', 'gateway'],
                    'city_col': ['city, state, zip (billing)', 'city', 'town', 'district']
                }
            }

            config = {}
            
            # Helper to find column index
            def find_index(options, keywords):
                for i, col in enumerate(options):
                    if any(k in col.lower() for k in keywords):
                        return i
                return 0

            # 2-Column Layout for Mapping
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Required Fields")
                for key, keywords in mapping['required'].items():
                    idx = find_index(df.columns, keywords)
                    config[key] = st.selectbox(
                        f"{key.replace('_col', '').replace('_', ' ').title()} *",
                        options=df.columns,
                        index=idx,
                        key=key
                    )
            
            with col2:
                st.markdown("##### Optional Fields")
                opts = ["None"] + list(df.columns)
                for key, keywords in mapping['optional'].items():
                    idx = find_index(opts, keywords)
                    val = st.selectbox(
                        f"{key.replace('_col', '').replace('_', ' ').title()}",
                        options=opts,
                        index=idx,
                        key=key
                    )
                    if val != "None":
                        config[key] = val

            st.write("") # Spacer
            
            if st.button("🚀 Process Orders"):
                with st.spinner("Generating WhatsApp links..."):
                    processor = WhatsAppOrderProcessor(config=config)
                    # Process
                    processed_df = processor.process_orders(df) # First aggregation
                    final_df = processor.create_whatsapp_links(processed_df) # Link generation
                    excel_data = processor.generate_excel_bytes(final_df) # Export
                    
                    st.success(f"✅ Processed {len(final_df)} orders!")
                    
                    col_d1, col_d2 = st.columns([2, 1])
                    with col_d1:
                        st.download_button(
                            label="📥 Download Result",
                            data=excel_data,
                            file_name="whatsapp_orders.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
