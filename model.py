import mesa
import seaborn as sns
import numpy as np
import pandas as pd
import requests
import json
from CitizenAgent import CitizenAgent
from RaiderAgent import RaiderAgent
from utils import compute_gini, ChooseUtils
from imageProcessing import procesar_imagen
from WallAgent import WallAgent


class MoneyModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_citizen, num_raider ,width, 
                 height,distance_to_commute,distance_field_of_view, 
                 countDownSuspicion, countDownChase,
                 minCitizenToStalk,pathMap = None, thresholdMap = 244):
        self.num_citizen = num_citizen
        self.num_raider = num_raider
        # self.grid = mesa.space.SingleGrid(width, height, False)
        self.schedule = mesa.time.RandomActivation(self)
        self.chooseUtils = ChooseUtils()
        self.running = True
        self.distance_to_commute = distance_to_commute
        self.distance_field_of_view = distance_field_of_view
        self.countDownSuspicion = countDownSuspicion 
        self.countDownChase = countDownChase
        self.minCitizenToStalk = minCitizenToStalk

        # Create city
        if pathMap is not None:
            indexMap = self.num_citizen + self.num_raider
            matrix_map = procesar_imagen(pathMap,thresholdMap)
            self.grid = mesa.space.SingleGrid(matrix_map.shape[0], matrix_map.shape[1], False)
            for i in range(matrix_map.shape[0]):
                for j in range(matrix_map.shape[1]):
                    if matrix_map[i,j] == '#':
                        wall = WallAgent(indexMap,self)
                        indexMap += 1
                        self.schedule.add(wall)
                        self.grid.place_agent(wall,(i,j))
        else:
            self.grid = mesa.space.SingleGrid(width, height, False)



        # Create Citizen
        
        for i in range(self.num_citizen):
            a = CitizenAgent(i, self, self.countDownSuspicion) # Each agent have their own countDown
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x,y = self.randomEmptyPlace()
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            a.setNewDestination()

        # Create Raider
        for i in range(self.num_citizen,self.num_citizen+self.num_raider):
            a = RaiderAgent(i, self,self.countDownChase)
            self.schedule.add(a)
            # Add the agent to a random grid cell
            x,y = self.randomEmptyPlace()
            # x = self.random.randrange(self.grid.width)
            # y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            a.setNewDestination()

        self.datacollector = mesa.DataCollector(
            model_reporters={"Gini": compute_gini}, 
            agent_reporters={"Wealth": "wealth"}
        )
        print("Holaaaaa")

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        # print("Schedulando")
    def filterAvailableSpace(self,potentialPoints, onlyGridIn = False):
        if onlyGridIn:
            return [pos for pos in potentialPoints 
                    if not self.model.grid.out_of_bounds(pos)]
        else:
            return [pos for pos in potentialPoints 
                    if not self.grid.out_of_bounds(pos) 
                    and self.grid.is_cell_empty(pos)]
    def randomEmptyPlace(self):
        posiciones_vacias = [(i, j) for i in range(self.grid.width) for j in range(self.grid.height) if self.grid.is_cell_empty((i,j))]
        
        if posiciones_vacias:
            return self.random.choice(posiciones_vacias)
        else:
            print("ALERT FULL MAP!!!")
            return None