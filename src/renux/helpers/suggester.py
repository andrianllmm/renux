from textual.suggester import Suggester, SuggestFromList

from renux.tags import FILTERS, PLACEHOLDERS


class TagSuggester(Suggester):
    """Suggests filenames, or, while inside an unclosed `{...}`, matching
    placeholder/filter names from the tags registry.

    Always requests the raw (non-casefolded) value from the base `Suggester`
    so that already-typed text (e.g. a `{now(%Y)` argument) is never
    mangled when reconstructing a suggestion; case-insensitivity is applied
    only to the comparison, not the returned string.
    """

    def __init__(self, filenames: list[str], *, case_sensitive: bool = False) -> None:
        super().__init__(case_sensitive=True)
        self._match_case_sensitive = case_sensitive
        self._filename_suggester = SuggestFromList(
            filenames, case_sensitive=case_sensitive
        )
        self._placeholder_names = sorted(PLACEHOLDERS)
        self._filter_names = sorted(FILTERS)

    async def get_suggestion(self, value: str) -> str | None:
        brace_index = value.rfind("{")
        close_index = value.rfind("}")
        if brace_index == -1 or brace_index < close_index:
            lookup_value = value if self._match_case_sensitive else value.casefold()
            return await self._filename_suggester.get_suggestion(lookup_value)

        inside = value[brace_index + 1 :]
        pipe_index = inside.rfind("|")
        partial = inside[pipe_index + 1 :] if pipe_index != -1 else inside
        candidates = self._filter_names if pipe_index != -1 else self._placeholder_names

        # Mid-args (e.g. "counter(1,") isn't a name to complete against.
        if "(" in partial:
            return None

        partial_for_match = (
            partial if self._match_case_sensitive else partial.casefold()
        )
        for name in candidates:
            comparison = name if self._match_case_sensitive else name.casefold()
            if comparison.startswith(partial_for_match):
                token_start = (
                    brace_index + 1 + (pipe_index + 1 if pipe_index != -1 else 0)
                )
                return value[:token_start] + name

        return None
