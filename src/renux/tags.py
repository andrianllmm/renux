"""Registry for renux's tag syntax: `{value}` and `{value|filter}`.

Every placeholder (`{counter}`, `{now(%Y)}`, ...) and every filter
(`{name|slugify}`, `{name|upper}`, ...) is registered here, once, with the
metadata needed both to resolve it and to document it.

To add a new filter, call `register_filter`. To add a new placeholder, call `register_placeholder`.
"""

from __future__ import annotations

import datetime
import os
import re
from dataclasses import dataclass, field
from typing import Callable

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
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
    category: str
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

# Display order for placeholder categories in generated docs. A category not
# listed here is appended after these, in first-registered order.
CATEGORY_ORDER = ["General", "Date", "File", "Image", "Location", "Video"]


def register_filter(name: str, func: Callable[[str], str], description: str) -> None:
    """Register a `{value|name}` text transformation."""
    FILTERS[name] = Filter(name, func, description)


def grouped_placeholders() -> dict[str, list[Placeholder]]:
    """Group placeholders by category, ordered per `CATEGORY_ORDER` then by
    first-registration order for any category not listed there."""
    groups: dict[str, list[Placeholder]] = {}
    for placeholder in PLACEHOLDERS.values():
        groups.setdefault(placeholder.category, []).append(placeholder)

    ordered = {c: groups[c] for c in CATEGORY_ORDER if c in groups}
    ordered.update({c: g for c, g in groups.items() if c not in ordered})
    return ordered


def register_placeholder(
    name: str,
    resolve: Callable[[PlaceholderContext], str],
    description: str,
    syntax: str,
    category: str,
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
        category=category,
        example=example,
        arg_suggestions=arg_suggestions or [],
        stateful=stateful,
        initial=initial,
        advance=advance,
    )


# Filters

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


# Placeholders


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
    category="General",
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
    category="Date",
    example="{now(%Y)}",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
register_placeholder(
    "created_at",
    _resolve_created_at,
    "The file's creation date/time.",
    syntax="{created_at(<format>)}",
    category="Date",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
register_placeholder(
    "modified_at",
    _resolve_modified_at,
    "The file's last-modified date/time.",
    syntax="{modified_at(<format>)}",
    category="Date",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)


_SIZE_UNITS = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3}

SIZE_UNIT_SUGGESTIONS = ["", "(b)", "(kb)", "(mb)", "(gb)"]


def _resolve_size(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    size_bytes = os.path.getsize(path)

    unit = ctx.args.strip().lower()
    if unit not in _SIZE_UNITS:
        # Auto-pick the largest unit that keeps the value at least 1.
        unit = "b"
        for candidate in ("kb", "mb", "gb"):
            if size_bytes < _SIZE_UNITS[candidate]:
                break
            unit = candidate

    value = size_bytes / _SIZE_UNITS[unit]
    if unit == "b":
        return f"{int(value)}{unit}"
    return f"{value:.2f}".rstrip("0").rstrip(".") + unit


register_placeholder(
    "size",
    _resolve_size,
    "The file's size. Auto-scaled to the largest sensible unit unless a "
    "unit (b, kb, mb, gb) is given.",
    syntax="{size(<unit>)}",
    category="File",
    example="{size(mb)}",
    arg_suggestions=SIZE_UNIT_SUGGESTIONS,
)


def _resolve_width(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    with Image.open(path) as img:
        return str(img.width)


def _resolve_height(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    with Image.open(path) as img:
        return str(img.height)


register_placeholder(
    "width",
    _resolve_width,
    "The image's width in pixels.",
    syntax="{width}",
    category="Image",
)
register_placeholder(
    "height",
    _resolve_height,
    "The image's height in pixels.",
    syntax="{height}",
    category="Image",
)


_EXIF_MAKE = 271
_EXIF_MODEL = 272
_EXIF_SUB_IFD = 0x8769
_EXIF_DATETIME_ORIGINAL = 36867


def _resolve_taken_at(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    with Image.open(path) as img:
        raw = img.getexif().get_ifd(_EXIF_SUB_IFD).get(_EXIF_DATETIME_ORIGINAL)
    if not raw:
        raise ValueError(f"No EXIF capture date found: {path}")
    taken_at = datetime.datetime.strptime(raw, "%Y:%m:%d %H:%M:%S")
    return taken_at.strftime(ctx.args or "%Y-%m-%d")


def _resolve_camera_make(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    with Image.open(path) as img:
        make = img.getexif().get(_EXIF_MAKE)
    if not make:
        raise ValueError(f"No EXIF camera make found: {path}")
    return str(make).strip()


def _resolve_camera_model(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    with Image.open(path) as img:
        model = img.getexif().get(_EXIF_MODEL)
    if not model:
        raise ValueError(f"No EXIF camera model found: {path}")
    return str(model).strip()


register_placeholder(
    "taken_at",
    _resolve_taken_at,
    "The photo's capture date/time from EXIF metadata. Not available for "
    "images without EXIF data (e.g. screenshots, re-exported/edited images).",
    syntax="{taken_at(<format>)}",
    category="Image",
    example="{taken_at(%Y)}",
    arg_suggestions=DATE_FORMAT_SUGGESTIONS,
)
register_placeholder(
    "camera_make",
    _resolve_camera_make,
    "The camera manufacturer from EXIF metadata. Not available for images "
    "without EXIF data.",
    syntax="{camera_make}",
    category="Image",
)
register_placeholder(
    "camera_model",
    _resolve_camera_model,
    "The camera model from EXIF metadata. Not available for images "
    "without EXIF data.",
    syntax="{camera_model}",
    category="Image",
)


_EXIF_GPS_IFD = 0x8825
_GPS_LAT_REF = 1
_GPS_LAT = 2
_GPS_LON_REF = 3
_GPS_LON = 4
_GPS_ALT_REF = 5
_GPS_ALT = 6


def _gps_ifd(path: str):
    with Image.open(path) as img:
        return img.getexif().get_ifd(_EXIF_GPS_IFD)


def _dms_to_decimal(dms: tuple[float, float, float], ref: str) -> float:
    degrees, minutes, seconds = dms
    decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    return -decimal if ref in ("S", "W") else decimal


def _resolve_latitude(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    gps = _gps_ifd(path)
    lat, lat_ref = gps.get(_GPS_LAT), gps.get(_GPS_LAT_REF)
    if not lat or not lat_ref:
        raise ValueError(f"No EXIF GPS latitude found: {path}")
    return f"{_dms_to_decimal(lat, lat_ref):.6f}"


def _resolve_longitude(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    gps = _gps_ifd(path)
    lon, lon_ref = gps.get(_GPS_LON), gps.get(_GPS_LON_REF)
    if not lon or not lon_ref:
        raise ValueError(f"No EXIF GPS longitude found: {path}")
    return f"{_dms_to_decimal(lon, lon_ref):.6f}"


def _resolve_altitude(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    gps = _gps_ifd(path)
    alt = gps.get(_GPS_ALT)
    if alt is None:
        raise ValueError(f"No EXIF GPS altitude found: {path}")
    alt_ref = gps.get(_GPS_ALT_REF, 0)
    below_sea_level = alt_ref == 1 or alt_ref == b"\x01"
    value = -float(alt) if below_sea_level else float(alt)
    return f"{value:.1f}m"


register_placeholder(
    "latitude",
    _resolve_latitude,
    "The photo's GPS latitude in decimal degrees. Not available for images "
    "without GPS EXIF data.",
    syntax="{latitude}",
    category="Location",
)
register_placeholder(
    "longitude",
    _resolve_longitude,
    "The photo's GPS longitude in decimal degrees. Not available for images "
    "without GPS EXIF data.",
    syntax="{longitude}",
    category="Location",
)
register_placeholder(
    "altitude",
    _resolve_altitude,
    "The photo's GPS altitude in meters. Not available for images without "
    "GPS EXIF data.",
    syntax="{altitude}",
    category="Location",
)


def _video_metadata(path: str):
    parser = createParser(path)
    if not parser:
        raise ValueError(f"Unable to parse video file: {path}")
    with parser:
        metadata = extractMetadata(parser)
    if not metadata:
        raise ValueError(f"No metadata found for video file: {path}")
    return metadata


def _resolve_video_width(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    metadata = _video_metadata(path)
    return str(metadata.get("width"))


def _resolve_video_height(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    metadata = _video_metadata(path)
    return str(metadata.get("height"))


def _resolve_frame_rate(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    metadata = _video_metadata(path)
    fps = metadata.get("frame_rate")
    if fps is None:
        raise ValueError(f"No frame rate found for video file: {path}")
    return f"{fps:.2f}".rstrip("0").rstrip(".") + "fps"


def _resolve_duration(ctx: PlaceholderContext) -> str:
    path = os.path.join(ctx.directory, ctx.file_name)
    metadata = _video_metadata(path)
    duration = metadata.get("duration")
    if duration is None:
        raise ValueError(f"No duration found for video file: {path}")
    return f"{int(duration.total_seconds())}s"


register_placeholder(
    "video_width",
    _resolve_video_width,
    "The video's width in pixels.",
    syntax="{video_width}",
    category="Video",
)
register_placeholder(
    "video_height",
    _resolve_video_height,
    "The video's height in pixels.",
    syntax="{video_height}",
    category="Video",
)
register_placeholder(
    "frame_rate",
    _resolve_frame_rate,
    "The video's frame rate. Not available for all containers (e.g. MP4).",
    syntax="{frame_rate}",
    category="Video",
)
register_placeholder(
    "duration",
    _resolve_duration,
    "The video's duration, in seconds.",
    syntax="{duration}",
    category="Video",
)
