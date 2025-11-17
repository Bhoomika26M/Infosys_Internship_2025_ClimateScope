import streamlit as st

def render_sidebar_filters(df):
    st.sidebar.title("🌍 ClimateScope")
    st.sidebar.markdown("### Global Climate Analysis Platform")
    st.sidebar.markdown("---")
    
    st.sidebar.header("Filters")
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range
    
    all_countries = sorted(df['Country'].unique())
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=all_countries[:10] if 'selected_countries' not in st.session_state else st.session_state.get('selected_countries', all_countries[:10])
    )
    
    if not selected_countries:
        selected_countries = all_countries
    
    st.session_state['selected_countries'] = selected_countries
    
    filtered_df = df[
        (df['Date'].dt.date >= start_date) & 
        (df['Date'].dt.date <= end_date) & 
        (df['Country'].isin(selected_countries))
    ].copy()
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"**Records:** {len(filtered_df):,}")
    st.sidebar.info(f"**Countries:** {len(selected_countries)}")
    
    return filtered_df
