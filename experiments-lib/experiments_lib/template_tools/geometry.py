from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Generic
from typing import List
from typing import Tuple
from typing import TypeVar

from shapely.geometry import Polygon


NumericType = TypeVar("NumericType", int, float)


@dataclass
class Rectangle(Generic[NumericType]):
    x: NumericType
    y: NumericType
    width: NumericType
    height: NumericType

    @staticmethod
    def from_tuple(
        rect_tuple: Tuple[NumericType, NumericType, NumericType, NumericType]
    ) -> Rectangle[NumericType]:
        return Rectangle(*rect_tuple)

    @cached_property
    def top_left(self) -> Tuple[NumericType, NumericType]:
        return self.x, self.y

    @cached_property
    def top_right(self) -> Tuple[NumericType, NumericType]:
        return self.x + self.width, self.y

    @cached_property
    def bottom_right(self) -> Tuple[NumericType, NumericType]:
        return self.x + self.width, self.y + self.height

    @cached_property
    def bottom_left(self) -> Tuple[NumericType, NumericType]:
        return self.x, self.y + self.height

    @cached_property
    def minmax_tuple(self) -> Tuple[NumericType, NumericType, NumericType, NumericType]:
        return self.top_left + self.bottom_right

    @cached_property
    def polygon(self) -> Polygon:
        return Polygon(
            [self.top_left, self.top_right, self.bottom_right, self.bottom_left]
        )

    def expand_left(self, by: NumericType) -> Rectangle[NumericType]:
        return Rectangle(
            x=self.x - by, y=self.y, width=self.width + by, height=self.height
        )

    def expand_right(self, by: NumericType) -> Rectangle[NumericType]:
        return Rectangle(x=self.x, y=self.y, width=self.width + by, height=self.height)

    def expand_bottom(self, by: NumericType) -> Rectangle[NumericType]:
        return Rectangle(x=self.x, y=self.y, width=self.width, height=self.height + by)

    def expand_top(self, by: NumericType) -> Rectangle[NumericType]:
        return Rectangle(
            x=self.x, y=self.y - by, width=self.width, height=self.height + by
        )

    def expand(self, by: NumericType) -> Rectangle[NumericType]:
        return self.expand_left(by).expand_right(by).expand_top(by).expand_bottom(by)


def merge_rectangles(
    rectangles: List[Rectangle[NumericType]],
) -> Rectangle[NumericType]:
    min_x = min(map(lambda rect: rect.x, rectangles))
    min_y = min(map(lambda rect: rect.y, rectangles))

    max_x = max(map(lambda rect: rect.top_right[0], rectangles))
    max_y = max(map(lambda rect: rect.bottom_right[1], rectangles))

    return Rectangle(x=min_x, y=min_y, width=max_x - min_x, height=max_y - min_y)