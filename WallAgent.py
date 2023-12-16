import mesa

from utils import agentTypes
class WallAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.typeAgent = agentTypes.WALL
        self.wealth = 1
