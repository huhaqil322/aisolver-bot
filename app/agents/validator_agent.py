from app.agents.base_agent import AgentType, BaseAgent, AgentResult
from app.agents.prompts import VALIDATOR_SYSTEM_PROMPT
from app.core.ai_provider import Message, MessageRole, TokenUsage


class ValidatorAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.VALIDATOR,
            system_prompt=VALIDATOR_SYSTEM_PROMPT,
        )

    async def validate(self, problem: str, solution: str, context) -> AgentResult:
        validation_prompt = f"""Problem:
{problem}

Proposed Solution:
{solution}

Please validate this solution step by step. Check all calculations, reasoning, and final answer. Assign a confidence score and list any errors found."""
        return await self.process(validation_prompt, context)
