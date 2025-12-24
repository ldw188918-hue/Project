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

# CSV 템플릿 로드 (템플릿 다운로드용)
@st.cache_data
def load_templates():
    templates_path = Path(__file__).parent.parent.parent / "templates"
    return {
        'parts': (templates_path / "parts_template.csv").read_text(),
        'suppliers': (templates_path / "suppliers_template.csv").read_text(),
        'production': (templates_path / "production_template.csv").read_text()
    }

templates = load_templates()

# 사이드바 - CSV 업로드
with st.sidebar.expander("📁 데이터 업로드", expanded=False):
    st.caption("자체 데이터로 시뮬레이션")
    
    # 템플릿 다운로드
    st.markdown("**📥 템플릿 다운로드**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            "부품",
            templates['parts'],
            "parts_template.csv",
            "text/csv",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "공급사",
            templates['suppliers'],
            "suppliers_template.csv",
            "text/csv",
            use_container_width=True
        )
    with col3:
        st.download_button(
            "라인",
            templates['production'],
            "production_template.csv",
            "text/csv",
            use_container_width=True
        )
    
    st.divider()
    
    # CSV 업로드
    st.markdown("**📤 CSV 업로드**")
    
    # 업로드 섹션을 더 컴팩트하게 표현
    with st.container():
        parts_file = st.file_uploader(
            "부품 데이터", 
            type=['csv'],
            key='parts_upload',
            help="부품 정보 CSV 파일을 업로드하세요"
        )
        
        suppliers_file = st.file_uploader(
            "공급사 데이터",
            type=['csv'],
            key='suppliers_upload',
            help="공급사 정보 CSV 파일을 업로드하세요"
        )
        
        production_file = st.file_uploader(
            "생산라인 데이터",
            type=['csv'],
            key='production_upload',
            help="생산라인 정보 CSV 파일을 업로드하세요"
        )

# 데이터 로드 (DI: Dependency Injection 유사 패턴)
@st.cache_data
def get_simulation_service(_parts_file=None, _suppliers_file=None, _production_file=None):
    repo = SimulationRepository()
    
    # 업로드된 파일이 있으면 사용, 없으면 mock 데이터
    if _parts_file or _suppliers_file or _production_file:
        context = repo.load_context_from_uploads(
            parts_csv=_parts_file,
            suppliers_csv=_suppliers_file,
            production_csv=_production_file
        )
    else:
        context = repo.load_context()
    
    return SimulationService(context)

service = get_simulation_service(parts_file, suppliers_file, production_file)

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
