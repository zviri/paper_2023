from datetime import date
from itertools import chain
from typing import Iterable, List, Optional

from experiments_lib.util.lists import first
from experiments_lib.models.pb.ocr_pb2 import OCRResponse
from experiments_lib.expressions.due_date_expr import due_date as due_date_expr
from experiments_lib.expressions.date_expr import date_ as date_expr
from experiments_lib.template_tools.template_matcher import TemplateMatcher
from experiments_lib.template_tools.template_matcher import TemplateMatcherFactory
from experiments_lib.template_tools.template_matcher import RelativeCoordinates
from attr import attrib, attrs


@attrs
class DueDateExtractor:
    template_matcher_factory: TemplateMatcherFactory = attrib()

    def extract(self, document: List[OCRResponse.Page]) -> Optional[date]:
        pages_matchers = self._build_matchers_for_pages(document)
        matcher = self._merge_matchers(pages_matchers)

        first_due_date = min(
            chain(
                self._find_all_due_dates_in_text(matcher),
                self._find_all_due_dates_in_old_receivables(matcher),
                self._find_all_due_dates_in_new_receivables_v1(matcher),
            ),
            default=None,
        )
        return first_due_date

    def _find_all_due_dates_in_text(self, matcher: TemplateMatcher) -> Iterable[date]:
        all_text = "\n".join(map(lambda b: b.text, matcher.get_all_blocks()))
        for match in due_date_expr.search_string(all_text):
            if (first_due_date := match.date) and isinstance(first_due_date, date):
                yield first_due_date

    def _find_all_due_dates_in_old_receivables(
        self, matcher: TemplateMatcher
    ) -> Iterable[date]:
        line_matcher = matcher.explode()
        if label := first(line_matcher.get_blocks_by_text("Splatná od:", True, 1)):
            if date_block := first(
                filter(
                    lambda block: block.id != label.id,
                    line_matcher.get_relative_blocks(
                        label,
                        RelativeCoordinates(
                            width=label.bbox.width,
                            height=label.bbox.height,
                            x_translate=0,
                            y_translate=label.bbox.height,
                        ),
                    ),
                )
            ):
                if date_match := first(date_expr.searchString(date_block.text)):
                    if (first_due_date := date_match.date) and isinstance(
                        first_due_date, date
                    ):
                        yield first_due_date

    def _find_all_due_dates_in_new_receivables_v1(
        self, matcher: TemplateMatcher
    ) -> Iterable[date]:
        if label := first(
            chain(
                matcher.get_blocks_by_text(
                    "Splatnost nejstarší časti závazku", True, 2
                ),
                matcher.get_blocks_by_text("Splatnost nejst. c. zavazku od:", True, 2),
            )
        ):
            if date_block := first(
                matcher.get_relative_blocks(
                    label,
                    RelativeCoordinates(
                        width=label.bbox.width * 0.6,
                        height=label.bbox.height,
                        x_translate=label.bbox.width * 1.3,
                        y_translate=0,
                    ),
                )
            ):
                if date_match := first(date_expr.searchString(date_block.text)):
                    if (first_due_date := date_match.date) and isinstance(
                        first_due_date, date
                    ):
                        yield first_due_date

    def _build_matchers_for_pages(
        self, pages: Iterable[OCRResponse.Page]
    ) -> List[TemplateMatcher]:
        page_matchers = [
            self.template_matcher_factory.create(list(page.blocks)) for page in pages
        ]
        return page_matchers

    def _merge_matchers(self, matchers: List[TemplateMatcher]) -> TemplateMatcher:
        if matchers:
            return matchers[0].merge_all(matchers[1:])
        else:
            return self.template_matcher_factory.create_empty()
