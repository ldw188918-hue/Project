import streamlit as st
import pandas as pd
import plotly.express as px

import sys
import importlib
from pathlib import Path

# src 디렉토리를 Python 경로에 추가
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# 모듈 강제 리로드 (캐싱 문제 해결용)
modules_to_reload = [
    'domain.models',
    'domain.strategies',
    'domain.insights_service',
    'domain.forecast_service',
    'infrastructure.repositories',
    'application.services'
]

for module_name in modules_to_reload:
    if module_name in sys.modules:
        try:
            importlib.reload(sys.modules[module_name])
            print(f"Reloaded {module_name}")
        except Exception as e:
            print(f"Failed to reload {module_name}: {e}")

from infrastructure.repositories import SimulationRepository
from application.services import SimulationService
from application.services import SimulationService

# 페이지 설정
st.set_page_config(
    page_title="공급망 디지털 트윈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium UI ---
st.markdown("""
<style>
    /* 메인 타이틀 그라데이션 */
    .block-container h1 {
        background: linear-gradient(90deg, #00E5FF, #FF2B7D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* 카드 스타일 (Glassmorphism) */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-2px);
        border-color: #00E5FF;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.2);
    }
    
    /* Expander 스타일 */
    .streamlit-expanderHeader {
        background-color: #1A1D24 !important;
        border-radius: 8px !important;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #FF2B7D;
        color: #FF2B7D !important;
    }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1A1D24;
        border-radius: 4px;
        border: 1px solid rgba(255,255,255,0.1);
        padding: 10px 20px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00E5FF !important;
        color: black !important;
        font-weight: bold;
    }
    
</style>
""", unsafe_allow_html=True)

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

# 세션 상태 초기화
if 'use_sample' not in st.session_state:
    st.session_state['use_sample'] = False

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

# 파일이 업로드되면 샘플 모드 해제
if parts_file or suppliers_file or production_file:
    st.session_state['use_sample'] = False

# 데이터 로드 (DI: Dependency Injection 유사 패턴)
# 데이터 로드 (DI: Dependency Injection 유사 패턴)
# @st.cache_data 제거: 파일 업로드 스트림 이슈 방지 및 즉각적인 반응성 확보
def get_simulation_service(_parts_file=None, _suppliers_file=None, _production_file=None):
    repo = SimulationRepository()
    
    try:
        # 1. 업로드된 파일이 하나라도 있으면 업로드 로드 시도
        if _parts_file or _suppliers_file or _production_file:
            context = repo.load_context_from_uploads(
                parts_csv=_parts_file,
                suppliers_csv=_suppliers_file,
                production_csv=_production_file
            )
            return SimulationService(context)
            
        # 2. 샘플 데이터 사용 모드이면 Mock 데이터 로드
        elif st.session_state.get('use_sample', False):
            context = repo.load_context()
            return SimulationService(context)
            
        # 3. 그 외의 경우 (데이터 없음)
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ 데이터 처리 중 오류가 발생했습니다: {e}")
        # 디버깅 도움말
        with st.expander("🛠️ 상세 오류 정보"):
            st.code(str(e))
            st.info("파일 형식이 올바른지 확인해주세요 (UTF-8 인코딩, 필수 컬럼 포함 등).")
        return None



# 파일 업로드 성공 피드백
if parts_file or suppliers_file or production_file:
    uploaded_files = []
    if parts_file: uploaded_files.append("부품")
    if suppliers_file: uploaded_files.append("공급사")
    if production_file: uploaded_files.append("생산라인")
    
    st.sidebar.success(f"✅ 데이터 로드 완료: {', '.join(uploaded_files)}")

service = get_simulation_service(parts_file, suppliers_file, production_file)

# --- Empty State 처리 ---
if service is None:
    st.info("👈 왼쪽 사이드바에서 CSV 파일을 업로드하여 분석을 시작하세요.")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("""
        ### 사용 방법
        1. **데이터 업로드**: 사이드바에서 부품, 공급사, 생산라인 데이터를 업로드하세요.
        2. **시뮬레이션**: 가격 변화와 공급 지연 시나리오를 조절하세요.
        3. **인사이트 확인**: AI가 분석한 리스크와 대응 방안을 확인하세요.
        """)
        
        if st.button("🚀 샘플 데이터로 체험하기", type="primary", use_container_width=True):
            st.session_state['use_sample'] = True
            st.rerun()

    # 데이터가 없으면 여기서 실행 중단 (아래 대시보드 코드 실행 안 됨)
    st.stop()

# --- 데이터가 있을 때만 아래 로직 실행 ---

# 하지만 순수하게 하기 위해 서비스나 리포지토리에서 DF 변환 메서드를 제공하는 것이 좋음.
context = service.context


# 사이드바
st.sidebar.header("🎛️ What-If 시나리오 시뮬레이션")
st.sidebar.markdown("변수를 조절하여 공급망 예상 리스크를 시뮬레이션하세요.")

price_increase = st.sidebar.slider(
    "원자재 단가 변화율 (%)",
    min_value=-50.0,
    max_value=50.0,
    value=0.0,
    step=1.0,
    help="양수: 가격 상승, 음수: 가격 하락"
)
st.caption("📉 팁: 값을 음수(-)로 설정하면 원자재 가격 하락에 따른 **영업이익 증가**를 시뮬레이션할 수 있습니다.")

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

# --- AI 인사이트 섹션 ---
st.markdown("---")
st.subheader("🤖 AI 비즈니스 인사이트")

# 인사이트 서비스 로드
from domain.insights_service import InsightsService

insights_service = InsightsService()
insights = insights_service.generate_insights(context, result, price_increase, supplier_delay)

if insights:
    # 인사이트를 타입별로 그룹화
    warnings = [i for i in insights if i.type == "warning"]
    recommendations = [i for i in insights if i.type == "recommendation"]
    infos = [i for i in insights if i.type == "info"]
    
    # Tabs로 구분하여 표시
    tab1, tab2, tab3 = st.tabs(["⚠️ 경고", "💡 권장사항", "📊 정보"])
    
    with tab1:
        if warnings:
            for insight in warnings:
                with st.expander(insight.title, expanded=True):
                    st.markdown(insight.message)
        else:
            st.success("현재 심각한 경고 사항이 없습니다.")
    
    with tab2:
        if recommendations:
            for insight in recommendations:
                with st.expander(insight.title, expanded=False):
                    st.markdown(insight.message)
        else:
            st.info("현재 특별한 권장사항이 없습니다.")
    
    with tab3:
        if infos:
            for insight in infos:
                with st.expander(insight.title, expanded=False):
                    st.markdown(insight.message)
        else:
            st.info("추가 정보가 없습니다.")
else:
    st.success("✅ 현재 공급망 상태가 안정적입니다. 리스크 없음.")

# --- 예측 및 트렌드 섹션 ---
st.markdown("---")
st.subheader("📈 예측 및 트렌드 분석")

from domain.forecast_service import ForecastService

forecast_service = ForecastService()

# 예측 탭
forecast_tab1, forecast_tab2, forecast_tab3 = st.tabs(
    ["가격 상승 시나리오", "공급 지연 시나리오", "향후 30일 예측"]
)

with forecast_tab1:
    st.markdown("**원자재 가격 상승률에 따른 영업이익 영향 예측**")
    forecasts = forecast_service.forecast_scenarios(context)
    price_df = forecasts['price_scenarios']
    
    fig_price = px.line(
        price_df,
        x='price_increase_pct',
        y='profit_delta',
        title='가격 상승률별 영업이익 변화 예측',
        labels={
            'price_increase_pct': '가격 상승률 (%)',
            'profit_delta': '영업이익 변화 ($)'
        },
        markers=True,
        template='plotly_dark'
    )
    fig_price.update_traces(line_color='#00E5FF', marker_color='#00E5FF')
    fig_price.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="손익분기점")
    fig_price.add_hline(y=-100000, line_dash="dash", line_color="red", annotation_text="위험 임계값")
    st.plotly_chart(fig_price, use_container_width=True)
    
    # 데이터 테이블
    with st.expander("📊 상세 데이터 보기"):
        st.dataframe(price_df, use_container_width=True)

with forecast_tab2:
    st.markdown("**공급 지연 일수에 따른 생산 손실 예측**")
    delay_df = forecasts['delay_scenarios']
    
    fig_delay = px.line(
        delay_df,
        x='delay_days',
        y='production_loss',
        title='지연 일수별 생산 손실 예측',
        labels={
            'delay_days': '지연 일수 (일)',
            'production_loss': '생산 손실 (units)'
        },
        markers=True,
        template='plotly_dark'
    )
    fig_delay.update_traces(line_color='#FF2B7D', marker_color='#FF2B7D')
    fig_delay.add_hline(y=500, line_dash="dash", line_color="orange", annotation_text="주의 임계값")
    fig_delay.add_hline(y=1000, line_dash="dash", line_color="red", annotation_text="위험 임계값")
    st.plotly_chart(fig_delay, use_container_width=True)
    
    # 데이터 테이블
    with st.expander("📊 상세 데이터 보기"):
        st.dataframe(delay_df, use_container_width=True)

with forecast_tab3:
    st.markdown("**현재 추세가 계속될 경우 향후 30일 예측**")
    
    if price_increase > 0 or supplier_delay > 0:
        trend_data = forecast_service.get_risk_trend(context, price_increase, supplier_delay)
        trend_df = trend_data['trend_data']
        
        # 이중 축 차트
        fig_trend = px.line(
            trend_df,
            x='day',
            y='predicted_profit_delta',
            title='향후 30일 리스크 트렌드 예측',
            labels={
                'day': '일수 (Days)',
                'predicted_profit_delta': '예상 영업이익 변화 ($)'
            },
            markers=True,
            template='plotly_dark'
        )
        fig_trend.update_traces(line_color='#00E5FF', name='예상 영업이익')
        
        # 생산 손실도 추가 (보조 축)
        fig_trend.add_scatter(
            x=trend_df['day'],
            y=trend_df['predicted_production_loss'],
            mode='lines+markers',
            name='예상 생산 손실 (units)',
            yaxis='y2'
        )
        
        fig_trend.update_layout(
            yaxis2=dict(
                title='예상 생산 손실 (units)',
                overlaying='y',
                side='right'
            )
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # 경고 메시지
        st.warning(trend_data['warning'])
        
        # 상세 데이터
        with st.expander("📊 상세 예측 데이터 보기"):
            st.dataframe(trend_df, use_container_width=True)
    else:
        st.info("시뮬레이션 변수를 조절하면 향후 트렌드 예측이 표시됩니다.")



