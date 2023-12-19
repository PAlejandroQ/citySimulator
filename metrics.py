from utils import agentTypes, raiderStates, citizenStates


# import numpy as np

# objCom = Objetivos completados
# numCi = Numero de civiles
# ciSu = Numero de civiles que sospechan
# ciPur = Numero de civiles que son perseguidos
# ciSssa = Numero de civiles que son asaltados
#
# raSta = Numero de atacantes que asechan
# raCha = Numero de atacantes que persiguen
# raAssa = Numero de atacantes que asaltan
# surVic = victimas sorprendidas

def objetivosCompletados(model):
    agent_objetives = [agent.completeObjetives for agent in model.schedule.agents
                       if agent.typeAgent == agentTypes.CITIZEN]
    if model.num_citizen == 0:
        return model.metric_values_acum["objetivosCompletados"]
    agent_objetives = sum(agent_objetives) * 1.0 # / model.num_citizen
    model.metric_values_acum["objetivosCompletados"] += agent_objetives
    return model.metric_values_acum["objetivosCompletados"]


def persecucionesFallidas(model):
    raCha = [agent for agent in model.schedule.agents
             if agent.state == raiderStates.CHASING]
    raAssa = [agent for agent in model.schedule.agents
              if agent.state == raiderStates.ASSAULTING]
    if len(raCha) == 0:
        return model.metric_values_acum["persecucionesFallidas"]
    temp = (len(raCha) - len(raAssa)) * 1.0 # / len(raCha)
    model.metric_values_acum["persecucionesFallidas"] += temp
    return model.metric_values_acum["persecucionesFallidas"]


def asechoFallido(model):
    raCha = [agent for agent in model.schedule.agents
             if agent.state == raiderStates.CHASING]
    raSta = [agent for agent in model.schedule.agents
             if agent.state == raiderStates.STALKIN]
    if len(raSta) == 0:
        return model.metric_values_acum["asechoFallido"]
    temp = (len(raSta) - len(raCha)) * 1.0 # / len(raSta)
    model.metric_values_acum["asechoFallido"] += temp
    return model.metric_values_acum["asechoFallido"]


def asechoDetectado(model):
    cisu = [agent for agent in model.schedule.agents
            if agent.state == citizenStates.SUSPICION]
    raSta = [agent for agent in model.schedule.agents
             if agent.state == raiderStates.STALKIN]
    if len(raSta) == 0:
        return model.metric_values_acum["asechoDetectado"]
    temp = (len(cisu) - len(raSta)) * -1.0 # / len(raSta)
    model.metric_values_acum["asechoDetectado"] += temp
    return model.metric_values_acum["asechoDetectado"]


def persecucionDetectada(model):
    raCha = [agent for agent in model.schedule.agents
             if agent.state == raiderStates.CHASING]
    ciPur = [agent for agent in model.schedule.agents
             if agent.state == citizenStates.PURSUED]
    if len(raCha) == 0:
        return model.metric_values_acum["persecucionDetectada"]
    tem = (len(raCha) - len(ciPur)) * 1.0 # / len(raCha)
    model.metric_values_acum["persecucionDetectada"] += tem
    return model.metric_values_acum["persecucionDetectada"]


def victimasSorprendidas(model):
    raAssa = [agent for agent in model.schedule.agents
              if agent.state == raiderStates.ASSAULTING]
    surVic = [agent for agent in model.schedule.agents
              if agent.typeAgent == agentTypes.RAIDER]
    if len(raAssa) == 0:
        return model.metric_values_acum["victimasSorprendidas"]
    temp = len(surVic) * 1.0 # / len(raAssa)
    model.metric_values_acum["victimasSorprendidas"] += temp
    return model.metric_values_acum["victimasSorprendidas"]
