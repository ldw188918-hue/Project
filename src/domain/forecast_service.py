from typing import Dict, List
import pandas as pd
from domain.models import SimulationContext, SimulationResult
from domain.strategies import PriceHikeStrategy, DelayImpactStrategy


class ForecastService:
    """
    예측 및 트렌드 분석 서비스
    다양한 시나리오에 대한 예측 결과 제공
    """
    
    def forecast_scenarios(
        self,
        context: SimulationContext,
        max_price_increase: float = 30.0,
        max_delay: int = 30
    ) -> Dict:
        """
        다양한 시나리오별 예측 결과 생성
        
        Returns:
            Dict with keys:
            - price_scenarios: 가격 상승별 영향
            - delay_scenarios: 지연별 영향
            - combined_scenarios: 복합 시나리오
        """
        
        # 1. 가격 상승 시나리오 (0% ~ max_price_increase%)
        price_scenarios = self._forecast_price_impact(context, max_price_increase)
        
        # 2. 지연 시나리오 (0일 ~ max_delay일)
        delay_scenarios = self._forecast_delay_impact(context, max_delay)
        
        # 3. 복합 시나리오 (가격 상승 + 지연)
        combined_scenarios = self._forecast_combined_impact(context)
        
        return {
            'price_scenarios': price_scenarios,
            'delay_scenarios': delay_scenarios,
            'combined_scenarios': combined_scenarios
        }
    
    def _forecast_price_impact(
        self,
        context: SimulationContext,
        max_increase: float
    ) -> pd.DataFrame:
        """가격 상승률별 영업이익 영향 예측"""
        scenarios = []
        
        # 0%부터 max_increase%까지 5% 간격으로
        for pct in range(0, int(max_increase) + 1, 5):
            if pct == 0:
                profit_delta = 0
            else:
                strategy = PriceHikeStrategy(float(pct))
                result = strategy.calculate(context)
                profit_delta = result.profit_delta
            
            scenarios.append({
                'price_increase_pct': pct,
                'profit_delta': profit_delta,
                'risk_level': self._calculate_risk_level(profit_delta, 0)
            })
        
        return pd.DataFrame(scenarios)
    
    def _forecast_delay_impact(
        self,
        context: SimulationContext,
        max_delay: int
    ) -> pd.DataFrame:
        """공급 지연별 생산 손실 예측"""
        scenarios = []
        
        # 0일부터 max_delay일까지 5일 간격으로
        for days in range(0, max_delay + 1, 5):
            if days == 0:
                production_loss = 0
            else:
                strategy = DelayImpactStrategy(days)
                result = strategy.calculate(context)
                production_loss = result.production_loss
            
            scenarios.append({
                'delay_days': days,
                'production_loss': production_loss,
                'risk_level': self._calculate_risk_level(0, days)
            })
        
        return pd.DataFrame(scenarios)
    
    def _forecast_combined_impact(
        self,
        context: SimulationContext
    ) -> List[Dict]:
        """복합 시나리오 예측 (주요 조합만)"""
        combined = []
        
        # 주요 시나리오 조합
        scenarios = [
            (0, 0, "정상 상태"),
            (10, 5, "경미한 리스크"),
            (15, 10, "중간 리스크"),
            (20, 15, "높은 리스크"),
            (30, 20, "매우 높은 리스크")
        ]
        
        for price_pct, delay_days, label in scenarios:
            profit_delta = 0
            production_loss = 0
            
            if price_pct > 0:
                price_strategy = PriceHikeStrategy(float(price_pct))
                price_result = price_strategy.calculate(context)
                profit_delta = price_result.profit_delta
            
            if delay_days > 0:
                delay_strategy = DelayImpactStrategy(delay_days)
                delay_result = delay_strategy.calculate(context)
                production_loss = delay_result.production_loss
            
            combined.append({
                'scenario': label,
                'price_increase_pct': price_pct,
                'delay_days': delay_days,
                'profit_delta': profit_delta,
                'production_loss': production_loss,
                'total_impact_score': self._calculate_total_impact(profit_delta, production_loss),
                'risk_level': self._calculate_risk_level(profit_delta, delay_days)
            })
        
        return combined
    
    def _calculate_risk_level(self, profit_delta: float, delay_days: int) -> str:
        """리스크 레벨 계산"""
        if delay_days > 15 or profit_delta < -100000:
            return "위험 (High)"
        elif delay_days > 5 or profit_delta < -50000:
            return "주의 (Medium)"
        else:
            return "낮음 (Low)"
    
    def _calculate_total_impact(self, profit_delta: float, production_loss: int) -> float:
        """
        총 영향 점수 계산
        (비용 손실 + 생산 손실을 정규화한 점수)
        """
        # 생산 손실을 금액으로 환산 (가정: 1 unit = $1000 가치)
        production_loss_value = production_loss * 1000
        
        # 총 손실 (음수)
        total_loss = profit_delta + (-production_loss_value)
        
        return total_loss
    
    def get_risk_trend(
        self,
        context: SimulationContext,
        current_price_increase: float,
        current_delay: int
    ) -> Dict:
        """
        현재 상황 기반 향후 30일 리스크 트렌드 예측
        
        Args:
            current_price_increase: 현재 가격 상승률
            current_delay: 현재 지연 일수
            
        Returns:
            향후 30일간의 리스크 트렌드
        """
        # 간단한 선형 예측 (실제로는 더 복잡한 모델 사용 가능)
        days = list(range(0, 31, 5))  # 0, 5, 10, 15, 20, 25, 30일
        
        trend_data = []
        for day in days:
            # 시간이 지날수록 상황이 조금씩 악화된다고 가정
            future_price = current_price_increase + (day * 0.3)  # 일주일마다 0.5% 추가 상승
            future_delay = current_delay + (day // 7)  # 일주일마다 1일 추가 지연
            
            # 예측 계산
            profit_delta = 0
            production_loss = 0
            
            if future_price > 0:
                price_strategy = PriceHikeStrategy(future_price)
                price_result = price_strategy.calculate(context)
                profit_delta = price_result.profit_delta
            
            if future_delay > 0:
                delay_strategy = DelayImpactStrategy(int(future_delay))
                delay_result = delay_strategy.calculate(context)
                production_loss = delay_result.production_loss
            
            trend_data.append({
                'day': day,
                'predicted_price_increase': future_price,
                'predicted_delay': future_delay,
                'predicted_profit_delta': profit_delta,
                'predicted_production_loss': production_loss,
                'risk_level': self._calculate_risk_level(profit_delta, int(future_delay))
            })
        
        return {
            'trend_data': pd.DataFrame(trend_data),
            'warning': '이 예측은 현재 추세가 계속된다는 가정하에 생성되었습니다.'
        }
