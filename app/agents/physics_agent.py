from app.agents.base_agent import AgentType, BaseAgent
from app.agents.prompts import PHYSICS_SYSTEM_PROMPT


class PhysicsAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__(
            agent_type=AgentType.PHYSICS,
            system_prompt=PHYSICS_SYSTEM_PROMPT,
        )
