import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Orchestra ROI Engine", layout="wide")
st.title("Orchestra Industrial ROI Engine")


# --- 2. SIDEBAR: FACTORY BLUEPRINT ---
with st.sidebar:
    st.header("🏭 Industry Preset")
    industry = st.selectbox("Industry Type:", [
        "Textiles (Traditional)", 
        "Electronics (SME)", 
        "Mining (Traditional)", 
        "Custom"
    ])
    
    presets = {
        "Textiles (Traditional)": (800000, 12, 70, 50, 80), # Low margin, high labor waste
        "Electronics (SME)": (2500000, 20, 75, 60, 95),    # Older equipment, frequent stops
        "Mining (Traditional)": (5000000, 35, 55, 65, 98), # High downtime, safety risks
        "Custom": (1500000, 25, 80, 70, 95)
    }
    def_rev, def_margin, def_a, def_p, def_q = presets[industry]

    st.header("⚙️ Site Parameters")
    num_lines = st.number_input("Production Lines", value=2, min_value=1) # Updated to 2
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
    capex = st.number_input("Initial Setup (CapEx) ($)", value=35000, step=5000)
    
    # NEW: Let the user define the recurring cost
    opex_pct = st.slider("Annual Subscription (% of CapEx)", 10, 30, 20) / 100
    annual_opex = capex * opex_pct
    
    sub_years = st.slider("Analysis Period (Years)", 1, 5, 5)
    
    # Visual feedback in the sidebar
    st.write(f"**Recurring Cost:** `${annual_opex:,.0f}/year`")

# --- 3. DYNAMIC ROI LOGIC ---
st.header("🎯 Strategy & AI Impact")
strategy = st.radio("Select Strategy:", ["Product A: Expert Skill", "Product B: Workflow", "Product C: Risk & Safety"], horizontal=True)

total_rev = rev_line * num_lines
mat_cost = total_rev * (1 - margin)
ideal_pot = total_rev / curr_oee if curr_oee > 0 else 0

col1, col2 = st.columns(2)
with col1:
    if "Product A" in strategy:
        st.write("Focus: Quality (Q) Improvement")
        scrap_save_pct = st.slider("Target Scrap Reduction (%)", 0.0, 15.0, 7.0) / 100
        q_lift = st.slider("Direct OEE Quality Lift (ΔQ) %", 0.0, 10.0, 4.0) / 100
        target_oee = a_val * p_val * min(1.0, q_val + q_lift)
        impact_label, impact_val = "Material Savings", (mat_cost * scrap_save_pct)
    elif "Product B" in strategy:
        st.write("Focus: Performance (P) Improvement")
        p_lift = st.slider("Performance Speed Boost (ΔP) %", 0.0, 20.0, 12.0) / 100
        target_oee = a_val * min(1.0, p_val + p_lift) * q_val
        impact_label, impact_val = "Efficiency Gain", 0 
    else:
        st.write("Focus: Availability (A) Improvement")
        admin_hours = st.number_input("Safety Admin Hours Saved / Month", value=40)
        a_lift = st.slider("Availability Gain (ΔA) %", 0.0, 10.0, 3.0) / 100
        target_oee = min(1.0, a_val + a_lift) * p_val * q_val
        impact_label, impact_val = "Admin Recovery", (admin_hours * 12 * labor_rate)

# --- 4. THE MASTER COMPARISON TABLE (WITH HIGHLIGHTING & REALITY-ADJUSTED MATH) ---
st.header("📊 Financial Impact Analysis")

# NEW: The "CFO Buffer" (Assume factory only captures 70% of theoretical gains)
realization_factor = 0.70 

# Labels and Targets
labels = ["Fair (35%)", "Good (50%)", "Great (65%)", "World Class (80%)", "ORCHESTRA TARGET"]
targets = [0.35, 0.50, 0.65, 0.80, target_oee]

results_data = []
for t in targets:
    # 1. Throughput Profit (Only if target > current)
    t_profit = (ideal_pot * (t - curr_oee) * margin) if t > curr_oee else 0
    
    # 2. Orchestra Specific Impact (Material Savings/Admin)
    specific_impact = impact_val if t == target_oee else 0
    
    # NEW: Apply the Realization Factor to the total annual gain
    # This turns the "Theoretical" money into "Realized" money
    total_annual = (t_profit + specific_impact) * realization_factor
    
    # 3. Final Total Return (Accumulated over the Analysis Period)
    net_total_return = (total_annual - annual_opex) * sub_years - capex
    
    results_data.append({
        "OEE Score": f"{t:.1%}",
        "Realized Annual Value": total_annual, # The buffered amount
        "Annual OpEx (Sub)": -annual_opex,
        f"Net {sub_years}-Year Total Return": net_total_return,
        "annual_impact": total_annual # Keeps the graph in sync with the table
    })

# Create DataFrame
df_table = pd.DataFrame(results_data, index=labels).T

# --- HIGHLIGHT LOGIC ---
def highlight_orchestra(s):
    # Apply a light purple background to the 'ORCHESTRA TARGET' column
    return ['background-color: #f3e5f5; font-weight: bold; color: #7D3CFF' if s.name == 'ORCHESTRA TARGET' else '' for _ in s]

# Format and Display the Styled Table
styled_df = df_table.style.apply(highlight_orchestra, axis=0).format(
    lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x
)
st.table(styled_df)

st.caption(f"⚠️ **Note:** Results adjusted by a {int((1-realization_factor)*100)}% realization buffer to account for operational slack.")

# --- 5. THE GRAPH (CUMULATIVE CASH FLOW) ---
st.header(f"📈 Cumulative Cash Flow ({sub_years}-Year Outlook)")

fig = go.Figure()
years_range = list(range(sub_years + 1))

for i, label in enumerate(labels):
    annual_gain = results_data[i]["annual_impact"]
    
    # Year 0: Always start at negative CapEx (The initial "Hole")
    y_vals = [-capex] 
    cumulative_cash = -capex
    
    for yr in range(1, sub_years + 1):
        # Every year: Cash increases by (Annual Value - Subscription)
        cumulative_cash += (annual_gain - annual_opex)
        y_vals.append(cumulative_cash)
    
    is_target = "ORCHESTRA" in label
    
    fig.add_trace(go.Scatter(
        x=years_range, 
        y=y_vals, 
        name=label,
        mode='lines+markers',
        line=dict(
            width=6 if is_target else 2, 
            color="#7D3CFF" if is_target else None 
        ),
        marker=dict(size=10 if is_target else 6)
    ))

# Breakeven Line (0) - Where the client starts "Printing Money"
fig.add_trace(go.Scatter(
    x=years_range, y=[0]*(sub_years+1), 
    name="Breakeven", 
    line=dict(dash='dash', color='black', width=2)
))

fig.update_layout(
    template="plotly_white", 
    yaxis_title="Net Cash Position ($)", 
    xaxis_title="Years Post-Deployment",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# --- 6. EXECUTIVE STRATEGIC SUMMARY (DATA-DRIVEN) ---
st.divider()
st.subheader("📊 Investment Summary")

# Calculations for the summary
total_net_return = results_data[-1][f"Net {sub_years}-Year Total Return"]
annual_realized = results_data[-1]["annual_impact"]
payback_months = (capex / (annual_realized / 12)) if annual_realized > 0 else 0
tco = capex + (annual_opex * sub_years)

col_a, col_b, col_c = st.columns(3)
with col_a:
    color = "normal" if total_net_return > 0 else "inverse"
    st.metric("Net Financial Position", f"${total_net_return:,.0f}", delta=f"{total_net_return:,.0f}", delta_color=color)
with col_b:
    # If payback is longer than the analysis period, show 'Outside Period'
    payback_text = f"{payback_months:.1f} Months" if payback_months <= (sub_years * 12) else "Exceeds Analysis Period"
    st.metric("Breakeven Estimate", payback_text)
with col_c:
    roi_pct = (total_net_return / tco) * 100
    st.metric("Return on Investment", f"{roi_pct:.1f}%")

# Neutral Strategy Box
with st.expander("📝 Strategic Context", expanded=True):
    if total_net_return > 0:
        st.write(f"""
        **Performance Outlook:** The deployment of **{strategy}** is projected to be profitable within this {sub_years}-year window. 
        The primary value driver is **{impact_label}**, contributing approximately **${impact_val * realization_factor:,.0f}** to the annual realized gains.
        """)
    else:
        st.error("⚠️ **Investment Advisory**")
        # Using a backslash \$ to prevent LaTeX math errors
        st.markdown(f"The annual realized gains of **\${annual_realized:,.0f}** do not cover the Total Cost of Ownership of **\${tco:,.0f}** within the {sub_years}-year window.")

        st.markdown(f"""
        **To achieve a positive ROI, Steve should suggest:**
        * **Scale Up:** Increase the number of **Production Lines** (current: {num_lines}).
        * **Switch Focus:** Use a higher-impact strategy like **Product A (Quality/Scrap)**.
        * **Optimize Costs:** Reduce the **Initial Setup (CapEx)** below **${annual_realized * sub_years:,.0f}**.
        """)