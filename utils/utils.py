import json
import requests
from enum import Enum
import math
def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_citizen
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x)+1)
    return 1 + (1 / (N+1)) - 2 * B

def compute_gini(model):
    agent_wealths = [agent.wealth for agent in model.schedule.agents]
    x = sorted(agent_wealths)
    N = model.num_citizen
    B = sum(xi * (N - i) for i, xi in enumerate(x)) / (N * sum(x)+1)
    return 1 + (1 / (N+1)) - 2 * B



class ChooseUtils():
    def __init__(self):
        pass
    def distance_beetween_points(self,coord1, coord2):
        """Calcula la distancia euclidiana entre dos puntos."""
        return math.sqrt((coord2[0] - coord1[0])**2 + (coord2[1] - coord1[1])**2)

    def furthestPoint(self,coordenadas, punto_b):
        """Encuentra el punto más lejano de la lista con respecto a un punto dado."""
        if not coordenadas:
            return None  # Retorna None si la lista está vacía

        punto_mas_lejano = coordenadas[0]
        distancia_maxima = self.distance_beetween_points(coordenadas[0], punto_b)

        for punto in coordenadas[1:]:
            distancia = self.distance_beetween_points(punto, punto_b)
            if distancia > distancia_maxima:
                distancia_maxima = distancia
                punto_mas_lejano = punto

        return punto_mas_lejano
    def closestPoint(self,coordenadas, punto_b):
        """Encuentra el punto más cercano de la lista con respecto a un punto dado."""
        if not coordenadas:
            return None  # Retorna None si la lista está vacía 

        punto_mas_cercano = coordenadas[0]
        distancia_minima = self.distance_beetween_points(coordenadas[0], punto_b)

        for punto in coordenadas[1:]:
            distancia = self.distance_beetween_points(punto, punto_b)
            if distancia <= distancia_minima:
                distancia_minima = distancia
                punto_mas_cercano = punto

        return punto_mas_cercano

class citizenStates(Enum):
    WALK = 0
    SUSPICION = 1
    PURSUED = 2
    ASSAULTED = 3

class raiderStates(Enum):
    WALK = 0
    STALKIN = 1
    CHASING = 2
    ASSAULTING = 3
    ESCAPE = 4
class agentTypes(Enum):
    RAIDER = 0
    CITIZEN = 1
    WALL = 2

