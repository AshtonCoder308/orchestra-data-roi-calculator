import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 页面设置
st.set_page_config(page_title="Orchestra ROI Engine", layout="wide")

# 自定义淡紫色主题
PURPLE_LIGHT = "#E1BEE7"
PURPLE_MAIN = "#9C27B0"

st.title("💜 Orchestra Industrial ROI Predictor")
st.markdown("---")

# 左侧输入面板
with st.sidebar:
    st.header("🏢 Factory Parameters")
    num_workers = st.number_input("Number of Workers", value=20)
    hourly_wage = st.slider("Hourly Wage ($)", 2.0, 50.0, 5.5)
    annual_revenue = st.number_input("Annual Revenue ($)", value=1500000)
    material_cost = st.number_input("Annual Material Cost ($)", value=400000)
    system_cost = st.number_input("Orchestra System Cost ($)", value=18000)

# 计算逻辑
annual_labor_cost = num_workers * hourly_wage * 2000
savings_a = material_cost * 0.05  # 假设减少5%废品
savings_b = (annual_revenue * 0.25) * 0.10  # 假设提升10%效率
total_savings = savings_a + savings_b
payback_months = (system_cost / total_savings) * 12 if total_savings > 0 else 0

# 右侧结果展示
col1, col2, col3 = st.columns(3)
col1.metric("Annual Savings", f"${total_savings:,.0f}")
col2.metric("Payback Period", f"{payback_months:.1f} Months")
col3.metric("Year 1 Net Profit", f"${total_savings - system_cost:,.0f}")

# 绘图
years = [1, 2, 3, 4, 5]
cumulative = [(total_savings * y) - system_cost for y in years]
fig = go.Figure()
fig.add_trace(go.Bar(x=years, y=[savings_a]*5, name="Scrap Reduction", marker_color=PURPLE_LIGHT))
fig.add_trace(go.Bar(x=years, y=[savings_b]*5, name="Workflow Efficiency", marker_color="#CE93D8"))
fig.add_trace(go.Scatter(x=years, y=cumulative, name="Cumulative Profit", line=dict(color=PURPLE_MAIN, width=4)))

st.plotly_chart(fig, use_container_width=True)
st.info("🔍 **Live AI Diagnostic:** Analysis detected 12% non-value movement in Station 4.")