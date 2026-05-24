from app.agents.base_agent import AgentType, BaseAgent
from app.agents.prompts import MATH_SYSTEM_PROMPT


class MathAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.MATH,
            system_prompt=MATH_SYSTEM_PROMPT,
        )
