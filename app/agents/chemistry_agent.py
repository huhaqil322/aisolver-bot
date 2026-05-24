from app.agents.base_agent import AgentType, BaseAgent
from app.agents.prompts import CHEMISTRY_SYSTEM_PROMPT


class ChemistryAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.CHEMISTRY,
            system_prompt=CHEMISTRY_SYSTEM_PROMPT,
        )
