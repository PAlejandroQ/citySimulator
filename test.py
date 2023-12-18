from model import MoneyModel
model = MoneyModel(1,1,70,70,10,10,30,30,1,1,3,3,3,"testImg.png")
for i in range(30):
    model.step()
    print(model.schedule.steps)