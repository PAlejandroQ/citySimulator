from model import CityModel
model_params = {
    "num_citizen": 50 ,
    "num_raider": 4,
    "width": 70, # If pathMap is not None, this value doesn't matter
    "height": 70, # If pathMap is not None, this value doesn't matter
    "distance_to_commute_citizen": 30,
    "distance_to_commute_raider": 30,
    "distance_field_of_view_citizen":12,
    "distance_field_of_view_raider":12,
    "speed_citizen":1,
    "speed_raider":1,
    "countDownSuspicion":4,
    "countDownChase":6,
    "minCitizenToStalk":2, # Itera
    # "pathMap":"testImg.png",
    "pathMap":"mapsImage/mapReadyFinal.png",
    "thresholdMap":244
}
# model = CityModel(1, 1, 70, 70, 10, 10, 30, 30, 1, 1, 3, 3, 3, "mapsImage/testImg.png")
model = CityModel(**model_params)
for i in range(5):
    model.step()
    # print(model.schedule.steps)

gini = model.datacollector.get_model_vars_dataframe()