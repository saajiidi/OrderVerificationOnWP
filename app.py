import streamlit as st
import pandas as pd
from whatsapp_order_processor_perfected import WhatsAppOrderProcessor
import io

# Page Configuration
st.set_page_config(
    page_title="WhatsApp Order Verification",
    page_icon="📱",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #25D366;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #128C7E;
        color: white;
    }
    .instruction-text {
        font-size: 1.1rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">WhatsApp Order Processor</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="instruction-text">
        Upload your order Excel file to generate WhatsApp verification links.
        The tool will:
        <ul>
            <li>Clean phone numbers</li>
            <li>Format customer names and addresses</li>
            <li>Group multiple orders by phone number</li>
            <li>Generate a clickable WhatsApp link with a pre-filled verification message</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # improved file uploader
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        try:
            # Read the file
            df = pd.read_excel(uploaded_file)
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Show preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # Column mapping section
            st.subheader("Map Columns")
            st.write("Ensure the correct columns are selected for processing.")
            
            # Column mapping configuration
            column_definitions = {
                'required': {
                    'phone_col': {'default': 'Phone (Billing)', 'keywords': ['phone', 'mobile', 'contact', 'cell']},
                    'name_col': {'default': 'Full Name (Billing)', 'keywords': ['name', 'customer', 'receiver']},
                    'order_id_col': {'default': 'Order ID', 'keywords': ['order id', 'order no', 'invoice', '#']},
                    'product_col': {'default': 'Product Name (main)', 'keywords': ['product', 'item', 'goods']},
                    'quantity_col': {'default': 'Quantity', 'keywords': ['qty', 'quantity', 'count']},
                    'price_col': {'default': 'Order Line Subtotal', 'keywords': ['price', 'subtotal', 'amount', 'rate']},
                    'order_total_col': {'default': 'Order Total Amount', 'keywords': ['total', 'grand total', 'payable', 'amount to pay']},
                    'address_col': {'default': 'Address 1&2 (Billing)', 'keywords': ['address', 'shipping address', 'street', 'location']}
                },
                'optional': {
                    'sku_col': {'default': 'SKU', 'keywords': ['sku', 'code', 'product code']},
                    'payment_method_col': {'default': 'Payment Method Title', 'keywords': ['payment', 'method', 'gateway', 'pay']},
                    'city_col': {'default': 'City, State, Zip (Billing)', 'keywords': ['city', 'town', 'district', 'state']}
                }
            }

            config = {}

            st.markdown("### Required Columns")
            for key, info in column_definitions['required'].items():
                default_col = info['default']
                keywords = info['keywords']
                
                index = 0
                # Priority 1: Exact match
                if default_col in df.columns:
                    index = list(df.columns).index(default_col)
                else:
                    # Priority 2: Keyword match
                    found = False
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(k in col_lower for k in keywords):
                            index = list(df.columns).index(col)
                            found = True
                            break
                
                config[key] = st.selectbox(
                    f"Select column for {key.replace('_col', '').replace('_', ' ').title()} *",
                    options=df.columns,
                    index=index,
                    key=key
                )

            st.markdown("### Optional Columns")
            for key, info in column_definitions['optional'].items():
                default_col = info['default']
                keywords = info['keywords']
                
                options = ["None"] + list(df.columns)
                index = 0
                
                if default_col in df.columns:
                    index = options.index(default_col)
                else:
                    for col in df.columns:
                        col_lower = str(col).lower()
                        if any(k in col_lower for k in keywords):
                            index = options.index(col)
                            break
                            
                selected = st.selectbox(
                    f"Select column for {key.replace('_col', '').replace('_', ' ').title()}",
                    options=options,
                    index=index,
                    key=key
                )
                
                if selected != "None":
                    config[key] = selected
            
            if st.button("Process Orders"):
                with st.spinner("Processing orders..."):
                    # Initialize processor with custom config
                    processor = WhatsAppOrderProcessor(config=config)
                    
                    # Process orders - pass the dataframe directly
                    processed_df = processor.process_orders(df)
                    
                    # Create WhatsApp links
                    final_df = processor.create_whatsapp_links(processed_df)
                    
                    # Generate Excel bytes - Using the new method we added
                    excel_data = processor.generate_excel_bytes(final_df)
                    
                    # Success message
                    st.success(f"Successfully processed {len(final_df)} unique customers!")
                    
                    # Show results preview
                    st.subheader("Processed Data Preview")
                    st.dataframe(final_df.head())
                    
                    # Download button
                    st.download_button(
                        label="Download Processed Excel File",
                        data=excel_data,
                        file_name="processed_orders_whatsapp.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()
