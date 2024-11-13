# Code by Facundo Esparza GH: ItsEsparza
# Comments complemented by ChatGPT

import mesa
from mesa import Model, DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from agent import Roomba, ChargingStation, Obstacle, tile

class RoombaModel(Model):
    """
    Model representing the environment with a grid, Roombas, charging stations, obstacles, and tiles.
    """

    def __init__(self, height=15, width=15, density=20, roombas=5, obstacles=5, max_steps=300):
        """
        Initialize the RoombaModel with specified grid size, density of dirty tiles, 
        number of Roombas, and number of obstacles.
        """
        super().__init__()  # Initialize the base Model class
        self.schedule = RandomActivation(self)  # Scheduler for managing agent actions
        self.grid = MultiGrid(height, width, torus=False)  # Initialize the grid
        self.running = True
        self.step_count = 0
        self.max_steps = max_steps
        charging_stations = roombas  # Set the number of charging stations equal to the number of Roombas

        # DataCollector to track the percentage of cleaned and dirty tiles, and Roomba moves
        self.datacollector = DataCollector(
            {
                "Cleaned (%)": lambda m: self.count_type(m, "Cleaned") / (self.count_type(m, "Dirty") + self.count_type(m, "Cleaned")) * 100,
                "Dirty (%)": lambda m: self.count_type(m, "Dirty") / (self.count_type(m, "Dirty") + self.count_type(m, "Cleaned")) * 100,
                "Moves": lambda m: [roomba.moves for roomba in m.schedule.agents if isinstance(roomba, Roomba)]
            }
        )

        # Place dirty tiles based on the specified density
        tile_id = 0
        for contents, (x, y) in self.grid.coord_iter():
            if self.random.random() < (density / 100):
                new_tile = tile((x, y), self, condition="Dirty")
                tile_id += 1
                self.grid.place_agent(new_tile, (x, y))
                self.schedule.add(new_tile)

        # Special case for a single Roomba placed at (1,1) with a charging station
        if roombas == 1:
            new_charging_station = ChargingStation((1, 1), self, condition="Not in use")
            self.grid.place_agent(new_charging_station, (1, 1))
            self.schedule.add(new_charging_station)
            
            new_roomba = Roomba((1, 1), self, condition="Charged")
            self.grid.place_agent(new_roomba, (1, 1))
            self.schedule.add(new_roomba)
        else:
            # Place multiple charging stations randomly
            charging_positions = []
            charging_stations_id = 750  # Arbitrary ID start point for charging stations
            while charging_stations_id < 750 + charging_stations:
                for contents, (x, y) in self.grid.coord_iter():
                    if self.random.random() < (charging_stations / 100) and self.grid.is_cell_empty((x, y)):
                        new_charging_station = ChargingStation((x, y), self, condition="Not in use")
                        charging_stations_id += 1
                        self.grid.place_agent(new_charging_station, (x, y))
                        self.schedule.add(new_charging_station)
                        charging_positions.append((x, y))
                        if charging_stations_id == 750 + charging_stations:
                            break

            # Place Roombas on charging stations
            for i in range(min(roombas, len(charging_positions))):
                position = charging_positions[i]
                new_roomba = Roomba(position, self, condition="Charged")
                self.grid.place_agent(new_roomba, position)
                self.schedule.add(new_roomba)

        # Place obstacles randomly across the grid
        obstacle_id = 500  # Arbitrary ID start point for obstacles
        while obstacle_id < 500 + obstacles:
            for contents, (x, y) in self.grid.coord_iter():
                if self.random.random() < (obstacles / 100) and self.grid.is_cell_empty((x, y)):
                    new_obstacle = Obstacle((x, y), self, condition="Placed")
                    obstacle_id += 1
                    self.grid.place_agent(new_obstacle, (x, y))
                    self.schedule.add(new_obstacle)
                    
        # Place clean tiles on empty cells with no agents
        for contents, (x, y) in self.grid.coord_iter():
            if self.grid.is_cell_empty((x, y)):
                new_tile = tile((x, y), self, condition="Cleaned")
                self.grid.place_agent(new_tile, (x, y))
                self.schedule.add(new_tile)

    def step(self):
        """
        Advance the model by one step, collecting data and activating agents.
        """
        self.schedule.step()
        self.datacollector.collect(self)
        self.step_count += 1
        # Stop the simulation if all tiles are cleaned or max steps are reached
        if self.count_type(self, "Dirty") == 0 or self.step_count >= self.max_steps:
            self.running = False  # Stops the simulation
    
    @staticmethod
    def count_type(model, cell_condition):
        """
        Helper method to count cells in a specific condition within the model.
        
        Args:
        model: The model instance.
        cell_condition: The condition to count (e.g., "Cleaned", "Dirty").
        
        Returns:
        count: Number of cells with the specified condition.
        """
        count = 0
        for cell in model.schedule.agents:
            if cell.condition == cell_condition:
                count += 1
        return count
