import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import generate_synthetic_data
from simulation import calculate_impact

# 페이지 설정
st.set_page_config(
    page_title="공급망 디지털 트윈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 헤더
st.title("🏭 디지털 트윈: 공급망 리스크 분석")
st.markdown("### 제조 분야 의사결정 지원 시스템 (DSS)")

# 데이터 로드
@st.cache_data
def get_data():
    return generate_synthetic_data()

data_frames = get_data()
df_suppliers = data_frames['suppliers']
df_parts = data_frames['parts']
df_production = data_frames['production']

# 사이드바 - What-If 시나리오
st.sidebar.header("🎛️ What-If 시나리오 시뮬레이션")
st.sidebar.markdown("변수를 조절하여 공급망 예상 리스크를 시뮬레이션하세요.")

price_increase = st.sidebar.slider(
    "원자재 단가 상승률 (%)",
    min_value=0.0,
    max_value=50.0,
    value=0.0,
    step=1.0,
    help="전 세계적인 원자재 가격 상승을 시뮬레이션합니다."
)

supplier_delay = st.sidebar.slider(
    "공급사 납품 지연 (일수)",
    min_value=0,
    max_value=30,
    value=0,
    step=1,
    help="1차 협력업체의 배송 지연을 시뮬레이션합니다."
)

# 시뮬레이션 실행
impact = calculate_impact(
    data_frames, 
    price_increase_pct=price_increase, 
    delay_days=supplier_delay
)

# 핵심 지표 (KPI Monitor)
st.markdown("---")
st.subheader("📊 경영진 요약 (Executive Summary)")

col1, col2, col3 = st.columns(3)

# 1. 영업 이익
profit_delta = impact['delta']['profit_change']
profit_current = impact['after']['operating_profit']
profit_before = impact['before']['operating_profit']

col1.metric(
    label="월간 영업이익 (Operating Profit)",
    value=f"${profit_current:,.0f}",
    delta=f"{profit_delta:,.0f}",
    delta_color="normal" # 수익 감소는 빨간색으로 표시됨 (음수일 경우)
)

# 2. 생산량
prod_current = impact['after']['production_units']
prod_loss = impact['delta']['production_loss']
prod_delta = -prod_loss # 손실은 음수로 표시

col2.metric(
    label="생산량 (Production Output)",
    value=f"{prod_current:,.0f} units",
    delta=f"{prod_delta:,.0f}",
    delta_color="normal"
)

# 3. 리스크 레벨 (파생 지표)
risk_status = "낮음 (Low)"
risk_color = "green"
if supplier_delay > 5:
    risk_status = "주의 (Medium)"
    risk_color = "orange"
if supplier_delay > 15 or (profit_before != 0 and profit_delta / profit_before < -0.2):
    risk_status = "위험 (High)"
    risk_color = "red"

col3.markdown(f"**리스크 레벨 (Risk Level)**")
col3.markdown(f"<h2 style='color: {risk_color};'>{risk_status}</h2>", unsafe_allow_html=True)


# 상세 분석 차트
st.markdown("---")
col_chart_1, col_chart_2 = st.columns(2)

with col_chart_1:
    st.subheader("📉 영업이익 영향도 분석")
    # Bar chart comparing Before vs After
    impact_df = pd.DataFrame({
        '시나리오': ['기존 (Baseline)', '시뮬레이션 (Simulated)'],
        '영업이익': [impact['before']['operating_profit'], impact['after']['operating_profit']]
    })
    fig_profit = px.bar(
        impact_df, 
        x='시나리오', 
        y='영업이익', 
        color='시나리오',
        color_discrete_map={'기존 (Baseline)': 'lightgrey', '시뮬레이션 (Simulated)': '#FF4B4B' if profit_delta < 0 else '#00CC96'},
        text_auto='.2s',
        title="시나리오별 예상 영업이익 비교"
    )
    st.plotly_chart(fig_profit, use_container_width=True)

with col_chart_2:
    st.subheader("📦 재고 및 생산 예측")
    # If delay exists, show linear drop
    days = list(range(1, 31))
    
    daily_prod = 300 # 평균 일일 생산량
    baseline_cum = [d * daily_prod for d in days]
    
    sim_cum = []
    current_prod = 0
    safe_days = 5 # 안전 재고 일수
    for d in days:
        is_stalled = False
        if d > safe_days and d <= supplier_delay:
            is_stalled = True
            
        if not is_stalled:
            current_prod += daily_prod
        sim_cum.append(current_prod)
        
    line_df = pd.DataFrame({
        '일자 (Day)': days,
        '기존 계획 생산량': baseline_cum,
        '예측 생산량 (지연 반영)': sim_cum
    })
    
    # Plotly 변환
    line_df_melt = line_df.melt('일자 (Day)', var_name='시나리오', value_name='누적 생산량 (Units)')
    
    fig_prod = px.line(
        line_df_melt, 
        x='일자 (Day)', 
        y='누적 생산량 (Units)', 
        color='시나리오',
        color_discrete_map={'기존 계획 생산량': 'grey', '예측 생산량 (지연 반영)': 'blue'},
        title="30일 누적 생산량 예측"
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# 상세 데이터 테이블
with st.expander("📝 상세 데이터 보기 (부품 및 공급망)"):
    st.dataframe(df_parts)
