# 기술 명세서 (Tech Spec)
## Digital Twin 공급망 리스크 분석 대시보드

### 1. 개요 (Overview)
본 문서는 "Digital Twin 공급망 리스크 분석 대시보드"의 기술적 아키텍처, 데이터 흐름, 배포 전략을 정의합니다. **TDD**와 **SOLID 원칙**을 기반으로 안정적이고 확장 가능한 코어 로직을 구축하며, **GitHub Pages**를 통한 정적 배포를 목표로 합니다.

### 2. 시스템 아키텍처 (Architecture)
#### 2.1 아키텍처 패턴: Layered Architecture
시스템을 명확한 역할별 레이어로 구분하여 SRP(단일 책임 원칙)와 DIP(의존성 역전 원칙)를 준수합니다.

```mermaid
graph TD
    UI[Presentation Layer (Streamlit)] --> Service[Service Layer (SimulationController)]
    Service --> Domain[Domain Layer (Core Logic)]
    Service --> Data[Data Access Layer (Repository)]
    
    subgraph Domain Layer
        Model[Domain Models (Supplier, Part, Line)]
        Strategy[Simulation Strategy (Abstract)]
        ConcreteStrategy1[PriceImpactStrategy]
        ConcreteStrategy2[DelayImpactStrategy]
    end
```

#### 2.2 디렉토리 구조 (Refactored)
SOLID 원칙 적용을 위해 구조를 세분화합니다.
```
src/
├── domain/             # 비즈니스 로직 (외부 의존성 없음)
│   ├── models.py       # 데이터 클래스 (Supplier, Part 등)
│   ├── interfaces.py   # 추상 인터페이스 (ISimulationStrategy 등)
│   └── services.py     # 도메인 서비스
├── application/        # 유스케이스 처리
│   └── use_cases.py    # 시나리오 실행 오케스트레이션
├── infrastructure/     # 외부 구현체
│   ├── repositories.py # 데이터 로드 (Mock/CSV)
│   └── stlite_wrapper.py # WASM 변환용 래퍼
└── presentation/       # UI
    └── dashboard.py    # Streamlit View
```

### 3. Core Logic Design (SOLID & TDD)

#### 3.1 Open-Closed Principle (OCP) 적용
*   **문제**: 시나리오(가격 인상, 지연, 환율, 파업 등)가 계속 추가될 수 있음.
*   **해결**: `if-else` 문으로 분기하는 대신, `SimulationStrategy` 인터페이스를 정의하고 이를 구현(Implement)하여 확장합니다.

```python
class ISimulationStrategy(ABC):
    @abstractmethod
    def calculate(self, context: SimulationContext) -> SimulationResult:
        pass

class PriceHikeStrategy(ISimulationStrategy):
    def calculate(self, context): ...

class DelayStrategy(ISimulationStrategy):
    def calculate(self, context): ...
```

#### 3.2 Dependency Inversion Principle (DIP) 적용
*   UI는 구체적인 `CsvDataLoader`나 `MockDataLoader`에 의존하지 않고, `IDataLoader` 인터페이스에 의존합니다. 이를 통해 데이터 소스가 바뀌어도 비즈니스 로직은 영향을 받지 않습니다.

### 4. 데이터 흐름 (Data Flow)
1.  **사용자 입력**: Streamlit 사이드바에서 변수(가격 변동폭, 지연 일수) 입력.
2.  **이벤트 전달**: UI가 `SimulationService`에 파라미터 전달.
3.  **전략 선택**: 서비스가 입력값에 맞는 `Strategy` 객체들을 선택 및 조합.
4.  **계산 실행**: 도메인 모델(Entity)의 순수 함수를 호출하여 상태 변화 계산.
5.  **결과 반환**: `SimulationResult` DTO(Data Transfer Object) 반환.
6.  **렌더링**: UI가 결과 데이터를 차트 및 KPI로 렌더링.

### 5. 배포 전략 (Deployment)
#### 5.1 제약 사항
*   **Target**: GitHub Pages (정적 호스팅만 가능, Python 서버 실행 불가).
*   **Source**: Streamlit (Python 런타임 필요).

#### 5.2 해결 방안: Stlite (Streamlit-run-in-browser)
*   **Stlite**는 Pyodide(WebAssembly)를 사용하여 브라우저 내에서 Python과 Streamlit을 구동합니다.
*   **빌드 프로세스**:
    1.  GitHub Actions에서 코드 체크아웃.
    2.  `pip install stlite-cli` 등으로 빌드 도구 설치.
    3.  `stlite mount src/dashboard.py` 명령어로 정적 HTML/JS 번들 생성.
    4.  생성된 `build/` 폴더를 `gh-pages` 브랜치로 배포.

### 6. 테스트 전략 (Testing)
*   **Unit Test**: 도메인 로직 및 전략 패턴 구현체에 대해 100% 커버리지 목표. (Pytest 사용)
*   **Integration Test**: 서비스 레이어와 시뮬레이션 엔진 간의 통합 테스트.
*   **UI Test**: Streamlit UI는 구조 특성상 자동화 테스트 효율이 낮으므로 **제외**하고 수동 검증을 원칙으로 함.
