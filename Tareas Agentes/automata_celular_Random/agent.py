from mesa import Agent

class TestCell(Agent):
    
    _nextState = {  # Next state of the cell
        (1,1,1): "Dead",
        (1,1,0): "Alive",
        (1,0,1): "Dead",
        (1,0,0): "Alive",
        (0,1,1): "Alive",
        (0,1,0): "Dead",
        (0,0,1): "Alive",
        (0,0,0): "Dead"
    }
        
    """
    White or black cell
    Black means cell is alive
    White means cell is dead
    """
    
    def __init__(self, position, model, condition="Alive"):
        """
        Args:
        position: The cell's coordinates on the grid.
        model: Standard model reference for agent.
        condition: Initial state of the cell, "Alive" or "Dead".
        """
        super().__init__(position, model)   
        self.position = position
        self.condition = condition  # Initialize with the provided condition
        self._next_condition = None
        
    def step(self):
        """Logic for next cell to become alive or dead."""
        
        neighbors = []
        
        # Get the y-position with wrapping
        wrapped_positions = [
            ((self.position[0] - 1), (self.position[1] - 1) % self.model.grid.height),  # Top left neighbor
            (self.position[0], (self.position[1] - 1) % self.model.grid.height),       # Top center neighbor
            ((self.position[0] + 1), (self.position[1] - 1) % self.model.grid.height)  # Top right neighbor
        ]
        
        # Collect neighbors only if they exist within the grid bounds
        for pos in wrapped_positions:
            if 0 <= pos[0] < self.model.grid.width:
                neighbor = self.model.grid[pos[0]][pos[1]]
                neighbors.append(neighbor)
                
        
        if len(neighbors) == 3:  # Verify if there are enough neighbors to determine the next state
            neighbor_states = tuple(1 if n.condition == "Alive" else 0 for n in neighbors)
            self._next_condition = self._nextState.get(neighbor_states, "Dead")
        else:
            self._next_condition = self.condition
            
            
    def advance(self):
        """Update the cell condition in the next step."""
        if self._next_condition is not None:
            self.condition = self._next_condition
