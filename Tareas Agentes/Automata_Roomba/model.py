import mesa
from mesa import Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation 
from statistics import mean

from agent import Roomba, ChargingStation, Obstacle, tile

class RoombaModel(Model):
    """
    Creates the grid and places the agents
    """
    
    def __init__(self, height=15, width=15, density=20, roombas = 5, obstacles = 5, Charging_Stations = 5):
        super().__init__()  # Initialize the base Model class
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, torus=False)
        self.running = True
        
        self.datacollector = DataCollector(
            {
                "Dirty": lambda m: self.count_type(m, "Dirty"),
                "Average_Battery": lambda m: mean([roomba.battery for roomba in m.schedule.agents if isinstance(roomba, Roomba)])
            }
        )

        tile_id = 0
        for contents, (x, y) in self.grid.coord_iter():
            if self.random.random() < (density/100):
                new_tile = tile((x, y), self, condition="Dirty")
                tile_id += 1
                self.grid.place_agent(new_tile, (x, y))
                self.schedule.add(new_tile)
                
        roomba_id = 250
        while roomba_id < 250 + roombas: #Prevent lower number of roombas due to randomness
            for contents, (x, y) in self.grid.coord_iter():
                if self.random.random() < (roombas/100) and self.grid.is_cell_empty((x, y)):
                    new_roomba = Roomba((x, y), self, condition="Charged")
                    roomba_id += 1
                    self.grid.place_agent(new_roomba, (x, y))
                    self.schedule.add(new_roomba)
                    if roomba_id == 250 + roombas:
                        break
                
        Obstacle_id = 500
        while Obstacle_id < 500 + obstacles:
            for contents, (x, y) in self.grid.coord_iter():
                if self.random.random() < (obstacles/100) and self.grid.is_cell_empty((x, y)):
                    new_obstacle = Obstacle((x, y), self, condition="Placed")
                    Obstacle_id += 1
                    self.grid.place_agent(new_obstacle, (x, y))
                    self.schedule.add(new_obstacle)
                    if Obstacle_id == 500 + obstacles:
                        break
                
        Charging_Stations_ID = 750
        while Charging_Stations_ID < 750 + Charging_Stations:
            for contents, (x, y) in self.grid.coord_iter():
                if self.random.random() < (Charging_Stations/100) and self.grid.is_cell_empty((x, y)):
                    new_charging_station = ChargingStation((x, y), self, condition="Not in use")
                    Charging_Stations_ID += 1
                    self.grid.place_agent(new_charging_station, (x, y))
                    self.schedule.add(new_charging_station)
                    if Charging_Stations_ID == 750 + Charging_Stations:
                        break

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        self.datacollector.collect(self)
    
    @staticmethod
    def count_type(model, cell_condition):
        """
        Helper method to count cells in a given condition in a given model.
        """
        count = 0
        for cell in model.schedule.agents:
            if cell.condition == cell_condition:
                count += 1
        return count