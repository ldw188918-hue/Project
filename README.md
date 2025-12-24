# 🏭 Digital Twin 공급망 리스크 분석 대시보드 (Smart Factory DSS)

> **"데이터를 넘어, 의사결정의 확신으로"**
>
> 제조업 현장의 불확실성(Uncertainty)을 통제 가능한 리스크(Risk)로 변환하는 **Digital Twin 기반 의사결정 지원 시스템(DSS)**입니다.

## 🌐 온라인 데모

- **라이브 대시보드**: [Streamlit Community Cloud에서 실행하기](https://share.streamlit.io/ldw188918-hue/Project/main/src/presentation/dashboard.py) 🚀
- **프로젝트 홈페이지**: [GitHub Pages](https://ldw188918-hue.github.io/Project/) 📄

> [!NOTE]
> Streamlit Community Cloud 배포 URL은 초기 배포 후 업데이트됩니다.

---

## 1. 프로젝트 소개 (Overview)
글로벌 공급망 이슈는 더 이상 예측 불가능한 재난이 아닙니다. 본 프로젝트는 한화시스템과 같은 제조 기업이 직면한 **부품 수급 불안정**과 **원자재 가격 변동**이 생산 라인과 영업이익에 미치는 영향을 **실시간으로 시뮬레이션**합니다.

단순한 현황 모니터링을 넘어, **"What-If" 시나리오 분석**을 통해 최적의 대응 전략을 수립할 수 있도록 돕습니다.

### 🎯 핵심 가치 & 기능
*   **What-If Simulation**: "원자재 가격이 20% 오르면 영업이익은 얼마나 감소하는가?"와 같은 가정을 즉시 검증.
*   **Real-time DSS**: 복잡한 수실 계산을 자동화하여 3초 이내에 경영진이 확인 가능한 핵심 지표(KPI) 제공.
*   **Cost-Effective Architecture**: 고가의 상용 솔루션 없이 오픈소스(Python Ecosystem)만으로 엔터프라이즈급 로직 구현.

---

## 2. 엔지니어링 역량 (Engineering Highlights)
이 프로젝트는 단순한 구현을 넘어, **지속 가능한 소프트웨어 아키텍처**와 **안정성**을 최우선으로 설계되었습니다.

### 🏗️ SOLID 아키텍처 설계
변화하는 비즈니스 요구사항(새로운 리스크 시나리오 등)에 유연하게 대응하기 위해 **Layered Architecture**와 **SOLID 원칙**을 철저히 준수했습니다.

*   **OCP (Open-Closed Principle)**: 새로운 시뮬레이션 로직(예: 환율 변동) 추가 시 기존 코드를 수정하지 않고 `ISimulationStrategy`를 구현한 클래스만 추가하면 됩니다.
*   **DIP (Dependency Inversion Principle)**: UI는 구체적인 구현체가 아닌 추상화된 인터페이스(Service/Repository)에 의존하여 결합도를 낮췄습니다.

### ✅ TDD (Test-Driven Development)
복잡한 시뮬레이션 계산 로직의 신뢰성을 보장하기 위해 **TDD**를 도입했습니다.
*   **Red-Green-Refactor** 사이클을 준수하여 핵심 비즈니스 로직(Domain Layer)에 대해 **100% 테스트 커버리지**를 달성했습니다.
*   CI(GitHub Actions)를 통해 코드가 변경될 때마다 자동으로 정합성을 검증합니다.

### ☁️ Serverless & Cost Optimization
*   **Stlite (WASM)** 기술을 도입하여 Python 백엔드 서버 없이 브라우저(Client-side)에서 시뮬레이션 엔진이 구동됩니다.
*   이를 통해 **호스팅 비용을 0원**으로 절감(GitHub Pages 활용)하면서도 높은 보안성과 접근성을 확보했습니다.

---

## 3. 기술 스택 (Tech Stack)
*   **Language**: Python 3.10+
*   **Frontend/UI**: Streamlit
*   **Core Logic**: NumPy, Pandas
*   **Data Visualization**: Plotly Interactive Charts
*   **Testing**: Pytest
*   **CI/CD**: GitHub Actions
*   **Deployment**: Stlite (WebAssembly) -> GitHub Pages

## 4. 실행 및 테스트 (How to Run)

### 온라인에서 실행 (권장)
1. [Streamlit Community Cloud 대시보드](https://share.streamlit.io/ldw188918-hue/Project/main/src/presentation/dashboard.py)에 접속
2. 좌측 사이드바에서 시뮬레이션 변수 조절
3. 실시간으로 공급망 리스크 분석 확인

### 로컬 환경 실행
```bash
# 1. 레포지토리 클론
git clone https://github.com/ldw188918-hue/Project.git
cd Project

# 2. 가상환경 생성 및 활성화 (Windows)
python -m venv venv
venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 대시보드 실행
streamlit run src/presentation/dashboard.py
```

### 테스트 실행
```bash
# 단위 테스트 수행
pytest tests/
```

---

## 5. Streamlit Community Cloud 배포 방법

본 프로젝트를 직접 배포하려면:

1. GitHub 레포지토리를 본인 계정으로 fork
2. [Streamlit Community Cloud](https://streamlit.io/cloud)에 접속 (무료)
3. GitHub 계정으로 로그인
4. "New app" 클릭
5. Repository 선택: `your-username/Project`
6. Main file path: `src/presentation/dashboard.py`
7. "Deploy!" 클릭

배포 후 생성된 URL을 README.md에 업데이트하세요.

---
*Developed by [Your Name] for Portfolio Demonstration.*
