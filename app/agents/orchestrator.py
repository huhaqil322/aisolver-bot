from __future__ import annotations

import json
from dataclasses import dataclass, field

from app.agents.base_agent import AgentContext, AgentResult, AgentType, BaseAgent
from app.agents.chemistry_agent import ChemistryAgent
from app.agents.code_agent import CodeAgent
from app.agents.explanation_agent import ExplanationAgent
from app.agents.math_agent import MathAgent
from app.agents.physics_agent import PhysicsAgent
from app.agents.prompts import ORCHESTRATOR_PROMPT
from app.agents.validator_agent import ValidatorAgent
from app.core.ai_provider import TokenUsage


@dataclass
class OrchestrationPlan:
    subject: str
    agents: list[AgentType]
    strategy: str
    needs_validation: bool = True
    needs_explanation: bool = True
    confidence_threshold: float = 0.7


@dataclass
class OrchestrationResult:
    final_answer: str
    plan: OrchestrationPlan
    agent_results: dict[str, AgentResult] = field(default_factory=dict)
    validation_result: AgentResult | None = None
    explanation_result: AgentResult | None = None
    total_tokens: TokenUsage = field(default_factory=TokenUsage)
    confidence: float = 1.0
    error: str | None = None


class AgentRegistry:
    _agents: dict[AgentType, BaseAgent] = {}

    @classmethod
    def register(cls, agent: BaseAgent) -> None:
        cls._agents[agent.agent_type] = agent

    @classmethod
    def get(cls, agent_type: AgentType) -> BaseAgent:
        agent = cls._agents.get(agent_type)
        if agent is None:
            raise KeyError(f"Agent {agent_type} not registered")
        return agent

    @classmethod
    def get_all(cls) -> dict[AgentType, BaseAgent]:
        return dict(cls._agents)


AgentRegistry.register(MathAgent())
AgentRegistry.register(PhysicsAgent())
AgentRegistry.register(ChemistryAgent())
AgentRegistry.register(CodeAgent())
AgentRegistry.register(ValidatorAgent())
AgentRegistry.register(ExplanationAgent())


class OrchestratorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.ORCHESTRATOR,
            system_prompt=ORCHESTRATOR_PROMPT,
        )

    async def classify(self, prompt: str, context: AgentContext) -> OrchestrationPlan:
        classification_prompt = f"""Analyze this user request and classify it:

Request: {prompt}

Respond with JSON only:
{{
    "subject": "mathematics|physics|chemistry|programming|general",
    "required_agents": ["math", "physics", "chemistry", "code", "ocr", "validator", "explanation"],
    "strategy": "direct_solve|step_by_step|multi_agent|verification_needed",
    "needs_validation": true/false,
    "needs_explanation": true/false
}}"""

        try:
            result = await self.process(classification_prompt, context)
            plan_data = json.loads(result.content.strip())
            agent_map = {
                "math": AgentType.MATH,
                "physics": AgentType.PHYSICS,
                "chemistry": AgentType.CHEMISTRY,
                "code": AgentType.CODE,
                "validator": AgentType.VALIDATOR,
                "explanation": AgentType.EXPLANATION,
                "ocr": AgentType.OCR,
            }
            agents = [
                agent_map.get(a, AgentType.MATH)
                for a in plan_data.get("required_agents", ["math"])
            ]
            return OrchestrationPlan(
                subject=plan_data.get("subject", "general"),
                agents=agents,
                strategy=plan_data.get("strategy", "direct_solve"),
                needs_validation=plan_data.get("needs_validation", True),
                needs_explanation=plan_data.get("needs_explanation", True),
            )
        except (json.JSONDecodeError, KeyError, AttributeError):
            return OrchestrationPlan(
                subject="general",
                agents=[AgentType.MATH],
                strategy="direct_solve",
                needs_validation=True,
                needs_explanation=True,
            )

    async def solve(
        self,
        prompt: str,
        context: AgentContext,
        ocr_text: str | None = None,
    ) -> OrchestrationResult:
        final_prompt = ocr_text if ocr_text else prompt

        plan = await self.classify(final_prompt, context)
        total_tokens = TokenUsage()
        agent_results: dict[str, AgentResult] = {}

        subject_to_agent = {
            "mathematics": AgentType.MATH,
            "physics": AgentType.PHYSICS,
            "chemistry": AgentType.CHEMISTRY,
            "programming": AgentType.CODE,
            "code": AgentType.CODE,
            "general": AgentType.MATH,
        }
        primary_type = subject_to_agent.get(plan.subject, AgentType.MATH)
        primary_result = None

        try:
            agent = AgentRegistry.get(primary_type)
            result = await agent.process(final_prompt, context)
            agent_results[primary_type.value] = result
            total_tokens = TokenUsage(
                prompt_tokens=result.tokens_used.prompt_tokens,
                completion_tokens=result.tokens_used.completion_tokens,
                total_tokens=result.tokens_used.total_tokens,
                cost=result.tokens_used.cost,
            )
            if result.error is None:
                primary_result = result
        except Exception:
            pass

        lang = context.language or "en"
        _lang_map = {"ru": "ru", "uk": "ru", "be": "ru"}
        ui_lang = _lang_map.get(lang, "en")
        error_msg_text = (
            "Произошла ошибка:" if ui_lang == "ru" else "I encountered an error:"
        )
        validation_text = (
            "\n\n⚠️ **Примечание проверки:** Уверенность: {confidence:.0%}. "
            "Пожалуйста, проверьте результат самостоятельно."
            if ui_lang == "ru"
            else "\n\n⚠️ **Validation Note:** Confidence: {confidence:.0%}. "
            "Please verify the results independently."
        )

        if primary_result is None:
            err = agent_results.get(primary_type.value, AgentResult(content="", agent_type=AgentType.MATH)).error or "Unknown error"
            return OrchestrationResult(
                final_answer=f"{error_msg_text} {err}",
                plan=plan,
                agent_results=agent_results,
                error=f"Primary agent failed: {err}",
            )

        final_answer = primary_result.content
        confidence = primary_result.confidence

        validation_result = None
        if plan.needs_validation:
            try:
                validator = AgentRegistry.get(AgentType.VALIDATOR)
                validation_result = await validator.validate(
                    final_prompt, final_answer, context
                )
                agent_results["validator"] = validation_result
                total_tokens.prompt_tokens += validation_result.tokens_used.prompt_tokens
                total_tokens.completion_tokens += validation_result.tokens_used.completion_tokens
                total_tokens.total_tokens += validation_result.tokens_used.total_tokens
                total_tokens.cost += validation_result.tokens_used.cost

                if validation_result.confidence < plan.confidence_threshold:
                    final_answer += validation_text.format(confidence=validation_result.confidence)
                confidence = min(confidence, validation_result.confidence)
            except KeyError:
                pass

        explanation_result = None
        if plan.needs_explanation:
            try:
                explainer = AgentRegistry.get(AgentType.EXPLANATION)
                explanation_result = await explainer.simplify(
                    final_prompt,
                    final_answer,
                    level=context.explanation_level,
                    context=context,
                )
                agent_results["explanation"] = explanation_result
                total_tokens.prompt_tokens += explanation_result.tokens_used.prompt_tokens
                total_tokens.completion_tokens += explanation_result.tokens_used.completion_tokens
                total_tokens.total_tokens += explanation_result.tokens_used.total_tokens
                total_tokens.cost += explanation_result.tokens_used.cost

                if explanation_result.error is None and explanation_result.content:
                    final_answer = explanation_result.content
            except KeyError:
                pass

        return OrchestrationResult(
            final_answer=final_answer,
            plan=plan,
            agent_results=agent_results,
            validation_result=validation_result,
            explanation_result=explanation_result,
            total_tokens=total_tokens,
            confidence=confidence,
        )
