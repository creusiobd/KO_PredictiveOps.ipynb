import numpy as np
import math
from datetime import datetime

class KOPredictiveOpsEngine:
    def __init__(self, base_risk: float, system_resilience: float):
        """
        :param base_risk: mu(t) - Risco sazonal intrínseco (ex: 0.1 dia comum, 0.8 quinto dia útil)
        :param system_resilience: beta - Quão rápido o sistema absorve/esquece um impacto
        """
        self.base_risk = base_risk
        self.system_resilience = system_resilience
        self.events_history = [] # Armazena tuplas (timestamp, severidade_alpha)
        self.prior_inc_prob = 0.05 # Crença inicial de um INC ocorrer hoje

    def register_signal(self, current_time: float, severity: float):
        """Registra um evento técnico, como degradação de CPU, timeout de DB ou log severo."""
        self.events_history.append((current_time, severity))

    def calculate_hawkes_intensity(self, current_time: float) -> float:
        """Calcula o contágio operacional baseado nos tremores recentes."""
        intensity = self.base_risk
        for event_time, alpha in self.events_history:
            if event_time < current_time:
                time_decay = current_time - event_time
                # Adiciona o impacto do evento com decaimento exponencial
                intensity += alpha * math.exp(-self.system_resilience * time_decay)
        return intensity

    def update_bayesian_probability(self, likelihood_signal_given_inc: float, likelihood_signal_normal: float):
        """
        Atualiza a probabilidade de INC com base em padrões históricos.
        """
        # P(INC | Sinal) = (P(Sinal | INC) * P(INC)) / P(Sinal Total)
        prob_signal_total = (likelihood_signal_given_inc * self.prior_inc_prob) + \
                            (likelihood_signal_normal * (1 - self.prior_inc_prob))

        if prob_signal_total > 0:
            posterior_prob = (likelihood_signal_given_inc * self.prior_inc_prob) / prob_signal_total
            self.prior_inc_prob = posterior_prob # O aprendizado contínuo da máquina

    def evaluate_system_state(self, current_time: float, business_criticality: float) -> str:
        """Sintetiza a saúde e classifica o risco."""
        intensity = self.calculate_hawkes_intensity(current_time)

        # Risco composto: Quão estressado o sistema está * Probabilidade de INC * Peso do Negócio
        total_risk = intensity * self.prior_inc_prob * business_criticality

        # Thresholds de decisão
        if total_risk < 0.2:
            return "🟢 Normal - Fluidez Operacional"
        elif total_risk < 0.5:
            return "🟡 Observação - Sinais Anômalos Isolados"
        elif total_risk < 0.8:
            return "🟠 Risco Elevado - Contágio e Degradação em Curso"
        elif total_risk < 1.2:
            return "🔴 Incidente Provável - Intervenção SRE Requerida"
        else:
            return "⚫ Crise Iminente - Ativar Protocolo de Contingência"

# Simulando a operação na véspera de um quinto dia útil
ko_engine = KOPredictiveOpsEngine(base_risk=0.7, system_resilience=0.1)

# Ocorrem eventos sucessivos (o efeito cascata)
ko_engine.register_signal(current_time=1.0, severity=0.3) # 1. Pico leve na API
ko_engine.register_signal(current_time=2.0, severity=0.6) # 2. Aumento de Lock no Banco de Dados
ko_engine.register_signal(current_time=2.5, severity=0.8) # 3. Kafka Consumer Lag dispara

# Motor percebe que esse combo (API -> DB -> Kafka) tem alta correlação com quedas passadas
ko_engine.update_bayesian_probability(likelihood_signal_given_inc=0.85, likelihood_signal_normal=0.1)

state = ko_engine.evaluate_system_state(current_time=3.0, business_criticality=1.0)
print(f"Estado do Ecossistema: {state}")
     
Estado do Ecossistema: 🟠 Risco Elevado - Contágio e Degradação em Curso
