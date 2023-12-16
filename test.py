from model import MoneyModel
model = MoneyModel(1,1,70,70,10,30,3,3,3,"testImg.png")
for i in range(30):
    model.step()