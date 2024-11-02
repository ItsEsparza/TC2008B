import mesa
from mesa import Model, DataCollector
from mesa.space import SingleGrid
from mesa.time import SimultaneousActivation 

from agent import TestCell

class DeadOrAlive(Model):
    """
    Model class for the Dead or Alive model.
    Attributes:
        height, width: Grid size.
        density: Threshold to determine initial Alive cells.
    """
    
    def __init__(self, height=50, width=50, density=0.2):
        """
        Create a grid of dead and alive cells.
        
        Args:
            height, width: The size of the grid to model
            density: Threshold probability for cells to start as Alive.
        """
        
        self.schedule = SimultaneousActivation(self)
        self.grid = SingleGrid(height, width, torus=False)
        
        self.datacollector = DataCollector(
            {
                "Alive": lambda m: self.count_type(m, "Alive"),
                "Dead": lambda m: self.count_type(m, "Dead"),
            }
        )
        
        for contents, (x, y) in self.grid.coord_iter():
            
                # Determine cell's initial state based on the density threshold
                if self.random.random() < density and y == 49:
                    # Set cell as alive if random value is below the threshold density
                    new_cell = TestCell((x, y), self, condition="Alive")
                else:
                    # Set cell as dead if random value is above the threshold density
                    new_cell = TestCell((x, y), self, condition="Dead")
                    
                # Place the cell in the grid and add it to the schedule
                self.grid.place_agent(new_cell, (x, y))
                self.schedule.add(new_cell)
                
        self.running = True
        self.datacollector.collect(self)
        
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
