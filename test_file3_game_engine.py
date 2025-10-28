"""
Game Engine Example - Simple 2D game engine architecture
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import math
import time


class EventType(Enum):
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"
    MOUSE_CLICK = "mouse_click"
    COLLISION = "collision"
    TICK = "tick"


@dataclass
class Event:
    """Game event"""
    type: EventType
    data: Dict[str, Any]
    timestamp: float = 0.0


class Vector2:
    """2D Vector class"""

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = x
        self.y = y

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)

    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def normalize(self) -> 'Vector2':
        mag = self.magnitude()
        if mag > 0:
            return Vector2(self.x / mag, self.y / mag)
        return Vector2(0, 0)

    def distance_to(self, other: 'Vector2') -> float:
        return (self - other).magnitude()


@dataclass
class Rectangle:
    """2D Rectangle for collision detection"""
    x: float
    y: float
    width: float
    height: float

    def intersects(self, other: 'Rectangle') -> bool:
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

    def contains_point(self, point: Vector2) -> bool:
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)


class Component(ABC):
    """Base component class"""

    def __init__(self, owner: 'GameObject'):
        self.owner = owner
        self.enabled = True

    @abstractmethod
    def update(self, delta_time: float):
        pass


class Transform(Component):
    """Transform component for position, rotation, scale"""

    def __init__(self, owner: 'GameObject'):
        super().__init__(owner)
        self.position = Vector2()
        self.rotation = 0.0
        self.scale = Vector2(1.0, 1.0)

    def update(self, delta_time: float):
        pass


class Renderer(Component):
    """Renderer component"""

    def __init__(self, owner: 'GameObject'):
        super().__init__(owner)
        self.color = (255, 255, 255)
        self.visible = True

    def update(self, delta_time: float):
        pass

    def render(self, screen):
        # Simulated rendering
        if self.visible:
            transform = self.owner.get_component(Transform)
            if transform:
                print(f"Rendering {self.owner.name} at ({transform.position.x}, {transform.position.y})")


class Physics(Component):
    """Physics component"""

    def __init__(self, owner: 'GameObject'):
        super().__init__(owner)
        self.velocity = Vector2()
        self.acceleration = Vector2()
        self.mass = 1.0
        self.friction = 0.95

    def update(self, delta_time: float):
        transform = self.owner.get_component(Transform)
        if transform:
            # Apply physics
            self.velocity += self.acceleration * delta_time
            self.velocity *= self.friction
            transform.position += self.velocity * delta_time


class Collider(Component):
    """Collision detection component"""

    def __init__(self, owner: 'GameObject'):
        super().__init__(owner)
        self.bounds = Rectangle(0, 0, 50, 50)
        self.is_trigger = False

    def update(self, delta_time: float):
        transform = self.owner.get_component(Transform)
        if transform:
            self.bounds.x = transform.position.x
            self.bounds.y = transform.position.y

    def check_collision(self, other: 'Collider') -> bool:
        return self.bounds.intersects(other.bounds)


class GameObject:
    """Game object base class"""

    def __init__(self, name: str):
        self.name = name
        self.components: Dict[type, Component] = {}
        self.active = True
        self.tags = set()

    def add_component(self, component: Component):
        self.components[type(component)] = component

    def get_component(self, component_type: type) -> Optional[Component]:
        return self.components.get(component_type)

    def update(self, delta_time: float):
        if not self.active:
            return

        for component in self.components.values():
            if component.enabled:
                component.update(delta_time)

    def add_tag(self, tag: str):
        self.tags.add(tag)

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


class System(ABC):
    """Base system class"""

    def __init__(self, world: 'World'):
        self.world = world

    @abstractmethod
    def update(self, delta_time: float):
        pass


class PhysicsSystem(System):
    """Physics simulation system"""

    def update(self, delta_time: float):
        # Update physics for all objects with physics components
        for game_object in self.world.objects:
            if game_object.active:
                physics = game_object.get_component(Physics)
                if physics:
                    physics.update(delta_time)


class RenderSystem(System):
    """Rendering system"""

    def update(self, delta_time: float):
        # Render all objects with renderer components
        for game_object in self.world.objects:
            if game_object.active:
                renderer = game_object.get_component(Renderer)
                if renderer:
                    renderer.render(None)  # Would pass actual screen


class CollisionSystem(System):
    """Collision detection system"""

    def update(self, delta_time: float):
        objects_with_colliders = []
        for game_object in self.world.objects:
            if game_object.active and game_object.get_component(Collider):
                objects_with_colliders.append(game_object)

        # Check collisions
        for i, obj1 in enumerate(objects_with_colliders):
            for obj2 in objects_with_colliders[i+1:]:
                collider1 = obj1.get_component(Collider)
                collider2 = obj2.get_component(Collider)

                if collider1 and collider2:
                    if collider1.check_collision(collider2):
                        self.world.emit_event(Event(
                            EventType.COLLISION,
                            {"obj1": obj1, "obj2": obj2}
                        ))


class World:
    """Game world manager"""

    def __init__(self):
        self.objects: List[GameObject] = []
        self.systems: List[System] = []
        self.event_listeners: Dict[EventType, List[Callable]] = {}
        self.is_running = False

    def add_object(self, game_object: GameObject):
        self.objects.append(game_object)

    def remove_object(self, game_object: GameObject):
        if game_object in self.objects:
            self.objects.remove(game_object)

    def add_system(self, system: System):
        self.systems.append(system)

    def add_event_listener(self, event_type: EventType, listener: Callable):
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)

    def emit_event(self, event: Event):
        listeners = self.event_listeners.get(event.type, [])
        for listener in listeners:
            listener(event)

    def get_objects_by_tag(self, tag: str) -> List[GameObject]:
        return [obj for obj in self.objects if obj.has_tag(tag)]

    def update(self, delta_time: float):
        # Update all game objects
        for game_object in self.objects:
            game_object.update(delta_time)

        # Update all systems
        for system in self.systems:
            system.update(delta_time)

    def run(self):
        """Main game loop"""
        self.is_running = True
        last_time = time.time()

        while self.is_running:
            current_time = time.time()
            delta_time = current_time - last_time
            last_time = current_time

            # Update world
            self.update(delta_time)

            # Emit tick event
            self.emit_event(Event(EventType.TICK, {"delta_time": delta_time}))

            # Simple frame rate limiting
            time.sleep(0.016)  # ~60 FPS


class Game:
    """Main game class"""

    def __init__(self, title: str = "Game"):
        self.title = title
        self.world = World()
        self.setup_systems()
        self.setup_scene()

    def setup_systems(self):
        """Setup game systems"""
        self.world.add_system(PhysicsSystem(self.world))
        self.world.add_system(RenderSystem(self.world))
        self.world.add_system(CollisionSystem(self.world))

    def setup_scene(self):
        """Setup initial game scene"""
        # Create player
        player = GameObject("Player")
        player.add_component(Transform())
        player.add_component(Renderer(player))
        player.add_component(Physics(player))
        player.add_component(Collider(player))
        player.add_tag("player")
        self.world.add_object(player)

        # Create enemy
        enemy = GameObject("Enemy")
        transform = Transform()
        transform.position = Vector2(200, 100)
        enemy.add_component(transform)
        enemy.add_component(Renderer(enemy))
        enemy.add_component(Collider(enemy))
        enemy.add_tag("enemy")
        self.world.add_object(enemy)

        # Setup collision listener
        self.world.add_event_listener(
            EventType.COLLISION,
            lambda event: print(f"Collision: {event.data['obj1'].name} hit {event.data['obj2'].name}")
        )

    def run(self):
        """Start the game"""
        print(f"Starting {self.title}")
        self.world.run()


# Example usage
if __name__ == "__main__":
    game = Game("Simple Game")
    game.run()