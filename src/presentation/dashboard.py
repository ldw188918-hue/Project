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
# 데이터 로드 (DI: Dependency Injection 유사 패턴)
# @st.cache_data 제거: 파일 업로드 스트림 이슈 방지 및 즉각적인 반응성 확보
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



# 파일 업로드 성공 피드백
if parts_file or suppliers_file or production_file:
    uploaded_files = []
    if parts_file: uploaded_files.append("부품")
    if suppliers_file: uploaded_files.append("공급사")
    if production_file: uploaded_files.append("생산라인")
    
    st.sidebar.success(f"✅ 데이터 로드 완료: {', '.join(uploaded_files)}")

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
    "원자재 단가 변화율 (%)",
    min_value=-50.0,
    max_value=50.0,
    value=0.0,
    step=1.0,
    help="양수: 가격 상승, 음수: 가격 하락"
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
        markers=True
    )
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
        color_discrete_sequence=['#EF553B']
    )
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
            markers=True
        )
        
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

# 차트 영역 (기존 코드 재활용하되 데이터 소스를 Context로 변경)
st.markdown("---")
# ... (차트 부분은 그대로 두거나 필요시 업데이트) ...
# 간소화를 위해 상세 데이터만 표시
st.subheader("📉 상세 데이터")
st.dataframe(df_parts)

