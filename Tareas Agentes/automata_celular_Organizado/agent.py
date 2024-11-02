from mesa import Agent

class TestCell(Agent):
    
    _nextState = {
        #0 = Dead, 1 = Alive
        (1, 1, 1): "Dead",
        (1, 1, 0): "Alive",
        (1, 0, 1): "Dead",
        (1, 0, 0): "Alive",
        (0, 1, 1): "Alive",
        (0, 1, 0): "Dead",
        (0, 0, 1): "Alive",
        (0, 0, 0): "Dead"
    }
    
    def __init__(self, position, model, condition="Alive"):
        super().__init__(position, model)
        self.position = position
        self.condition = condition
        self._next_condition = None 

    def step(self):
        x, y = self.position
        
        # Ignore limits of the grid
        if x == 0 or x == self.model.grid.width - 1 or y == 49:
            self._next_condition = self.condition
            return
        
        # Get neighbors
        neighbors = [
            self.model.grid.get_cell_list_contents([(x - 1, y + 1)]),
            self.model.grid.get_cell_list_contents([(x, y + 1)]),
            self.model.grid.get_cell_list_contents([(x + 1, y + 1)])
        ]

        # Convert neighbors to 1 or 0 to use dictionary
        neighbor_conditions = tuple(1 if n[0].condition == "Alive" else 0 for n in neighbors if n)

        # Get next state from dictionary
        self._next_condition = self._nextState.get(neighbor_conditions, self.condition)

    def advance(self):
        if self._next_condition is not None:
            self.condition = self._next_condition
            self._next_condition = None
