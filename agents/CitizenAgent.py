import mesa
from utils.utils import citizenStates, raiderStates, ChooseUtils, agentTypes
import requests
import json
# from RaiderAgent import RaiderAgent


class CitizenAgent(mesa.Agent):
    """An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, countDownSuspicion):
        super().__init__(unique_id, model)
        self.wealth = 1
        self.state = citizenStates.WALK
        self.destinationPoint = None
        self.chooseUtils = ChooseUtils() # Pass class to model
        self.countDownSuspicion = countDownSuspicion
        self.raiderIdentifier = None
        self.typeAgent = agentTypes.CITIZEN
        self.speed_citizen = model.speed_citizen
        self.lastPosition5Before = None
        self.completeObjetives = 0
        self.token_value = None
        self.initUserCredentials()

    def setNewDestination(self):
        # print("posicion es :",self.pos)
        temMax = self.model.grid.get_neighborhood(self.pos, moore=True, 
                                                        include_center=False, 
                                                        radius = self.model.distance_to_commute_citizen)
        temMin = self.model.grid.get_neighborhood(self.pos, moore=True, 
                                                        include_center=False, 
                                                        radius = self.model.distance_to_commute_citizen-2)
        
        possible_pos = list(set(temMax)-set(temMin))
        possible_pos = self.model.filterAvailableSpace(possible_pos)
        self.destinationPoint = self.random.choice(possible_pos)
        # print("Current Dest :",self.destinationPoint)


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
        if self.state == citizenStates.WALK:
            self.move_walk(self.speed_citizen)
        elif self.state == citizenStates.SUSPICION:
            self.move_suspicion(self.speed_citizen)
        elif self.state == citizenStates.PURSUED:
            self.move_pursued(self.speed_citizen+1)
        elif self.state == citizenStates.ASSAULTED:
            self.move_assaulted()
        else:
            print("FAIL STATE!!!")
        self.sendGPS2API()
        # if self.wealth > 0:
        #     self.give_money()

    def updateState(self):
        nearbyAgents = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius = self.model.distance_field_of_view_citizen
        )
        # print("ONLY GRID: ", field_of_view)
        if self.state == citizenStates.WALK:
            self.countDownSuspicion = 0
            self.raiderIdentifier = None
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.RAIDER and agent.state == raiderStates.STALKIN:
                    self.raiderIdentifier = agent
                    self.state = citizenStates.SUSPICION
        elif self.state == citizenStates.SUSPICION:
            flagRaiderClose = False
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.RAIDER and agent.state == raiderStates.STALKIN:
                    flagRaiderClose = True
                    if self.countDownSuspicion == 0:
                        self.state = citizenStates.PURSUED
                    else:
                        self.countDownSuspicion-=1
            if not flagRaiderClose:
                self.state = citizenStates.WALK
        elif self.state == citizenStates.PURSUED:
            flagRaiderClose = False
            for agent in nearbyAgents:
                if agent.typeAgent == agentTypes.RAIDER and agent.state == raiderStates.STALKIN:
                    flagRaiderClose = True
                    # if self.countDownSuspicion == 0:
                    #     self.state = citizenStates.PURSUED
                    # else:
                    #     self.countDownSuspicion-=1
            if not flagRaiderClose:
                self.state = citizenStates.SUSPICION
                    # pass # Raider have to set citizen in assaultMode
        elif self.state == citizenStates.ASSAULTED:
            pass
        else:
            print("ERROR STATES!!!")
        # print(self.state)
    def move_walk(self,speed = 1):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius = speed
        )
        possible_steps = self.model.filterAvailableSpace(possible_steps)
        new_position = self.chooseUtils.closestPoint(possible_steps,self.destinationPoint)
        # print(new_position)
        new_position = new_position if new_position is not None else self.pos
        if(self.chooseUtils.distance_beetween_points(new_position,self.destinationPoint)<1):
            self.setNewDestination()
            self.completeObjetives += 1
        elif (self.model.schedule.steps % 6 == 0):
            if self.lastPosition5Before is None:
                self.lastPosition5Before = self.pos
            else:
                if self.model.chooseUtils.distance_beetween_points(self.pos, self.lastPosition5Before) < 3:
                    self.setNewDestination()
                else:
                    self.lastPosition5Before = self.pos
        self.model.grid.move_agent(self, new_position)
    def move_suspicion(self,speed=1):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True, radius = speed
        )
        possible_steps = self.model.filterAvailableSpace(possible_steps)
        new_position = self.chooseUtils.furthestPoint(possible_steps,self.raiderIdentifier.pos)
        # print(new_position)
        if(self.chooseUtils.distance_beetween_points(new_position,self.destinationPoint)<1):
            self.setNewDestination()
        self.model.grid.move_agent(self, new_position)
    def move_pursued(self,speed = 2):
        self.move_suspicion(speed)
    def move_assaulted(self):
        pass # Keep same position

    def sendGPS2API(self):
        # url = "http://10.108.218.139:8080/api/checkpoints"
        url = "http://localhost:8080/api/checkpoints"
        payload = json.dumps({
            "userId": self.unique_id,
            "coordinates": {
                "x": self.pos[0],
                "y": self.pos[1]
            },
            "state": "ok"
        })
        headers = {
            'Authorization': f'Bearer {self.token_value}',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
    def initUserCredentials(self,host = 'localhost'):
        url = "http://" + host + ":8080/api/users/register"
        payload = json.dumps({
            "firstName": f"User_{self.unique_id}",
            "lastName": f"Citizen_{self.unique_id}",
            "email": f"user{self.unique_id}@testmail.com",
            "password": f"testPass{self.unique_id}"
        })
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            self.extracToken(response)
        elif response.status_code == 401:
            url = "http://" + host + ":8080/api/users/login"
            payload = json.dumps({
                "email": f"user{self.unique_id}@testmail.com",
                "password": f"testPass{self.unique_id}"
            })
            response = requests.request("POST", url, headers=headers, data=payload)
            self.extracToken(response)
    def extracToken(self,response):
        try:
            self.token_value = response.json()["token"]
            # print("Token extraído:", token_value)
        except KeyError:
            raise Exception("La clave 'token' no se encuentra en la respuesta")

