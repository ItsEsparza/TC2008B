# Code by Facundo Esparza GH: ItsEsparza
# Comments complemented by ChatGPT

import heapq
from mesa import Agent

class Roomba(Agent):
    def __init__(self, position, model, condition="Charged", battery=100):
        """
        Initialize the Roomba agent with position, model reference, condition, battery level, and other state-tracking attributes.
        """
        super().__init__(position, model)   
        self.position = position
        self.condition = condition
        self.battery = battery
        self.next_condition = None
        self.path = []  # Holds the path to the target
        self.low_battery_threshold = 30  # Threshold to start searching for a charging station
        self.recent_positions = set()  # Track recently visited positions to avoid repetition
        self.recent_positions_limit = 5  # Limit for recent positions memory
        self.moves = 0  # Count the moves made by the Roomba

    def verify_cell_type(self):
        """
        Check the current cell for dirt or a charging station. Clean if dirty, or recharge if at a charging station.
        """
        for agent in self.model.grid.get_cell_list_contents([self.position]):
            if isinstance(agent, tile) and agent.condition == "Dirty":
                agent.condition = "Cleaned"  # Clean the tile
                self.condition = "Exploring"  # Resume exploring
                break
        
        for agent in self.model.grid.get_cell_list_contents([self.position]):
            if isinstance(agent, ChargingStation):
                if self.battery < 100:
                    self.battery += 5  # Recharge battery by 5% per step
                    self.battery = min(self.battery, 100)  # Cap battery at 100%
                    self.condition = "Charging"
                if self.battery == 100:
                    self.condition = "Exploring"  # Resume exploring when fully charged
                break
        
    def step(self):
        """
        Called on each simulation step. Verifies cell type and moves if a path is available.
        """
        self.verify_cell_type()
        self.check_battery_and_move()

    def check_battery_and_move(self):
        """
        Check battery level; if low, prioritize finding a charging station, else move to the next target.
        """
        if self.battery <= self.low_battery_threshold and not self.is_charging_path():
            self.search_path(for_charging=True)  # Search for a charging station
        elif not self.path:  # If no path, search for a new target
            self.search_path()
        
        self.move()

    def is_charging_path(self):
        """
        Check if the current path leads to a charging station.
        """
        if not self.path:
            return False
        final_destination = self.path[-1]
        for agent in self.model.grid.get_cell_list_contents([final_destination]):
            if isinstance(agent, ChargingStation):
                return True
        return False

    def move(self):
        """
        Move the Roomba one step along its path unless it's charging and not fully charged.
        """
        if self.condition == "Charging" and self.battery < 100:
            return  # Remain stationary while charging

        if self.path:
            next_position = self.path.pop(0)
            if next_position != self.position:
                self.model.grid.move_agent(self, next_position)
                self.position = next_position
                self.moves += 1
                self.battery -= 1  # Decrease battery per move
                
                if self.battery <= 0:
                    self.condition = "Out of battery"
                    self.path = []
                
                if not self.path:
                    self.condition = "Idle"
                    self.recent_positions.clear()  # Reset recent positions when idle
        else:
            self.search_path()  # Look for a new path if path list is empty

    def search_path(self, for_charging=False):
        """
        Search for the nearest dirty tile or charging station using the A* algorithm.
        
        Args:
        for_charging: If True, only search for the nearest charging station.
        """
        targets = []
        for agent in self.model.schedule.agents:
            if for_charging and isinstance(agent, ChargingStation):
                distance = len(self.astar(self.position, agent.position))
                if distance > 0:  
                    targets.append((distance, agent.position))
            elif not for_charging and isinstance(agent, tile) and agent.condition == "Dirty":
                distance = len(self.astar(self.position, agent.position))
                if distance > 0 and agent.position not in self.recent_positions:  
                    targets.append((distance, agent.position))
        
        if targets:
            _, target_position = min(targets, key=lambda x: x[0])
            self.path = self.astar(self.position, target_position)
            self.recent_positions.add(target_position)
            if len(self.recent_positions) > self.recent_positions_limit:
                self.recent_positions.pop()

    def astar(self, start, goal):
        """
        A* algorithm to find the shortest path from start to goal.
        
        Args:
        start: The starting position (tuple).
        goal: The goal position (tuple).
        
        Returns:
        A list of tuples representing the path from start to goal, excluding the starting position.
        """
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        open_list = []
        heapq.heappush(open_list, (0 + heuristic(start, goal), 0, start, []))
        closed_set = set()

        while open_list:
            _, cost, current, path = heapq.heappop(open_list)
            
            if current == goal:
                return path[1:] + [goal]

            if current in closed_set:
                continue
            closed_set.add(current)

            neighbors = [
                (current[0] + 1, current[1]),
                (current[0] - 1, current[1]),
                (current[0], current[1] + 1),
                (current[0], current[1] - 1)
            ]

            for neighbor in neighbors:
                if self.model.grid.out_of_bounds(neighbor):
                    continue
                
                if any(isinstance(agent, Obstacle) for agent in self.model.grid.get_cell_list_contents(neighbor)):
                    continue
                
                if neighbor in closed_set:
                    continue

                new_cost = cost + 1
                heapq.heappush(open_list, (new_cost + heuristic(neighbor, goal), new_cost, neighbor, path + [current]))

        return []


class ChargingStation(Agent):
    """
    Charging Station agent that recharges the Roomba.
    """
    
    def __init__(self, position, model, condition="Not in use"):
        """
        Args:
        position: The cell's coordinates on the grid.
        model: Reference to the model instance.
        condition: "Not in use", "In use".
        """
        super().__init__(position, model)   
        self.position = position
        self.condition = condition
        self.next_condition = None
        
class Obstacle(Agent):
    """
    Obstacle agent that blocks the Roomba.
    """
    def __init__(self, position, model, condition="Placed"):
        """
        Args:
        position: The cell's coordinates on the grid.
        model: Reference to the model instance.
        condition: "Placed".
        """
        super().__init__(position, model)   
        self.position = position
        self.condition = condition
        self.next_condition = None
            
class tile(Agent):
    """
    Dirty tile agent representing a dirty spot on the floor.
    """
    def __init__(self, position, model, condition="Dirty"):
        """
        Args:
        position: The cell's coordinates on the grid.
        model: Reference to the model instance.
        condition: "Dirty".
        """
        super().__init__(position, model)
        self.position = position
        self.condition = condition
        self.next_condition = None
