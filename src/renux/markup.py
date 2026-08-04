"""Registry for renux's markup syntax: `{value}` and `{value|filter}`.

Every placeholder (`{counter}`, `{now(%Y)}`, ...) and every filter
(`{name|slugify}`, `{name|upper}`, ...) is registered here, once, with the
metadata needed both to resolve it and to document it. Adding or changing a
placeholder or filter here is the *only* change needed — the CLI `--help`
text, the TUI help screen, the syntax highlighter, and autocomplete
suggestions are all generated from this registry, not maintained separately.

To add a new filter, call `register_filter`. To add a new placeholder
(a `{name}` or `{name(args)}` value provider), call `register_placeholder`.
"""

from __future__ import annotations

import datetime
import os
import re
from dataclasses import dataclass, field
from typing import Callable

from slugify import slugify

from renux.helpers.casing import (
    to_camel_case,
    to_kebab_case,
    to_pascal_case,
    to_snake_case,
)


@dataclass(frozen=True)
class Filter:
    """A `{value|name}` text transformation."""

    name: str
    func: Callable[[str], str]
    description: str


@dataclass(frozen=True)
class PlaceholderContext:
    """Input available to a placeholder's `resolve` function."""

    args: str
    counter: int | None
    file_name: str
    directory: str


@dataclass(frozen=True)
class Placeholder:
    """A `{name}` or `{name(args)}` value provider."""

    name: str
    description: str
    syntax: str
    resolve: Callable[[PlaceholderContext], str]
    example: str | None = None
    # Suggested `(args)` strings for autocomplete, e.g. "(1,1,0)" or "(%Y)".
    arg_suggestions: list[str] = field(default_factory=list)
    # Stateful placeholders (e.g. counter) track a value that advances once
    # per occurrence, per file. `initial` parses the starting value out of
    # `args`; `advance` computes the next value from the current one.
    stateful: bool = False
    initial: Callable[[str], int] | None = None
    advance: Callable[[str, int], int] | None = None


FILTERS: dict[str, Filter] = {}
PLACEHOLDERS: dict[str, Placeholder] = {}


def register_filter(name: str, func: Callable[[str], str], description: str) -> None:
    """Register a `{value|name}` text transformation."""
    FILTERS[name] = Filter(name, func, description)


def register_placeholder(
    name: str,
    resolve: Callable[[PlaceholderContext], str],
    description: str,
    syntax: str,
    example: str | None = None,
    arg_suggestions: list[str] | None = None,
    stateful: bool = False,
    initial: Callable[[str], int] | None = None,
    advance: Callable[[str, int], int] | None = None,
) -> None:
    """Register a `{name}` / `{name(args)}` value provider."""
    PLACEHOLDERS[name] = Placeholder(
        name=name,
        description=description,
        syntax=syntax,
        resolve=resolve,
        example=example,
        arg_suggestions=arg_suggestions or [],
        stateful=stateful,
        initial=initial,
        advance=advance,
    )


# --- Filters -----------------------------------------------------------------

register_filter(
    "slugify",
    slugify,
    'Convert into a URL/filename-friendly format (e.g. "hello world" → "hello-world")',
)
register_filter("lower", str.lower, "Convert to lowercase")
register_filter("upper", str.upper, "Convert to uppercase")
register_filter("caps", str.capitalize, "Capitalize the first letter")
register_filter("title", str.title, "Capitalize each word")
register_filter(
    "camel",
    to_camel_case,
    'Convert to camel case (e.g. "hello world" → "helloWorld")',
)
register_filter(
    "pascal",
    to_pascal_case,
    'Convert to pascal case (e.g. "hello world" → "HelloWorld")',
)
register_filter(
    "snake",
    to_snake_case,
    'Convert to snake case (e.g. "hello world" → "hello_world")',
)
register_filter(
    "kebab",
    to_kebab_case,
    'Convert to kebab case (e.g. "hello world" → "hello-world")',
)
register_filter(
    "swapcase",
    str.swapcase,
    'Swap the case (e.g. "Hello World" → "hELLO wORLD")',
)
register_filter(
    "reverse",
    lambda s: s[::-1],
    'Reverse the string (e.g. "Hello World" → "dlroW olleH")',
)
register_filter("strip", str.strip, "Remove leading and trailing whitespace")
register_filter("len", lambda s: str(len(s)), "Get the length of the string")


# --- Placeholders --------------------------------------------------------------


def _parse_counter_args(args: str) -> tuple[int, int, int]:
    match = re.match(r"\s*(\d+)?\s*,?\s*(\d+)?\s*,?\s*(\d+)?\s*", args)
    start = int(match.group(1)) if match and match.group(1) else 1
    step = int(match.group(2)) if match and match.group(2) else 1
    padding = int(match.group(3)) if match and match.group(3) else 1
    return start, step, padding


def _resolve_counter(ctx: PlaceholderContext) -> str:
    assert ctx.counter is not None
    _, _, padding = _parse_counter_args(ctx.args)
    return str(ctx.counter).zfill(padding)


def _counter_initial(args: str) -> int:
    start, _, _ = _parse_counter_args(args)
    return start


def _counter_advance(args: str, current: int) -> int:
    _, step, _ = _parse_counter_args(args)
    return current + step


register_placeholder(
    "counter",
    _resolve_counter,
    "Insert an incrementing counter. Each placeholder occurrence tracks its "
    "own sequence, advancing by `step` after every file.",
    syntax="{counter(start=1,step=1,padding=1)}",
    example="{counter(1,2,3)}",
    arg_suggestions=["", "(1,1,0)", "(0,1,0)"],
    stateful=True,
    initial=_counter_initial,
    advance=_counter_advance,
)


DATE_FORMAT_SUGGESTIONS = [
    "",
    "(%Y)",
    "(%Y-%m-%d)",
    "(%d-%m-%Y)",
    "(%m-%d-%Y)",
    "(%H:%M:%S)",
    "(%Y-%m-%d %H:%M:%S)",
    "(%d-%m-%Y %H:%M:%S)",
    "(%m-%d-%Y %H:%M:%S)",
]


def _resolve_now(ctx: PlaceholderContext) -> str:
    return datetime.datetime.now().strftime(ctx.args or "%Y-%m-%d")


def _resolve_created_at(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    timestamp = os.path.getctime(path)
    return datetime.datetime.fromtimestamp(timestamp).strftime(ctx.args or "%Y-%m-%d")


def _resolve_modified_at(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    timestamp = os.path.getmtime(path)
    return datetime.datetime.fromtimestamp(timestamp).strftime(ctx.args or "%Y-%m-%d")


register_placeholder(
    "now",
    _resolve_now,
    "The current date/time.",
    syntax="{now(<format>)}",
    example="{now(%Y)}",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
register_placeholder(
    "created_at",
    _resolve_created_at,
    "The file's creation date/time.",
    syntax="{created_at(<format>)}",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
register_placeholder(
    "modified_at",
    _resolve_modified_at,
    "The file's last-modified date/time.",
    syntax="{modified_at(<format>)}",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
