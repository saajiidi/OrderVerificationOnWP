import streamlit as st
import pandas as pd

def render_woocommerce_orders_tab():
    """Renders the WooCommerce Orders list module."""
    st.markdown("<h2 style='color: #6366f1;'>🛒 WooCommerce Orders List</h2>", unsafe_allow_html=True)
    st.markdown("<p style='opacity: 0.8;'>Live synchronization view of your current WooCommerce operations.</p>", unsafe_allow_html=True)
    st.divider()

    # Fetch the WooCommerce Dataframe from session state
    df = st.session_state.get("wc_curr_df")

    if df is None or df.empty:
        st.warning("⚠️ No active WooCommerce order data found. Please trigger a sync from the **Live Dashboard** first.")
        return

    # Advanced Multi-Column Filter Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Order Filters")
        
        # Search Filter
        search_query = st.text_input("🔍 Global Search:", help="Search by Name, Phone, ID, etc.")
        
        # Status Filter
        status_filter = []
        if "Status" in df.columns:
            statuses = df["Status"].dropna().unique().tolist()
            status_filter = st.multiselect("Status:", statuses, default=statuses)

        # Total Amount Range Filter
        amount_filter = None
        if "Total Amount" in df.columns:
            min_amt = float(df["Total Amount"].min())
            max_amt = float(df["Total Amount"].max())
            if min_amt < max_amt:
                amount_filter = st.slider("Total Amount Range:", min_value=min_amt, max_value=max_amt, value=(min_amt, max_amt))

    display_df = df.copy()

    # Apply Filters
    if search_query:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        
    if status_filter and "Status" in display_df.columns:
        display_df = display_df[display_df["Status"].isin(status_filter)]
        
    if amount_filter and "Total Amount" in display_df.columns:
        display_df = display_df[(display_df["Total Amount"] >= amount_filter[0]) & (display_df["Total Amount"] <= amount_filter[1])]

    # Top-level operational metrics
    total_orders = len(display_df)
    total_revenue = display_df["Total Amount"].sum() if "Total Amount" in display_df.columns else 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Filtered Orders", total_orders)
    c2.metric("Filtered Revenue", f"৳{total_revenue:,.0f}")
    
    if "Status" in display_df.columns:
        processing = len(display_df[display_df["Status"].astype(str).str.lower() == "processing"])
        c3.metric("Processing Orders", processing)
        completed = len(display_df[display_df["Status"].astype(str).str.lower() == "completed"])
        c4.metric("Completed Orders", completed)

    st.markdown("### 📋 Raw Order Data")
    
    # Configure specific column formats
    column_configuration = {}
    if "Date" in display_df.columns:
        display_df["Date"] = pd.to_datetime(display_df["Date"], errors='coerce')
        column_configuration["Date"] = st.column_config.DatetimeColumn(
            "Order Date",
            format="D MMM YYYY, h:mm a",
        )
        
    if "Total Amount" in display_df.columns:
        column_configuration["Total Amount"] = st.column_config.NumberColumn(
            "Total Amount",
            help="Total order amount in BDT",
            format="৳ %.2f",
        )

    st.dataframe(
        display_df, 
        use_container_width=True, 
        height=600,
        column_config=column_configuration
    )