import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Orchestra ROI Engine", layout="wide")
st.title("Orchestra Industrial ROI Engine")

# --- 2. SIDEBAR: FACTORY BLUEPRINT ---
with st.sidebar:
    st.header("🏭 Industry Preset")
    industry = st.selectbox("Industry Type:", ["Textiles (Apparel)", "Electronics (PCBA)", "Mining (Coal)", "Custom"])
    
    # Presets: Rev, Margin, A, P, Q
    presets = {
        "Textiles (Apparel)": (1200000, 18, 80, 60, 85),
        "Electronics (PCBA)": (3500000, 30, 75, 65, 98),
        "Mining (Coal)": (8000000, 45, 60, 75, 99),
        "Custom": (1500000, 25, 80, 70, 95)
    }
    def_rev, def_margin, def_a, def_p, def_q = presets[industry]

    st.header("⚙️ Site Parameters")
    num_lines = st.number_input("Production Lines", value=1, min_value=1)
    rev_line = st.number_input("Annual Revenue per Line ($)", value=def_rev)
    margin = st.slider("Gross Margin (%)", 5, 60, def_margin) / 100
    labor_rate = st.number_input("Labor Cost ($/hr)", value=12.0)
    
    st.header("📉 Current OEE (A-P-Q)")
    a_val = st.slider("Availability (A) %", 10, 100, def_a) / 100
    p_val = st.slider("Performance (P) %", 10, 100, def_p) / 100
    q_val = st.slider("Quality (Q) %", 10, 100, def_q) / 100
    curr_oee = a_val * p_val * q_val
    st.metric("Current Site OEE", f"{curr_oee:.1%}")

    st.header("💰 Investment")
    capex = st.number_input("Initial Setup Cost (CapEx)", value=35000)
    sub_years = st.slider("Analysis Period (Years)", 1, 5, 5)
    annual_opex = capex * 0.20 # 20% maintenance/SaaS fee

# --- 3. DYNAMIC ROI LOGIC ---
st.header("🎯 Strategy & AI Impact")
strategy = st.radio("Select Strategy:", ["Product A: Expert Skill", "Product B: Workflow", "Product C: Risk & Safety"], horizontal=True)

# Shared Calculations
total_rev = rev_line * num_lines
mat_cost = total_rev * (1 - margin)
ideal_pot = total_rev / curr_oee if curr_oee > 0 else 0

st.markdown(f"**Calculated Annual Material Cost:** `${mat_cost:,.0f}`")

col1, col2 = st.columns(2)
with col1:
    if "Product A" in strategy:
        st.write("Focus: Quality (Q) Improvement")
        scrap_save_pct = st.slider("Target Scrap Reduction (%)", 0.0, 15.0, 7.0) / 100
        q_lift = st.slider("Direct OEE Quality Lift (ΔQ) %", 0.0, 10.0, 4.0) / 100
        # Impact A = Scrap savings + Small Throughput Gain from higher Quality
        target_oee = a_val * p_val * min(1.0, q_val + q_lift)
        impact_label, impact_val = "Material Savings", (mat_cost * scrap_save_pct)
        
    elif "Product B" in strategy:
        st.write("Focus: Performance (P) Improvement")
        p_lift = st.slider("Performance Speed Boost (ΔP) %", 0.0, 20.0, 12.0) / 100
        # Impact B = Pure Throughput Gain from faster workflow
        target_oee = a_val * min(1.0, p_val + p_lift) * q_val
        impact_label, impact_val = "Efficiency Gain", 0 # Captured in Throughput Profit
        
    else:
        st.write("Focus: Availability (A) Improvement")
        admin_hours = st.number_input("Safety Admin Hours Saved / Month", value=40)
        a_lift = st.slider("Availability Gain (ΔA) %", 0.0, 10.0, 3.0) / 100
        # Impact C = Admin labor recovery + small uptime gain
        target_oee = min(1.0, a_val + a_lift) * p_val * q_val
        impact_label, impact_val = "Admin Recovery", (admin_hours * 12 * labor_rate)

# --- 4. THE MASTER COMPARISON TABLE ---
st.header("📊 Scenarios & Potential Value")
labels = ["Current", "Fair (35%)", "Good (50%)", "Great (65%)", "World Class (80%)", "ORCHESTRA TARGET"]
targets = [curr_oee, 0.35, 0.50, 0.65, 0.80, target_oee]

results = []
for t in targets:
    # Throughput profit = (Target OEE - Current OEE) * Ideal Potential * Margin
    t_profit = (ideal_pot * (t - curr_oee) * margin) if t > curr_oee else 0
    # Add Product-specific impact only to the Orchestra Target column
    specific_impact = impact_val if t == target_oee else 0
    total_annual = t_profit + specific_impact
    
    results.append({
        "OEE Score": f"{t:.1%}",
        "Throughput Profit Gain": t_profit,
        impact_label: specific_impact,
        "Total Annual Impact": total_annual,
        "Net 5-Year Return": (total_annual - annual_opex) * 5 - capex
    })

df_table = pd.DataFrame(results, index=labels).T
st.table(df_table.applymap(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x))

# --- 5. THE GRAPH ---
st.header("📈 Cumulative Financial Impact (Breakeven Analysis)")
fig = go.Figure()
years = list(range(sub_years + 1))

for i, label in enumerate(labels):
    annual = results[i]["Total Annual Impact"]
    y_vals = [-capex]
    current_total = -capex
    for yr in range(1, sub_years + 1):
        current_total += (annual - annual_opex)
        y_vals.append(current_total)
    
    fig.add_trace(go.Scatter(x=years, y=y_vals, name=label, mode='lines+markers',
                             line=dict(width=4 if "ORCHESTRA" in label else 2)))

fig.add_trace(go.Scatter(x=years, y=[0]*(sub_years+1), name="Breakeven", line=dict(dash='dash', color='black')))
fig.update_layout(template="plotly_white", yaxis_title="Net Profit ($)", xaxis_title="Years Post-Deployment")
st.plotly_chart(fig, use_container_width=True)

st.info(f"💡 **Strategic Insight:** Your 'Orchestra Target' ({target_oee:.1%} OEE) delivers a total annual impact of **${results[5]['Total Annual Impact']:,.0f}**. This covers your initial investment in less than 12 months.")