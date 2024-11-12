import heapq  # for priority queue
from mesa import Agent

class Roomba(Agent):
    def __init__(self, position, model, condition="Charged", battery=100):
        super().__init__(position, model)   
        self.position = position
        self.condition = condition
        self.battery = battery
        self.next_condition = None
        self.path = []  
        self.low_battery_threshold = 30  
        self.recent_positions = set()  # Track recent positions to avoid loops
        self.recent_positions_limit = 5  # Limit memory of visited positions

    def verify_cell_type(self):
        """
        Check if the Roomba is on a dirty tile and clean it, or on a charging station and recharge.
        """
        for agent in self.model.grid.get_cell_list_contents([self.position]):
            if isinstance(agent, tile) and agent.condition == "Dirty":
                print(f"[Tile] Cleaning tile at {self.position}")
                agent.condition = "Cleaned"  # Mark the tile as cleaned
                self.condition = "Exploring"
                break
        
        for agent in self.model.grid.get_cell_list_contents([self.position]):
            if isinstance(agent, ChargingStation):
                print(f"[Charging] Reached charging station at {self.position}. Battery recharged.")
                self.condition = "Charging"
                self.battery = 100  
                break

    def step(self):
        """
        Called on each simulation step. Verifies cell type and moves if path is available.
        """
        print(f"[Step] Position: {self.position}, Battery: {self.battery}, Condition: {self.condition}, Path: {self.path}")
        self.verify_cell_type()
        self.check_battery_and_move()

    def check_battery_and_move(self):
        """
        Check battery level and prioritize finding a charging station if battery is low.
        """
        if self.battery <= self.low_battery_threshold and not self.is_charging_path():
            print(f"[Low Battery] Battery: {self.battery}. Prioritizing charging station.")
            self.search_path(for_charging=True)  
        elif not self.path:  # If no path is set, search for a target
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
        Move the Roomba one step along its path. If it reaches the target, clear the path.
        """
        if self.path:
            next_position = self.path.pop(0)
            if next_position != self.position:
                print(f"[Move] Moving from {self.position} to {next_position}")
                self.model.grid.move_agent(self, next_position)
                self.position = next_position  # Update position to prevent teleporting issues
                self.battery -= 1  # Decrease battery per move
                
                if self.battery <= 0:
                    print("[Battery] Out of battery.")
                    self.condition = "Out of battery"
                    self.path = []  
                
                if not self.path:
                    print("[Path] Reached destination. Path cleared.")
                    self.condition = "Idle"
                    self.recent_positions.clear()  # Reset recent positions when reaching a destination
        else:
            print("[Search] No path found. Searching for a new target.")
            self.search_path()  

    def search_path(self, for_charging=False):
        """
        Search for the nearest dirty tile or charging station.
        Uses A* algorithm to find the shortest path.
        Args:
        for_charging: If True, only searches for the nearest charging station.
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
            print(f"[Path Search] Nearest target selected at {target_position}")
            self.path = self.astar(self.position, target_position)
            self.recent_positions.add(target_position)
            if len(self.recent_positions) > self.recent_positions_limit:
                self.recent_positions.pop()
        else:
            print("[Path Search] No reachable targets found.")

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
                print(f"[A*] Path found to goal: {goal}")
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

        print("[A*] No path found to goal.")
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
    Dirty tile.
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
