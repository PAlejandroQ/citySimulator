import mesa
from agents.CitizenAgent import CitizenAgent
from agents.RaiderAgent import RaiderAgent
from utils.metrics import *
from utils.utils import ChooseUtils
from utils.imageProcessing import procesar_imagen
from agents.WallAgent import WallAgent
import requests
import json


class CityModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_citizen, num_raider, width,
                 height, distance_to_commute_citizen, distance_to_commute_raider,
                 distance_field_of_view_citizen, distance_field_of_view_raider,
                 speed_citizen, speed_raider,
                 countDownSuspicion, countDownChase,
                 minCitizenToStalk, pathMap=None, thresholdMap=244, use_system=False):
        self.num_citizen = num_citizen
        self.num_raider = num_raider
        # self.grid = mesa.space.SingleGrid(width, height, False)
        self.schedule = mesa.time.RandomActivation(self)
        self.chooseUtils = ChooseUtils()
        self.running = True
        self.distance_to_commute_citizen = distance_to_commute_citizen
        self.distance_to_commute_raider = distance_to_commute_raider
        self.distance_field_of_view_citizen = distance_field_of_view_citizen
        self.distance_field_of_view_raider = distance_field_of_view_raider
        self.countDownSuspicion = countDownSuspicion
        self.countDownChase = countDownChase
        self.minCitizenToStalk = minCitizenToStalk
        self.speed_citizen = speed_citizen
        self.speed_raider = speed_raider
        self.use_system = use_system

        self.metric_values_acum = {"objetivosCompletados": 0,
                                   "persecucionesFallidas": 0,
                                   "asechoFallido": 0,
                                   "asechoDetectado": 0,
                                   "persecucionDetectada": 0,
                                   "victimasSorprendidas": 0}

        # Create city
        if pathMap is not None:
            indexMap = self.num_citizen + self.num_raider
            matrix_map = procesar_imagen(pathMap, thresholdMap)
            self.grid = mesa.space.SingleGrid(matrix_map.shape[0], matrix_map.shape[1], False)
            print("Map size: ", (matrix_map.shape[0], matrix_map.shape[1]))
            for i in range(matrix_map.shape[0]):
                for j in range(matrix_map.shape[1]):
                    if matrix_map[i, j] == '#':
                        wall = WallAgent(indexMap, self)
                        indexMap += 1
                        # self.schedule.add(wall)
                        self.grid.place_agent(wall, (i, j))
        else:
            self.grid = mesa.space.SingleGrid(width, height, False)

        # Create Citizen

        for i in range(self.num_citizen):
            a = CitizenAgent(i, self, self.countDownSuspicion)  # Each agent have their own countDown
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x, y = self.randomEmptyPlace()
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            a.setNewDestination()

        # Create Raider
        for i in range(self.num_citizen, self.num_citizen + self.num_raider):
            a = RaiderAgent(i, self, self.countDownChase)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x, y = self.randomEmptyPlace()
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            a.setNewDestination()

        self.datacollector = mesa.DataCollector(
            # model_reporters={"objetivosCompletados": objetivosCompletados,
            #                  "persecucionesFallidas": persecucionesFallidas,
            #                  "asechoFallido":asechoFallido,
            #                  "asechoDetectado":asechoDetectado,
            #                  "persecucionDetectada":persecucionDetectada,
            #                  "victimasSorprendidas":victimasSorprendidas},
            # agent_reporters={"Wealth": "wealth"}
            model_reporters={"asaltosRealizados": asaltosRealizados}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()

    def filterAvailableSpace(self, potentialPoints, onlyGridIn=False):
        if onlyGridIn:
            return [pos for pos in potentialPoints
                    if not self.model.grid.out_of_bounds(pos)]
        else:
            return [pos for pos in potentialPoints
                    if not self.grid.out_of_bounds(pos)
                    and self.grid.is_cell_empty(pos)]

    def randomEmptyPlace(self):
        posiciones_vacias = [(i, j) for i in range(self.grid.width) for j in range(self.grid.height) if
                             self.grid.is_cell_empty((i, j))]

        if posiciones_vacias:
            return self.random.choice(posiciones_vacias)
        else:
            print("ALERT FULL MAP!!!")
            return None
