# Code by Facundo Esparza GH: ItsEsparza
# Comments complemented by ChatGPT

from mesa.visualization import CanvasGrid, ChartModule, BarChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider

from model import RoombaModel, Roomba, ChargingStation, Obstacle, tile

def ground_portrayal(RoombaModel):
    """
    Define how each type of agent (Roomba, tile, Obstacle, ChargingStation) is visually represented on the grid.
    """
    if RoombaModel is None:
        return
    
    # Default portrayal settings for grid cells
    portrayal = {
        "Shape": "rect", 
        "w": 1, 
        "h": 1, 
        "Filled": "true", 
        "Layer": 0
    }
    
    # Representation for a Roomba
    if isinstance(RoombaModel, Roomba):
        portrayal["Shape"] = "Images/Roomba.png"

    # Representation for a tile, depending on its condition
    if isinstance(RoombaModel, tile):
        if RoombaModel.condition == "Dirty":
            portrayal["Shape"] = "Images/Dirt.png"
        elif RoombaModel.condition == "Cleaned":
            portrayal["Color"] = "white"  # Color for cleaned tile
            portrayal["Layer"] = 1        # Set layer to show above other agents
            portrayal["Shape"] = "rect"   # Shape fills the entire cell

    # Representation for an Obstacle
    if isinstance(RoombaModel, Obstacle):
        portrayal["Shape"] = "Images/Obstacle.png"
        
    # Representation for a Charging Station
    if isinstance(RoombaModel, ChargingStation):
        portrayal["Shape"] = "Images/Charging_Stations.png"
        
    # Set the position of the portrayal on the grid
    (x, y) = RoombaModel.pos
    portrayal["x"] = x
    portrayal["y"] = y
    
    return portrayal

# Define the grid display settings
canvas_elements = CanvasGrid(ground_portrayal, 15, 15, 500, 500)

# Model parameters with sliders to adjust settings before running the model
model_params = {
    "height": 15,
    "width": 15,
    "density": Slider("Initial Dirtiness (% of grid)", 20, 0, 100, 1),
    "obstacles": Slider("Obstacles (% of grid)", 10, 0, 100, 1),
    "roombas": Slider("Roombas", 1, 1, 25, 1),
    "max_steps": Slider("Max Steps", 300, 10, 1000, 1)
}

# Chart to show the percentage of cleaned vs. dirty tiles over time
CleanedP_chart = ChartModule([{"Label": "Dirty (%)", "Color": "Red"},
                                {"Label": "Cleaned (%)", "Color": "Green"}],
                                data_collector_name='datacollector')

# Bar chart to display the number of moves made by each Roomba
Moves_chart = BarChartModule([{"Label": "Moves", "Color": "Black"}],
                                data_collector_name='datacollector')

# Set up and launch the server for the model with the grid, charts, and parameters
server = ModularServer(
    RoombaModel, [canvas_elements, CleanedP_chart, Moves_chart], "Roomba", model_params
)

server.launch(open_browser=False) #Prevent browser launching on each file save
