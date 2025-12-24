from abc import ABC, abstractmethod
from src.domain.models import SimulationContext, SimulationResult

class ISimulationStrategy(ABC):
    """
    OCP를 위한 시뮬레이션 전략 인터페이스.
    새로운 시나리오가 추가되면 이 인터페이스를 구현한다.
    """
    @abstractmethod
    def calculate(self, context: SimulationContext) -> SimulationResult:
        pass
