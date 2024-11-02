from mesa.visualization import CanvasGrid, ChartModule, PieChartModule
from mesa.visualization import ModularServer
from mesa.visualization import Slider

from model import DeadOrAlive

# The colors of the portrayal will depend on cell condition.
COLORS = {"Alive": "#000000", "Dead": "#ffffff"}

def Dead_Or_Alive_Portrayal(cell):
    if cell is None:
        return
    portrayal = {"Shape": "rect", "w": 1, "h": 1, "Filled": "true", "Layer": 0}
    (x, y) = cell.pos
    portrayal["x"] = x
    portrayal["y"] = y
    portrayal["Color"] = COLORS[cell.condition]
    
    return portrayal
    
canvas_elements = CanvasGrid(Dead_Or_Alive_Portrayal, 50, 50, 500, 500)

# Set up a line chart to track the number of "Alive" and "Dead" cells over time
cell_chart = ChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

# Set up a pie chart to show the distribution of "Alive" and "Dead" cells at the current step
pie_chart = PieChartModule(
    [{"Label": label, "Color": color} for label, color in COLORS.items()]
)

# Define sliders and parameters for the model
model_params = {
    "height": 50,
    "width": 50,
    "density": Slider("Initial Alive Density", 0.2, 0.01, 1.0, 0.01),
}

# Initialize the server with the model, visual elements, and parameters
server = ModularServer(
    DeadOrAlive, [canvas_elements, cell_chart, pie_chart], "Dead or Alive", model_params
)

# Launch the server
server.launch()