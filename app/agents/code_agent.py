from app.agents.base_agent import AgentType, BaseAgent
from app.agents.prompts import CODE_SYSTEM_PROMPT


class CodeAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.CODE,
            system_prompt=CODE_SYSTEM_PROMPT,
        )
