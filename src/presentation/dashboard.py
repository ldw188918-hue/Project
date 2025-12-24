import streamlit as st
import pandas as pd
import plotly.express as px

import sys
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from infrastructure.repositories import SimulationRepository
from application.services import SimulationService

# 페이지 설정
st.set_page_config(
    page_title="공급망 디지털 트윈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 헤더
st.title("🏭 디지털 트윈: 공급망 리스크 분석")
st.markdown("### 제조 분야 의사결정 지원 시스템 (DSS) - SOLID Architecture Ver.")

# 데이터 로드 (DI: Dependency Injection 유사 패턴)
@st.cache_data
def get_simulation_service():
    repo = SimulationRepository()
    context = repo.load_context()
    return SimulationService(context)

service = get_simulation_service()

# 기존 레거시 데이터프레임 접근 (차트 그리기용, 서비스에서 데이터를 DTO로 꺼내오는 게 정석이나 편의상 컨텍스트 활용)
# 하지만 순수하게 하기 위해 서비스나 리포지토리에서 DF 변환 메서드를 제공하는 것이 좋음.
# 여기서는 시각화를 위해 Context 데이터를 DataFrame으로 변환.
context = service.context
df_parts = pd.DataFrame([vars(p) for p in context.parts])

# 사이드바
st.sidebar.header("🎛️ What-If 시나리오 시뮬레이션")
st.sidebar.markdown("변수를 조절하여 공급망 예상 리스크를 시뮬레이션하세요.")

price_increase = st.sidebar.slider(
    "원자재 단가 상승률 (%)",
    min_value=0.0,
    max_value=50.0,
    value=0.0,
    step=1.0
)

supplier_delay = st.sidebar.slider(
    "공급사 납품 지연 (일수)",
    min_value=0,
    max_value=30,
    value=0,
    step=1
)

# 시뮬레이션 실행 (어플리케이션 서비스 호출)
result = service.run_simulation(price_increase, supplier_delay)

# --- KPI 출력 (기존 로직 유지하되 Service Result 사용) ---
st.markdown("---")
st.subheader("📊 경영진 요약 (Executive Summary)")

col1, col2, col3 = st.columns(3)

# 1. 영업 이익 Delta
# Base Calculation 로직이 아직 단순화되어 있어서, 기존 로직처럼 '변화량' 중심으로 표현
col1.metric(
    label="영업이익 변화 (Profit Delta)",
    value=f"${result.profit_delta:,.0f}",
    delta=f"{result.profit_delta:,.0f}",
    delta_color="normal"
)

# 2. 생산 손실
col2.metric(
    label="생산 차질 (Production Loss)",
    value=f"-{result.production_loss:,.0f} units",
    delta=f"-{result.production_loss:,.0f}",
    delta_color="inverse" # 손실이 커지면 빨간색
)

# 3. 리스크 레벨
risk_status = "낮음 (Low)"
risk_color = "green"
if supplier_delay > 5:
    risk_status = "주의 (Medium)"
    risk_color = "orange"
if supplier_delay > 15 or result.profit_delta < -100000: # 임의의 임계값
    risk_status = "위험 (High)"
    risk_color = "red"

col3.markdown(f"**리스크 레벨 (Risk Level)**")
col3.markdown(f"<h2 style='color: {risk_color};'>{risk_status}</h2>", unsafe_allow_html=True)

# 차트 영역 (기존 코드 재활용하되 데이터 소스를 Context로 변경)
st.markdown("---")
# ... (차트 부분은 그대로 두거나 필요시 업데이트) ...
# 간소화를 위해 상세 데이터만 표시
st.subheader("📉 상세 데이터")
st.dataframe(df_parts)
