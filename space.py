from abc import ABC, abstractmethod
from math import pi, sqrt, cos, atan, sin
from typing import Tuple, List

G = 9.80665


class Space:
    def __init__(self, size: Tuple[int, int]):
        self.width, self.height = size


class Angle:
    def __init__(self, value, to_deg: bool = False):
        self.__value = value if not to_deg else value * 180 / pi

    def __str__(self):
        return f"{self.degrees}°"

    @property
    def degrees(self):
        return self.__value

    @property
    def radians(self):
        return self.__value * pi / 180

    def __sub__(self, other: 'Angle'):
        return Angle(self.__value - other.__value)

    def __add__(self, other: 'Angle'):
        return Angle(self.__value + other.__value)


class VectorizeParameter:
    def __init__(self, value: float, angle: Angle, name: str = "val"):
        self.__value = value
        self.__angle = angle
        self.name = name

    @property
    def x_vector(self):
        return self.__value * cos(self.__angle.radians)

    @property
    def y_vector(self):
        return self.__value * sin(self.__angle.radians)

    def __add__(self, other: 'VectorizeParameter'):
        a, b, alpha, betta = self.__value, other.__value, self.__angle, other.__angle
        c = sqrt(a ** 2 + b ** 2 + 2 * a * b * cos((alpha - betta).radians))

        fx = a * cos(alpha.radians) + b * cos(betta.radians)
        fy = a * sin(alpha.radians) + b * sin(betta.radians)

        angle = Angle(atan(fy / fx), to_deg=True)
        v = VectorizeParameter(value=c, angle=angle)
        return v

    def __str__(self):
        return f"{self.__value}{self.name} {self.__angle}"

    def __eq__(self, other: 'VectorizeParameter'):
        return str(other) == str(self)

    def __mul__(self, other: int):
        return VectorizeParameter(self.__value * other, self.__angle)

    def __truediv__(self, other: int):
        return VectorizeParameter(self.__value / other, self.__angle)


class Speed:
    def __init__(self, linear: VectorizeParameter = None, rotational: VectorizeParameter = None):
        self.linear = linear if linear else VectorizeParameter(0, Angle(0))
        self.rotational = rotational if rotational else VectorizeParameter(0, Angle(0))


class CollisionShape(ABC):

    @abstractmethod
    def top_verticals(self, *args):
        ...

    @abstractmethod
    def bottom_verticals(self, *args):
        ...


class SquareShape(CollisionShape):

    def top_verticals(self, *args):
        (x, y), a, (w, h) = c1, _, _ = args
        x2, y2 = c2 = x + w * sin(a.radians), y - w * cos(a.radians)
        x3, y3 = c3 = x2 + h * cos(a.radians), y2 + h * sin(a.radians)
        x4, y4 = c4 = x3 - w * sin(a.radians), y + w * cos(a.radians)

        return (x, y), (x2, y2), (x3, y3), (x4, y4)


class SpaceData:
    def __init__(self, size: Tuple[int, int], coords: Tuple[int, int], angles: Angle):
        self.__width, self.__height = size
        self.__x, self.__y = coords
        self.__angle = angles
        self.__shape = CollisionShape()

    def update_coords(self, speed: VectorizeParameter, _time: float):
        self.__x += speed.x_vector * _time
        self.__y += speed.y_vector * _time
        return self.__x, self.__y


class ForceData:
    def __init__(self, mass: float, speed: Speed):
        self.mass = mass
        self.speed = speed

    def update_speed(self, forces: List[VectorizeParameter], _time: float):
        if forces:
            map((avg_force := forces[0]).__add__, forces[1:])
            self.speed.linear += avg_force * _time / self.mass
        return self.speed.linear


class CollideObject:

    MIN_LENGTH = 1

    def __init__(self, space_data: SpaceData):
        self._space_data = space_data

    def __contains__(self, item: 'CollideObject'):
        ...


class Object(CollideObject):

    def __init__(self, space_data: SpaceData, force_data: ForceData):
        super().__init__(space_data)
        self.__force_data = force_data

    @property
    def mass(self):
        return self.__force_data.mass

    def interact(self, *args, _time: float = 1):
        speed: VectorizeParameter = self.__force_data.update_speed(args, _time=_time)
        coords: Tuple = self._space_data.update_coords(speed, _time)
        return coords


if __name__ == "__main__":
    s, f = (
        SpaceData((50, 50), (0, 0), Angle(0)),
        ForceData(5, VectorizeParameter(15, Angle(90)))
    )
    obj = Object(s, f)
    y, counter = 0, 0
    gravity = VectorizeParameter(obj.mass * G, Angle(-90))
    while y >= 0:
        x, y = obj.interact(gravity, _time=0.016)
        print(f"X: {x:.2f}; Y: {y:.2f}")
        counter += 0.016
    print(f"Total time: {counter:.2f}")
