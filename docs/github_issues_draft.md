# GitHub Issues Draft

이 문서는 프로젝트의 작업 내역을 GitHub Issue로 등록하기 위한 초안입니다. 각 항목을 복사하여 GitHub Repository의 Issue 탭에 등록하실 수 있습니다.

---

## Issue 1: [Refactor] SOLID 원칙 기반 도메인 레이어 구축
**작업 배경 (Background)**
기존의 `simulation.py`에 모든 로직이 집중되어 있어 유지보수와 확장이 어렵습니다. 새로운 시뮬레이션 시나리오(예: 환율 변동, 파업 등)를 유연하게 추가할 수 있도록 **개방-폐쇄 원칙(OCP)**을 적용한 도메인 레이어 설계가 필요합니다.

**작업 내용 (Work Content)**
1.  `src/domain` 패키지 생성.
2.  **Entity 정의**: `Supplier`, `Part`, `ProductionLine` 등 핵심 비즈니스 객체를 Data Class로 정의.
3.  **Interface 정의**: 시뮬레이션 로직을 추상화한 `ISimulationStrategy` 인터페이스 작성.

**인수 조건 (Acceptance Criteria)**
- [ ] `src/domain/models.py`에 주요 데이터 클래스가 정의되어야 함.
- [ ] `src/domain/interfaces.py`에 `calculate` 메서드를 가진 `ISimulationStrategy`가 정의되어야 함.
- [ ] 외부 라이브러리(Pandas, Streamlit 등)에 대한 의존성이 도메인 레이어에 없어야 함.

---

## Issue 2: [Feat] TDD 기반 시뮬레이션 전략 구현 (Strategy Pattern)
**작업 배경 (Background)**
비즈니스 로직의 신뢰성을 보장하기 위해 핵심 계산 엔진을 **TDD(Test-Driven Development)** 방식으로 구현해야 합니다.

**작업 내용 (Work Content)**
1.  **Red**: `PriceHikeStrategy`(단가 상승)와 `DelayImpactStrategy`(납기 지연)에 대한 실패하는 단위 테스트 작성.
2.  **Green**: 테스트를 통과하는 최소한의 구현체 작성.
3.  **Refactor**: 중복 코드를 제거하고 로직 최적화.

**인수 조건 (Acceptance Criteria)**
- [ ] `tests/test_strategies.py`의 모든 테스트 케이스가 통과해야 함.
- [ ] `PriceHikeStrategy`: 원자재 가격 상승에 따른 영업이익 감소분이 정확히 계산되어야 함.
- [ ] `DelayImpactStrategy`: 안전 재고 일수를 초과하는 지연에 대해 생산 차질 물량이 정확히 계산되어야 함.

---

## Issue 3: [Feat] 서비스 레이어(Facade) 및 UI 의존성 주입 구현
**작업 배경 (Background)**
UI(Streamlit)가 도메인 로직에 직접 의존하면 결합도가 높아집니다. **Facade 패턴**을 적용하여 UI는 단순한 인터페이스로 시뮬레이션을 요청하고, 복잡한 전략 조합은 서비스 레이어가 담당하도록 해야 합니다.

**작업 내용 (Work Content)**
1.  `src/application/services.py`에 `SimulationService` 구현.
2.  사용자 입력(가격 인상률, 지연 일수)에 따라 적절한 Strategy 객체를 생성 및 조합하는 로직 구현.
3.  `src/presentation/dashboard.py`를 리팩토링하여 서비스 레이어를 호출하도록 변경.

**인수 조건 (Acceptance Criteria)**
- [ ] UI에서 슬라이더 조작 시 실시간으로 시뮬레이션 결과(KPI)가 업데이트되어야 함.
- [ ] `simulation.py`(구형 로직) 파일이 삭제되고 새로운 아키텍처로 완전히 대체되어야 함.

---

## Issue 4: [DevOps] Stlite 기반 GitHub Pages 배포 파이프라인 구축
**작업 배경 (Background)**
포트폴리오 용도로 누구나 접근 가능한 데모 페이지가 필요합니다. 하지만 별도의 서버 호스팅 비용을 절감하기 위해 **Serverless** 방식인 **Stlite(WASM)**를 활용하여 GitHub Pages에 배포합니다.

**작업 내용 (Work Content)**
1.  GitHub Actions 워크플로우(`deploy.yml`) 작성.
2.  `stlite-cli`를 사용하여 Python 코드를 정적 HTML/JS로 빌드하는 스텝 구현.
3.  `gh-pages` 브랜치로 자동 배포 설정.

**인수 조건 (Acceptance Criteria)**
- [ ] `main` 브랜치 푸시 시 자동으로 빌드 및 배포가 수행되어야 함.
- [ ] 배포된 URL 접속 시 브라우저 상에서 Python 런타임이 로드되고 대시보드가 정상 작동해야 함.
