from typing import List
from dataclasses import dataclass
from domain.models import SimulationContext, SimulationResult


@dataclass
class Insight:
    """비즈니스 인사이트 데이터 모델"""
    type: str  # "warning", "recommendation", "info"
    title: str
    message: str
    priority: int  # 1(높음) ~ 3(낮음)


class InsightsService:
    """
    Rule-based AI 인사이트 생성 서비스
    시뮬레이션 결과를 분석하여 실용적인 비즈니스 조언 생성
    """
    
    def generate_insights(
        self,
        context: SimulationContext,
        result: SimulationResult,
        price_increase_pct: float,
        delay_days: int
    ) -> List[Insight]:
        """현재 상황 기반 인사이트 생성"""
        insights = []
        
        # 1. 영업이익 변화 분석
        insights.extend(self._analyze_profit_impact(result.profit_delta, price_increase_pct))
        
        # 2. 생산 손실 분석
        insights.extend(self._analyze_production_loss(result.production_loss, delay_days))
        
        # 3. 재고 관리 분석
        insights.extend(self._analyze_inventory(context, delay_days))
        
        # 4. 공급사 리스크 분석
        insights.extend(self._analyze_supplier_risk(context, delay_days))
        
        # 5. 복합 리스크 분석
        if price_increase_pct > 0 and delay_days > 0:
            insights.extend(self._analyze_combined_risk(result, price_increase_pct, delay_days))
        
        # 우선순위 순으로 정렬
        insights.sort(key=lambda x: x.priority)
        
        return insights
    
    def _analyze_profit_impact(self, profit_delta: float, price_increase_pct: float) -> List[Insight]:
        """영업이익 영향 분석"""
        insights = []
        
        if profit_delta < -100000:
            insights.append(Insight(
                type="warning",
                title="⚠️ 심각한 영업이익 감소 예상",
                message=f"원자재 가격 {price_increase_pct}% 상승으로 약 ${abs(profit_delta):,.0f}의 "
                        f"손실이 예상됩니다. 즉시 대응이 필요합니다.",
                priority=1
            ))
            insights.append(Insight(
                type="recommendation",
                title="💡 대응 방안",
                message="1) 대체 공급사 긴급 검토\n"
                        "2) 제품 가격 인상 고려\n"
                        "3) 장기 계약으로 가격 고정 협상",
                priority=2
            ))
        elif profit_delta < -50000:
            insights.append(Insight(
                type="warning",
                title="⚠️ 영업이익 감소 주의",
                message=f"${abs(profit_delta):,.0f}의 손실이 예상됩니다. "
                        f"비용 절감 방안을 검토하세요.",
                priority=2
            ))
        elif profit_delta < -10000:
            insights.append(Insight(
                type="info",
                title="📊 경미한 영업이익 영향",
                message=f"${abs(profit_delta):,.0f}의 소폭 손실이 예상됩니다. "
                        f"모니터링을 지속하세요.",
                priority=3
            ))
        
        return insights
    
    def _analyze_production_loss(self, production_loss: int, delay_days: int) -> List[Insight]:
        """생산 손실 분석"""
        insights = []
        
        if production_loss > 1000:
            insights.append(Insight(
                type="warning",
                title="⚠️ 대규모 생산 차질 예상",
                message=f"{delay_days}일 지연으로 {production_loss:,} units의 생산 손실이 예상됩니다. "
                        f"고객 납기 준수가 어려울 수 있습니다.",
                priority=1
            ))
            insights.append(Insight(
                type="recommendation",
                title="💡 생산 차질 대응",
                message="1) 안전 재고 50% 증가 권장\n"
                        "2) 대체 공급사 선정\n"
                        "3) 고객사와 납기 재협상 준비",
                priority=2
            ))
        elif production_loss > 500:
            insights.append(Insight(
                type="warning",
                title="⚠️ 생산 차질 주의",
                message=f"{production_loss:,} units의 생산 손실이 예상됩니다. "
                        f"생산 계획을 재조정하세요.",
                priority=2
            ))
        
        return insights
    
    def _analyze_inventory(self, context: SimulationContext, delay_days: int) -> List[Insight]:
        """재고 관리 분석"""
        insights = []
        
        if delay_days > 10:
            # 재고가 부족한 부품 찾기
            critical_parts = []
            for part in context.parts:
                days_of_inventory = part.current_inventory / part.daily_usage_rate
                if days_of_inventory < delay_days:
                    critical_parts.append(part.name)
            
            if critical_parts:
                insights.append(Insight(
                    type="warning",
                    title="⚠️ 재고 부족 위험",
                    message=f"다음 부품의 재고가 {delay_days}일 지연을 감당하기 어렵습니다:\n" +
                            "\n".join(f"- {name}" for name in critical_parts[:3]) +
                            (f"\n...외 {len(critical_parts)-3}개" if len(critical_parts) > 3 else ""),
                    priority=1
                ))
                insights.append(Insight(
                    type="recommendation",
                    title="💡 재고 확보 전략",
                    message=f"최소 {delay_days + 5}일분의 안전 재고 확보를 권장합니다. "
                            f"긴급 발주를 고려하세요.",
                    priority=2
                ))
        
        return insights
    
    def _analyze_supplier_risk(self, context: SimulationContext, delay_days: int) -> List[Insight]:
        """공급사 리스크 분석"""
        insights = []
        
        # 고위험 공급사 찾기
        high_risk_suppliers = [s for s in context.suppliers if s.risk_score > 0.4]
        
        if high_risk_suppliers and delay_days > 5:
            insights.append(Insight(
                type="recommendation",
                title="💡 공급사 다각화 권장",
                message=f"{len(high_risk_suppliers)}개 공급사가 고위험으로 분류되었습니다. "
                        f"공급망 리스크 분산을 위해 대체 공급사 확보를 권장합니다.",
                priority=2
            ))
        
        return insights
    
    def _analyze_combined_risk(
        self,
        result: SimulationResult,
        price_increase_pct: float,
        delay_days: int
    ) -> List[Insight]:
        """복합 리스크 분석"""
        insights = []
        
        # 가격 상승 + 지연의 복합 효과
        if price_increase_pct >= 15 and delay_days >= 10:
            insights.append(Insight(
                type="warning",
                title="🚨 복합 리스크 경보",
                message=f"원자재 가격 급등({price_increase_pct}%)과 공급 지연({delay_days}일)이 "
                        f"동시에 발생하여 매우 위험한 상황입니다. 경영진 즉시 대응이 필요합니다.",
                priority=1
            ))
            insights.append(Insight(
                type="recommendation",
                title="💡 긴급 대응 계획",
                message="1) 비상 경영진 회의 소집\n"
                        "2) 전사 비용 절감 프로그램 시작\n"
                        "3) 고객사 가격 인상 협상\n"
                        "4) 긴급 자금 흐름 점검",
                priority=1
            ))
        
        return insights
