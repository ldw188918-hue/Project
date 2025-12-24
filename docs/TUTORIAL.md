# 📚 Digital Twin 프로젝트 튜토리얼

이 튜토리얼은 프로젝트를 **처음부터 끝까지** 따라하며 학습할 수 있도록 구성되었습니다.

## 🎯 학습 목표
이 튜토리얼을 완료하면 다음을 할 수 있게 됩니다:
- SOLID 원칙 기반의 아키텍처 이해
- TDD(Test-Driven Development) 방식으로 코드 작성
- Streamlit을 활용한 대시보드 개발
- GitHub Actions를 통한 CI/CD 파이프라인 구축

---

## 📋 사전 준비 사항

### 1️⃣ 필수 소프트웨어 설치
다음 소프트웨어가 설치되어 있어야 합니다:

#### Python 3.10 이상
```bash
# 설치 확인
python --version
# 출력 예시: Python 3.10.0 이상이어야 함
```
**설치 방법**: [python.org](https://python.org) 에서 다운로드

#### Git
```bash
# 설치 확인
git --version
```
**설치 방법**: [git-scm.com](https://git-scm.com) 에서 다운로드

#### Visual Studio Code (권장)
**설치 방법**: [code.visualstudio.com](https://code.visualstudio.com) 에서 다운로드

---

## 📂 Step 1: 프로젝트 시작하기

### 1-1. GitHub 레포지토리 Fork 또는 Clone
```bash
# 방법 1: 기존 프로젝트 클론
git clone https://github.com/ldw188918-hue/Project.git
cd Project

# 방법 2: 본인의 GitHub에서 새로 시작하려면
mkdir digital-twin-dashboard
cd digital-twin-dashboard
git init
```

### 1-2. 가상 환경 생성 및 활성화
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 1-3. 의존성 패키지 설치
```bash
pip install -r requirements.txt
```

**설치되는 패키지**:
- `pandas`: 데이터 처리
- `numpy`: 수치 계산
- `plotly`: 인터랙티브 차트
- `streamlit`: 웹 대시보드 프레임워크
- `pytest`: 테스트 프레임워크

---

## 🏗️ Step 2: 프로젝트 구조 이해하기

```
Project/
├── src/
│   ├── domain/              # 핵심 비즈니스 로직
│   │   ├── models.py        # 데이터 클래스 (Supplier, Part 등)
│   │   ├── interfaces.py    # 추상 인터페이스 (ISimulationStrategy)
│   │   └── strategies.py    # 시뮬레이션 전략 구현
│   ├── application/         # 유스케이스 서비스
│   │   └── services.py      # SimulationService (Facade 패턴)
│   ├── infrastructure/      # 데이터 레이어
│   │   └── repositories.py  # 데이터 로더
│   └── presentation/        # UI 레이어
│       └── dashboard.py     # Streamlit 대시보드
├── tests/                   # 테스트 코드
│   └── test_strategies.py  # 전략 패턴 단위 테스트
├── docs/                    # 문서
└── .github/workflows/       # CI/CD 파이프라인
```

**아키텍처 핵심 개념**:
- **Domain Layer**: 외부 의존성 없는 순수 비즈니스 로직
- **Application Layer**: 도메인을 조합하여 유스케이스 처리
- **Infrastructure Layer**: 외부 시스템(DB, API) 연동
- **Presentation Layer**: 사용자 인터페이스

---

## ✅ Step 3: 테스트 실행해보기 (TDD 체험)

### 3-1. 전체 테스트 실행
```bash
pytest tests/
```

**예상 출력**:
```
collected 2 items

tests/test_strategies.py ..                    [100%]

======= 2 passed in 0.02s =======
```

### 3-2. 테스트 코드 이해하기
`tests/test_strategies.py` 파일을 열어보세요.

**Red-Green-Refactor 사이클**:
1. **Red**: 실패하는 테스트를 먼저 작성 (`test_price_hike_strategy_calculation`)
2. **Green**: 테스트를 통과하는 최소 코드 작성 (`PriceHikeStrategy`)
3. **Refactor**: 중복 제거 및 코드 개선

---

## 🎨 Step 4: 대시보드 실행하기

### 4-1. Streamlit 앱 실행
```bash
streamlit run src/presentation/dashboard.py
```

### 4-2. 브라우저에서 확인
- 자동으로 브라우저가 열리면서 `http://localhost:8501` 접속
- 좌측 사이드바에서 슬라이더를 조작하여 시뮬레이션 실행
  - **원자재 단가 상승률**: 0% → 20% 변경 시 영업이익 감소 확인
  - **공급사 납품 지연**: 0일 → 10일 변경 시 생산 차질 확인

---

## 🧪 Step 5: 새로운 기능 추가하기 (TDD 실습)

### 실습 과제: "환율 변동 시나리오" 추가하기

#### 5-1. 테스트 먼저 작성 (Red)
`tests/test_strategies.py`에 다음 테스트 추가:

```python
def test_exchange_rate_strategy():
    from src.domain.strategies import ExchangeRateStrategy
    
    part = Part(id="P1", name="Part1", supplier_id="S1", 
                unit_price=100.0, current_inventory=10, daily_usage_rate=1)
    context = SimulationContext(parts=[part], suppliers=[], production_lines=[])
    
    # 환율 10% 상승 시뮬레이션
    strategy = ExchangeRateStrategy(rate_increase_pct=10.0)
    result = strategy.calculate(context)
    
    # 환율 상승 = 수입 부품 가격 상승 = 비용 증가
    assert result.profit_delta < 0
```

#### 5-2. 테스트 실행 (실패 확인)
```bash
pytest tests/test_strategies.py::test_exchange_rate_strategy
```

#### 5-3. 구현 코드 작성 (Green)
`src/domain/strategies.py`에 클래스 추가:

```python
class ExchangeRateStrategy(ISimulationStrategy):
    def __init__(self, rate_increase_pct: float):
        self.rate_increase_pct = rate_increase_pct

    def calculate(self, context: SimulationContext) -> SimulationResult:
        # 수입 부품에만 환율 영향 적용 (여기서는 전체 적용으로 간소화)
        total_delta = 0.0
        for part in context.parts:
            base_cost = part.unit_price * part.monthly_usage
            new_cost = base_cost * (1 + self.rate_increase_pct / 100)
            total_delta -= (new_cost - base_cost)
        
        return SimulationResult(
            operating_profit=0,
            production_output=0,
            profit_delta=total_delta,
            production_loss=0
        )
```

#### 5-4. 테스트 재실행 (통과 확인)
```bash
pytest tests/test_strategies.py::test_exchange_rate_strategy
```

---

## 🚀 Step 6: GitHub에 배포하기

### 6-1. 변경사항 커밋
```bash
git add .
git commit -m "Feat: 환율 변동 시나리오 추가"
```

### 6-2. GitHub에 푸시
```bash
git push origin main
```

### 6-3. GitHub Actions 확인
1. `https://github.com/본인계정/Project/actions` 접속
2. **Unit Tests** 워크플로우가 자동으로 실행되는지 확인
3. 모든 테스트가 통과하면 ✅ 표시

### 6-4. GitHub Pages 확인
- `https://본인계정.github.io/Project/` 접속
- 프로젝트 소개 페이지 확인

---

## 📊 Step 7: 대시보드에 새 기능 추가하기

### 7-1. UI에 환율 슬라이더 추가
`src/presentation/dashboard.py` 수정:

```python
# 사이드바에 슬라이더 추가
exchange_rate = st.sidebar.slider(
    "환율 상승률 (%)",
    min_value=0.0,
    max_value=30.0,
    value=0.0,
    step=1.0
)

# SimulationService에 전달 (services.py도 수정 필요)
```

### 7-2. 로컬에서 확인
```bash
streamlit run src/presentation/dashboard.py
```

---

## 🎓 학습 체크리스트

완료한 항목에 체크하세요:
- [ ] 프로젝트 클론 및 환경 설정 완료
- [ ] 프로젝트 구조 및 SOLID 아키텍처 이해
- [ ] 테스트 실행 및 TDD 사이클 체험
- [ ] Streamlit 대시보드 실행 체험
- [ ] 새로운 시뮬레이션 전략 추가 (TDD 실습)
- [ ] GitHub Actions CI/CD 파이프라인 확인
- [ ] GitHub Pages 배포 확인

---

## 🔍 추가 학습 자료

### 참고 문서
- [PRD (제품 요구사항 문서)](docs/prd.md)
- [Tech Spec (기술 명세서)](docs/tech_spec.md)
- [개발 규칙](docs/rules.md)

### 외부 자료
- [SOLID 원칙 설명](https://ko.wikipedia.org/wiki/SOLID_(%EA%B0%9D%EC%B2%B4_%EC%A7%80%ED%96%A5_%EC%84%A4%EA%B3%84))
- [TDD 가이드](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Streamlit 공식 문서](https://docs.streamlit.io)

---

## ❓ 자주 묻는 질문 (FAQ)

**Q1. 테스트가 실패합니다.**  
A: `pytest -v`로 상세 로그를 확인하세요. 주로 임포트 오류나 의존성 문제입니다.

**Q2. Streamlit이 실행되지 않습니다.**  
A: 가상환경이 활성화되었는지 확인하세요. `which python` (macOS/Linux) 또는 `where python` (Windows)로 확인 가능합니다.

**Q3. GitHub Pages에 배포했는데 빈 페이지만 나옵니다.**  
A: Settings > Pages에서 Source가 `gh-pages` 브랜치로 설정되었는지 확인하세요.

---

**축하합니다! 🎉**  
이제 엔터프라이즈급 아키텍처를 갖춘 프로젝트를 처음부터 끝까지 다룰 수 있습니다!
