from app.agents.base_agent import AgentType, BaseAgent, AgentResult
from app.agents.prompts import EXPLANATION_SYSTEM_PROMPT
from app.core.ai_provider import Message, MessageRole


class ExplanationAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.EXPLANATION,
            system_prompt=EXPLANATION_SYSTEM_PROMPT,
        )

    async def simplify(
        self,
        problem: str,
        technical_solution: str,
        level: str = "intermediate",
        context=None,
    ) -> AgentResult:
        simplify_prompt = f"""Original problem: {problem}

Technical solution to adapt: {technical_solution}

User requested level: {level}

Please adapt this solution for the requested level while maintaining accuracy."""
        return await self.process(simplify_prompt, context)
