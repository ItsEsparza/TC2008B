from mesa.visualization import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider

from model import RoombaModel, Roomba, ChargingStation, Obstacle, tile

def ground_portrayal(RoombaModel):
    
    if RoombaModel is None:
        return
    
    portrayal = {
        "Shape": "rect", 
        "w": 1, 
        "h": 1, 
        "Filled": "true", 
        "Layer": 0}
    
    if (isinstance(RoombaModel, Roomba)):
        portrayal["Shape"] = "Images/Roomba.png"

    if (isinstance(RoombaModel, tile)):
        if RoombaModel.condition == "Dirty":
            portrayal["Shape"] = "Images/Dirt.png"
        elif RoombaModel.condition == "Cleaned":
            portrayal["Color"] = "white"  # Make tile white if cleaned
            portrayal["Layer"] = 1       # Set to a higher layer to show above other agents
            portrayal["Shape"] = "rect"  # Shape to fill the tile completely
        
        
    if (isinstance(RoombaModel, Obstacle)):
        portrayal["Shape"] = "Images/Obstacle.png"
        
    if (isinstance(RoombaModel, ChargingStation)):
        portrayal["Shape"] = "Images/Charging_Stations.png"
        
    (x, y) = RoombaModel.pos
    portrayal["x"] = x
    portrayal["y"] = y
    
    return portrayal

canvas_elements = CanvasGrid(ground_portrayal, 15, 15, 500, 500)

model_params = {
    "height": 15,
    "width": 15,
    "density": Slider("Initial Dirtiness (%)", 20, 0, 100, 1),
    "obstacles": Slider("Obstacles", 1, 0, 25, 1),
    "roombas": Slider("Roombas", 1, 1, 25, 1),
    "Charging_Stations": Slider("Charging Stations", 1, 0, 25, 1)
    
}

battery_chart = ChartModule(
    [{"Label": "Average_Battery", "Color": "Black"}],
    data_collector_name='datacollector'
)

server = ModularServer(
    RoombaModel, [canvas_elements, battery_chart], "Roomba", model_params
)

server.launch(open_browser=False)