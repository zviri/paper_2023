from __future__ import annotations

from itertools import chain
from typing import Callable
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import Levenshtein
import regex
from toolz import first
from attr import attrib
from attr import attrs
from experiments_lib.models.pb.ocr_pb2 import OCRResponse
from experiments_lib.util.strings import string_id
from shapely.geometry import Polygon


@attrs
class TemplateMatcherFactory:
    def create(self, blocks: List[OCRResponse.TextBlock]):
        return TemplateMatcher(blocks)

    def create_empty(self):
        return self.create([])


@attrs
class RelativeCoordinates:
    width: float = attrib()
    height: float = attrib()
    x_translate: float = attrib()
    y_translate: float = attrib()


@attrs
class TemplateMatcher:
    blocks: List[OCRResponse.TextBlock] = attrib()

    def explode(self) -> TemplateMatcher:
        new_blocks = self._flatten_block_children(self.blocks)
        return TemplateMatcher(list(new_blocks))

    def append(
        self, blocks: List[OCRResponse.TextBlock], sort: bool = False
    ) -> TemplateMatcher:
        new_blocks = self.blocks + blocks
        if sort:
            new_blocks = sorted(
                new_blocks, key=lambda block: (block.bbox.y, block.bbox.x)
            )
        return TemplateMatcher(new_blocks)

    def merge(self, matcher: TemplateMatcher) -> TemplateMatcher:
        return self.merge_all([matcher])

    def merge_all(self, matchers: Iterable[TemplateMatcher]) -> TemplateMatcher:
        new_blocks = self._merge_text_blocks(chain([self], matchers))
        return TemplateMatcher(list(new_blocks))

    def submatcher(
        self, select_func: Callable[[OCRResponse.TextBlock], bool]
    ) -> TemplateMatcher:
        blocks = list(self.get_blocks(select_func))
        return TemplateMatcher(blocks)

    def submatcher_between(
        self, top: float, bottom: Optional[float] = None, inclusive=False
    ) -> TemplateMatcher:
        if not self.blocks:
            return TemplateMatcher([])
        if bottom is None:
            bottom = max(self.blocks, key=lambda block: block.bbox.y).bbox.y + 0.01
        if top > bottom:
            raise ValueError("Top block must be above the bottom block")

        def _select(block):
            block_y = block.bbox.y
            return bottom >= block_y >= top if inclusive else bottom > block_y > top

        return self.submatcher(_select)

    def get_blocks(
        self, match_func: Callable[[OCRResponse.TextBlock], bool]
    ) -> Iterable[OCRResponse.TextBlock]:
        return filter(match_func, self.blocks)

    def get_all_blocks(self) -> Iterable[OCRResponse.TextBlock]:
        return self.get_blocks(lambda _: True)

    def get_blocks_by_text(
        self, text: str, normalize: bool = False, max_edit_distance: int = 0
    ) -> Iterable[OCRResponse.TextBlock]:
        return self.get_blocks(
            self._create_string_match_func(text, normalize, max_edit_distance)
        )

    def get_blocks_by_regex(
        self,
        regex_: Union[str, regex.Regex],
        normalize: bool = False,
    ) -> Iterable[OCRResponse.TextBlock]:
        return self.get_blocks(self._create_regex_matc_func(regex_, normalize))

    def get_relative_blocks(
        self,
        reference: OCRResponse.TextBlock,
        coordinates: RelativeCoordinates,
    ) -> Iterable[OCRResponse.TextBlock]:
        relative_box = self._create_relative_box(reference, coordinates)
        relative_box_polygon = self._to_shapely(relative_box)

        for block in self.blocks:
            block_polygon = self._to_shapely(block.bbox)
            if relative_box_polygon.intersects(block_polygon):
                yield block

    def get_key_values(
        self,
        key_match_func: Callable[[OCRResponse.TextBlock], bool],
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        coordinates: RelativeCoordinates,
    ) -> Iterable[OCRResponse.TextBlock]:
        for key_block in filter(key_match_func, self.blocks):
            for value_block in self.get_relative_blocks(
                reference=key_block, coordinates=coordinates
            ):
                if value_match_func(value_block):
                    yield value_block

    def get_key_value(
        self,
        key_match_func: Callable[[OCRResponse.TextBlock], bool],
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        coordinates: RelativeCoordinates,
    ) -> Optional[OCRResponse.TextBlock]:
        return first(self.get_key_values(key_match_func, value_match_func, coordinates))

    def get_key_values_by_text(
        self,
        text: str,
        coordinates: RelativeCoordinates,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        normalize: bool = False,
        max_edit_distance: int = 0,
    ) -> Iterable[OCRResponse.TextBlock]:
        return self.get_key_values(
            key_match_func=self._create_string_match_func(
                text, normalize, max_edit_distance
            ),
            value_match_func=value_match_func,
            coordinates=coordinates,
        )

    def get_key_value_by_text(
        self,
        text: str,
        coordinates: RelativeCoordinates,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        normalize: bool = False,
        max_edit_distance: int = 0,
    ) -> Optional[OCRResponse.TextBlock]:
        return first(
            self.get_key_values_by_text(
                text, coordinates, value_match_func, normalize, max_edit_distance
            )
        )

    def get_key_values_by_regex(
        self,
        regex_: Union[str, regex.Regex],
        coordinates: RelativeCoordinates,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        normalize: bool = False,
    ) -> Iterable[OCRResponse.TextBlock]:
        return self.get_key_values(
            key_match_func=self._create_regex_matc_func(regex_, normalize),
            value_match_func=value_match_func,
            coordinates=coordinates,
        )

    def get_key_value_by_regex(
        self,
        regex_: Union[str, regex.Regex],
        coordinates: RelativeCoordinates,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        normalize: bool = False,
    ) -> Optional[OCRResponse.TextBlock]:
        return first(
            self.get_key_values_by_regex(
                regex_, coordinates, value_match_func, normalize
            )
        )

    def get_table_cell(
        self,
        row_label: OCRResponse.TextBlock,
        column_label: OCRResponse.TextBlock,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        row_margin: Tuple[float, float] = (0, 0),
        column_margin: Tuple[float, float] = (0, 0),
    ) -> Optional[OCRResponse.TextBlock]:
        cell_bbox = self._create_cell_bbox(
            row_label, column_label, column_margin, row_margin
        )

        cell_polygon = self._to_shapely(cell_bbox)
        for block in self.blocks:
            if cell_polygon.intersects(
                self._to_shapely(block.bbox)
            ) and value_match_func(block):
                return block
        else:
            return None

    def get_table_cell_by_text(
        self,
        row_key: str,
        column_key: str,
        value_match_func: Callable[[OCRResponse.TextBlock], bool],
        normalize: bool = False,
        max_edit_distance: int = 0,
        row_margin: Tuple[float, float] = (0, 0),
        column_margin: Tuple[float, float] = (0, 0),
    ) -> Optional[OCRResponse.TextBlock]:
        row_key_blocks = list(
            self.get_blocks_by_text(row_key, normalize, max_edit_distance)
        )
        column_key_blocks = list(
            self.get_blocks_by_text(column_key, normalize, max_edit_distance)
        )

        if row_key_blocks and column_key_blocks:
            return self.get_table_cell(
                row_label=row_key_blocks[0],
                column_label=column_key_blocks[0],
                value_match_func=value_match_func,
                row_margin=row_margin,
                column_margin=column_margin,
            )
        return None

    @staticmethod
    def _flatten_block_children(
        blocks: Iterable[OCRResponse.TextBlock],
    ) -> Iterable[OCRResponse.TextBlock]:
        for block in blocks:
            yield from block.children

    @classmethod
    def _merge_text_blocks(
        cls, matchers: Iterable[TemplateMatcher]
    ) -> Iterable[OCRResponse.TextBlock]:
        for idx, matcher in enumerate(matchers):
            for block in matcher.get_all_blocks():
                if block.bbox.y > 1.0:
                    raise NotImplementedError(
                        "Merging of complex matchers is not supported"
                    )
                new_block = OCRResponse.TextBlock()
                new_block.CopyFrom(block)
                cls._update_y_coordinate_recursively(new_block, idx)
                yield new_block

    @classmethod
    def _update_y_coordinate_recursively(cls, block: OCRResponse.TextBlock, idx: int):
        block.bbox.y += idx
        for child in block.children:
            cls._update_y_coordinate_recursively(child, idx)

    @staticmethod
    def _create_string_match_func(
        search_text: str, normalize: bool, max_edit_distance: int
    ) -> Callable[[OCRResponse.TextBlock], bool]:
        search_text = TemplateMatcher._preprocess_text(search_text, normalize)

        def _string_match(block):
            block_text = TemplateMatcher._preprocess_text(block.text, normalize)
            return TemplateMatcher._compare_texts(
                search_text, block_text, max_edit_distance
            )

        return _string_match

    @staticmethod
    def _create_regex_matc_func(
        regex_: Union[str, regex.Regex], normalize: bool
    ) -> Callable[[OCRResponse.TextBlock], bool]:
        matcher = regex.compile(regex_) if type(regex_) == str else regex_

        def _regex_match(block):
            block_text = TemplateMatcher._preprocess_text(block.text, normalize)
            return matcher.match(block_text)

        return _regex_match

    @staticmethod
    def _create_cell_bbox(
        row_key: OCRResponse.TextBlock,
        column_key: OCRResponse.TextBlock,
        column_margin: Tuple[float, float],
        row_margin: Tuple[float, float],
    ) -> OCRResponse.BoundingBox:
        row_bbox = row_key.bbox
        col_bbox = column_key.bbox
        cell_bbox = OCRResponse.BoundingBox(
            x=col_bbox.x - column_margin[0],
            y=row_bbox.y - row_margin[0],
            width=col_bbox.width + column_margin[0] + column_margin[1],
            height=row_bbox.height + row_margin[0] + row_margin[1],
        )
        return cell_bbox

    @staticmethod
    def _preprocess_text(text: str, normalize: bool) -> str:
        if normalize:
            return string_id(text)
        else:
            return text

    @staticmethod
    def _compare_texts(text1: str, text2: str, max_edit_distance: int) -> bool:
        if max_edit_distance:
            return Levenshtein.distance(text1, text2) <= max_edit_distance
        else:
            return text1 == text2

    @staticmethod
    def _create_relative_box(
        label_block: OCRResponse.TextBlock,
        coordinates: RelativeCoordinates,
    ) -> OCRResponse.BoundingBox:
        label_bbox = label_block.bbox
        return OCRResponse.BoundingBox(
            x=label_bbox.x + coordinates.x_translate,
            y=label_bbox.y + coordinates.y_translate,
            width=coordinates.width,
            height=coordinates.height,
        )

    @staticmethod
    def _to_shapely(bbox: OCRResponse.BoundingBox) -> Polygon:
        return Polygon(
            [
                (bbox.x, bbox.y),
                (bbox.x + bbox.width, bbox.y),
                (bbox.x + bbox.width, bbox.y + bbox.height),
                (bbox.x, bbox.y + bbox.height),
            ]
        )