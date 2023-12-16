import mesa
import seaborn as sns
import numpy as np
import pandas as pd
import requests
import json
from utils import sendGPS2API
from utils import citizenStates, raiderStates, agentTypes
# from CitizenAgent import CitizenAgent


class RaiderAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model,countDownChase):
        super().__init__(unique_id, model)
        self.wealth = 1
        self.state = raiderStates.WALK
        self.destinationPoint = None
        # self.destinationPoint = (15,15)
        # self.chooseUtils = ChooseUtils()
        self.countDownChase = countDownChase
        self.victimIdentifier = None
        self.countDownAssault = 4
        # self.counDownNewAssault = 10
        self.typeAgent = agentTypes.RAIDER

    def setNewDestination(self):
        # print("posicion es :",self.pos)
        temMax = self.model.grid.get_neighborhood(self.pos, moore=True, 
                                                        include_center=False, 
                                                        radius = self.model.distance_to_commute)
        temMin = self.model.grid.get_neighborhood(self.pos, moore=True, 
                                                        include_center=False, 
                                                        radius = self.model.distance_to_commute-2)
        
        possible_pos = list(set(temMax)-set(temMin))
        possible_pos = self.model.filterAvailableSpace(possible_pos)
        self.destinationPoint = self.random.choice(possible_pos)
        print("Current Dest :",self.destinationPoint)


    def give_money(self):
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        cellmates.pop(
            cellmates.index(self)
        )  # Ensure agent is not giving money to itself
        if len(cellmates) > 1:
            other = self.random.choice(cellmates)
            other.wealth += 1
            self.wealth -= 1
            if other == self:
                print("I JUST GAVE MONEY TO MYSELF HEHEHE!")

    def step(self):
        self.updateState()
        if self.state == raiderStates.WALK:
            self.move_walk()
        elif self.state == raiderStates.STALKIN:
            self.move_stalkin()
        elif self.state == raiderStates.CHASING:
            self.move_chasing()
        elif self.state == raiderStates.ASSAULTING:
            self.move_assaulting()
        else:
            print("FAIL STATE!!!")
        # sendGPS2API()
        # if self.wealth > 0:
        #     self.give_money()

    def updateState(self):
        nearbyAgents = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius = self.model.distance_field_of_view
        )
        # print("ONLY GRID: ", field_of_view)
        if self.state == raiderStates.WALK:
            self.countDownChase = 0
            self.victimIdentifier = None
            countTem = 0
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.CITIZEN:
                    self.victimIdentifier = agent # Modify to append victims in list
                    countTem += 1
            if countTem<self.model.minCitizenToStalk and self.victimIdentifier is not None:        
                self.state = raiderStates.STALKIN
        elif self.state == raiderStates.STALKIN:
            countTem = 0
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.CITIZEN:
                    countTem += 1
                if agent == self.victimIdentifier:
                    if self.countDownChase == 0:
                        self.state = raiderStates.CHASING
                    else:
                        self.countDownChase-=1
            if countTem>=self.model.minCitizenToStalk:        
                self.state = raiderStates.WALK
        elif self.state == raiderStates.CHASING:
            countTem = 0
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.CITIZEN:
                    countTem += 1
                if agent == self.victimIdentifier:
                    if self.model.chooseUtils.distance_beetween_points(self.pos,self.victimIdentifier.pos)<=2:
                        self.state = raiderStates.ASSAULTING
            if countTem>=self.model.minCitizenToStalk:        
                self.state = raiderStates.WALK
                    # pass # Raider have to set citizen in assaultMode
        elif self.state == raiderStates.ASSAULTING:
            self.victimIdentifier.state = citizenStates.ASSAULTED
            if self.countDownAssault == 0:
                self.state = raiderStates.WALK
                self.victimIdentifier.state = citizenStates.WALK
                # self.counDownNewAssault = 10
            else:
                self.countDownAssault-=1

        else:
            print("ERROR STATES!!!")
        print(self.state)
    def move_walk(self, speed=1):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius = speed
        )
        possible_steps = self.model.filterAvailableSpace(possible_steps)
        new_position = self.model.chooseUtils.closestPoint(possible_steps,self.destinationPoint)
        print(new_position)
        if(self.model.chooseUtils.distance_beetween_points(new_position,self.destinationPoint)<1):
            self.setNewDestination()
        self.model.grid.move_agent(self, new_position)
    def move_stalkin(self,speed=1):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius = speed
        )
        possible_steps = self.model.filterAvailableSpace(possible_steps)
        new_position = self.model.chooseUtils.closestPoint(possible_steps,self.victimIdentifier.pos)
        print(new_position)
        if(self.model.chooseUtils.distance_beetween_points(new_position,self.destinationPoint)<1):
            self.setNewDestination()
        self.model.grid.move_agent(self, new_position)
    def move_chasing(self):
        self.move_stalkin(2)
    def move_assaulting(self):
        pass