import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="CZ-NoN Engagement Matrix", layout="wide")

# Constants & Colors
METRIC_COLORS = {
    'Reads': '#FF6719',    # Substack Orange
    'Clicks': '#10B981',   # Green
    'Views': '#3B82F6',    # Blue
    'Followers': '#8B5CF6' # Purple
}
# Weighted Logic
WEIGHTS = {'monthly reads': 1, 'total clicks': 2, 'total views': 0.1}

# 2. Custom Styling
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #f0f2f6; }
    .weight-legend { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 5px solid #1E3A8A; font-size: 0.85em; }
    h3 { font-size: 1.1rem !important; margin-bottom: 0.5rem !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data Processing
@st.cache_data
def load_and_clean_data():
    df_raw = pd.read_csv('CZ NoN Metrics - Sheet1.csv')
    results = []
    
    # Block 1: 2025 Data
    cols_25 = [c for c in df_raw.columns if '2025' in str(c)]
    current_platform = None
    for idx in range(1, 9):
        row = df_raw.iloc[idx]
        label = str(row.iloc[0]).strip()
        if label in ['Bluesky', 'Substack', 'Bitly']: current_platform = label; continue
        if label == 'nan' or not label: continue
        for col in cols_25:
            val = row[col]
            if pd.notna(val):
                clean_val = str(val).replace(',', '')
                results.append({'Date': col, 'Platform': current_platform, 'Metric': label, 'Value': float(clean_val)})

    # Block 2: 2026 Data
    current_platform = None
    cols_26 = [str(c) for c in df_raw.iloc[9].values[1:] if str(c) != 'nan']
    for idx in range(11, len(df_raw)):
        row = df_raw.iloc[idx]
        label = str(row.iloc[0]).strip()
        if label in ['Bluesky', 'Substack', 'Bitly']: current_platform = label; continue
        if label == 'nan' or not label: continue
        for i, date_label in enumerate(cols_26):
            val = row.iloc[i+1]
            if pd.notna(val):
                clean_val = str(val).replace(',', '')
                results.append({'Date': date_label, 'Platform': current_platform, 'Metric': label, 'Value': float(clean_val)})
    
    df = pd.DataFrame(results)
    df['Date'] = pd.to_datetime(df['Date'], format='%Y %m')
    return df

try:
    df_clean = load_and_clean_data()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# 4. Sidebar: Control Panel
st.sidebar.title("📊 Control Panel")
st.sidebar.markdown("### 🔑 Calculation Logic")
legend_html = "<div class='weight-legend'>"
for m, w in WEIGHTS.items():
    legend_html += f"<strong>{m.title()}:</strong> {w} Engagement Points<br>"
legend_html += "</div>"
st.sidebar.markdown(legend_html, unsafe_allow_html=True)

st.sidebar.markdown("---")
min_date, max_date = df_clean['Date'].min(), df_clean['Date'].max()
date_range = st.sidebar.date_input("Timeframe", [min_date, max_date])

# Filtering
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_f = df_clean[(df_clean['Date'] >= start) & (df_clean['Date'] <= end)].copy()
else:
    df_f = df_clean.copy()

# Score Calculation
df_f['Points'] = df_f.apply(lambda r: r['Value'] * WEIGHTS.get(r['Metric'], 0), axis=1)

# 5. Header & Primary KPIs (Updated Order)
st.title("🛰️ CZ-NoN engagement matrix")
st.markdown(f"[🦋 Bluesky](https://bsky.app/profile/cznews.bsky.social)  •  [✉️ Substack](https://criticalzonenews.substack.com/)")

# KPI Calculations
bs_followers = df_f[df_f['Metric'] == 'followers']['Value'].iloc[-1] if not df_f.empty else 0
total_reads = df_f[df_f['Metric'] == 'monthly reads']['Value'].sum()
bitly_clicks = df_f[df_f['Metric'] == 'total clicks']['Value'].sum()
avg_subs_pts = df_f[df_f['Platform'] == 'Substack'].groupby('Date')['Points'].sum().mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Bluesky Followers", f"{bs_followers:,.0f}")
k2.metric("Substack Total Reads", f"{total_reads:,.0f}")
k3.metric("Bitly Clicks", f"{bitly_clicks:,.0f}")
k4.metric("Avg Substack Engagement Points", f"{avg_subs_pts:.1f}")

st.markdown("---")

# 6. Detailed Engagement Trend
st.header("📈 Monthly Weighted Engagement Details")

# Aggregate Points and include Monthly Reads/Clicks for hover detail
agg_trend = df_f.groupby('Date').agg({
    'Points': 'sum',
    'Value': lambda x: x[df_f.loc[x.index, 'Metric'] == 'monthly reads'].sum()
}).reset_index().rename(columns={'Value': 'Raw Reads'})

fig_trend = px.line(agg_trend, x='Date', y='Points', 
                    title="Total Engagement Points (Weighted)",
                    markers=True, 
                    line_shape='spline',
                    hover_data={'Date': '|%b %Y', 'Points': ':.2f', 'Raw Reads': ':,.0f'})

fig_trend.update_traces(line_color='#1E293B', line_width=4, marker=dict(size=10, color='#1E293B'))
fig_trend.update_layout(
    xaxis_title="Month",
    yaxis_title="Total Engagement Points",
    hovermode="x unified"
)
st.plotly_chart(fig_trend, use_container_width=True)

# 7. Platform Specifics
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🦋 Bluesky Growth")
    bs_data = df_f[df_f['Platform'] == 'Bluesky']
    fig_bs = px.area(bs_data, x='Date', y='Value', title="Cumulative Follower Growth",
                    color_discrete_sequence=[METRIC_COLORS['Followers']])
    st.plotly_chart(fig_bs, use_container_width=True)

with col_right:
    st.subheader("✉️ Substack Interaction")
    ss_data = df_f[df_f['Platform'] == 'Substack']
    ss_pivot = ss_data.pivot(index='Date', columns='Metric', values='Value').reset_index()
    
    fig_ss = go.Figure()
    fig_ss.add_trace(go.Bar(x=ss_pivot['Date'], y=ss_pivot['total views'], name='Views', marker_color=METRIC_COLORS['Views']))
    fig_ss.add_trace(go.Bar(x=ss_pivot['Date'], y=ss_pivot['monthly reads'], name='Reads', marker_color=METRIC_COLORS['Reads']))
    fig_ss.update_layout(barmode='group', title="Views vs. Actual Reads")
    st.plotly_chart(fig_ss, use_container_width=True)
