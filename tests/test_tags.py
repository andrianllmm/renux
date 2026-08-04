from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from renux.tags import (
    FILTERS,
    PLACEHOLDERS,
    PlaceholderContext,
    _dms_to_decimal,
    _resolve_altitude,
    _resolve_camera_make,
    _resolve_camera_model,
    _resolve_duration,
    _resolve_frame_rate,
    _resolve_height,
    _resolve_latitude,
    _resolve_longitude,
    _resolve_size,
    _resolve_taken_at,
    _resolve_video_height,
    _resolve_video_width,
    _resolve_width,
    grouped_placeholders,
)


def ctx(
    args: str = "", directory: str = ".", file_name: str = ""
) -> PlaceholderContext:
    return PlaceholderContext(
        args=args, counter=None, file_name=file_name, directory=directory
    )


# Registry


def test_grouped_placeholders_uses_category_order():
    groups = grouped_placeholders()
    categories = list(groups.keys())
    # Every category present must appear in the declared order.
    ordered_known = [
        c
        for c in categories
        if c in ["General", "Date", "File", "Image", "Location", "Video"]
    ]
    assert ordered_known == ["General", "Date", "File", "Image", "Location", "Video"]


def test_all_placeholders_and_filters_registered():
    assert "counter" in PLACEHOLDERS
    assert "size" in PLACEHOLDERS
    assert "width" in PLACEHOLDERS and "height" in PLACEHOLDERS
    assert "taken_at" in PLACEHOLDERS
    assert "latitude" in PLACEHOLDERS
    assert "video_width" in PLACEHOLDERS and "frame_rate" in PLACEHOLDERS
    assert "upper" in FILTERS and "slugify" in FILTERS


# size


def test_resolve_size_auto_scale(tmp_path):
    file = tmp_path / "f.bin"
    file.write_bytes(b"0" * 500)
    assert _resolve_size(ctx(directory=str(tmp_path), file_name="f.bin")) == "500b"

    file.write_bytes(b"0" * 2048)
    assert _resolve_size(ctx(directory=str(tmp_path), file_name="f.bin")) == "2kb"

    file.write_bytes(b"0" * (1024 * 1024 * 3))
    assert _resolve_size(ctx(directory=str(tmp_path), file_name="f.bin")) == "3mb"


def test_resolve_size_explicit_unit(tmp_path):
    file = tmp_path / "f.bin"
    file.write_bytes(b"0" * 2048)
    assert (
        _resolve_size(ctx(args="kb", directory=str(tmp_path), file_name="f.bin"))
        == "2kb"
    )
    assert (
        _resolve_size(ctx(args="b", directory=str(tmp_path), file_name="f.bin"))
        == "2048b"
    )


def test_resolve_size_zero_byte_file(tmp_path):
    file = tmp_path / "empty.bin"
    file.write_bytes(b"")
    assert _resolve_size(ctx(directory=str(tmp_path), file_name="empty.bin")) == "0b"


# width/height


def test_resolve_width_height(tmp_path):
    file = tmp_path / "img.png"
    Image.new("RGB", (320, 200)).save(file)
    assert _resolve_width(ctx(directory=str(tmp_path), file_name="img.png")) == "320"
    assert _resolve_height(ctx(directory=str(tmp_path), file_name="img.png")) == "200"


# EXIF


def _make_exif_image(tmp_path, *, datetime_original=None, make=None, model=None):
    file = tmp_path / "img.jpg"
    img = Image.new("RGB", (10, 10))
    exif = img.getexif()
    if make is not None:
        exif[271] = make
    if model is not None:
        exif[272] = model
    if datetime_original is not None:
        exif.get_ifd(0x8769)[36867] = datetime_original
    img.save(file, exif=exif)
    return file


def test_resolve_taken_at(tmp_path):
    _make_exif_image(tmp_path, datetime_original="2021:05:04 10:20:30")
    result = _resolve_taken_at(
        ctx(args="%Y-%m-%d", directory=str(tmp_path), file_name="img.jpg")
    )
    assert result == "2021-05-04"


def test_resolve_taken_at_missing_raises(tmp_path):
    _make_exif_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_taken_at(ctx(directory=str(tmp_path), file_name="img.jpg"))


def test_resolve_camera_make_and_model(tmp_path):
    _make_exif_image(tmp_path, make="Canon", model="EOS R5")
    assert (
        _resolve_camera_make(ctx(directory=str(tmp_path), file_name="img.jpg"))
        == "Canon"
    )
    assert (
        _resolve_camera_model(ctx(directory=str(tmp_path), file_name="img.jpg"))
        == "EOS R5"
    )


def test_resolve_camera_make_missing_raises(tmp_path):
    _make_exif_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_camera_make(ctx(directory=str(tmp_path), file_name="img.jpg"))


def test_resolve_camera_model_missing_raises(tmp_path):
    _make_exif_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_camera_model(ctx(directory=str(tmp_path), file_name="img.jpg"))


# GPS


def _make_gps_image(
    tmp_path,
    *,
    lat=None,
    lat_ref=None,
    lon=None,
    lon_ref=None,
    alt=None,
    alt_ref=None,
):
    file = tmp_path / "gps.jpg"
    img = Image.new("RGB", (10, 10))
    exif = img.getexif()
    gps = exif.get_ifd(0x8825)
    if lat is not None:
        gps[2] = lat
        gps[1] = lat_ref
    if lon is not None:
        gps[4] = lon
        gps[3] = lon_ref
    if alt is not None:
        gps[6] = alt
        gps[5] = alt_ref
    img.save(file, exif=exif)
    return file


def test_dms_to_decimal():
    assert _dms_to_decimal((40, 26, 46), "N") == pytest.approx(40.446111, abs=1e-5)
    assert _dms_to_decimal((40, 26, 46), "S") == pytest.approx(-40.446111, abs=1e-5)
    assert _dms_to_decimal((79, 58, 56), "W") == pytest.approx(-79.982222, abs=1e-5)
    assert _dms_to_decimal((79, 58, 56), "E") == pytest.approx(79.982222, abs=1e-5)


def test_resolve_latitude_and_longitude(tmp_path):
    _make_gps_image(
        tmp_path,
        lat=(40.0, 26.0, 46.0),
        lat_ref="N",
        lon=(79.0, 58.0, 56.0),
        lon_ref="W",
    )
    lat = _resolve_latitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))
    lon = _resolve_longitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))
    assert lat == "40.446111"
    assert lon == "-79.982222"


def test_resolve_latitude_missing_raises(tmp_path):
    _make_gps_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_latitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))


def test_resolve_longitude_missing_raises(tmp_path):
    _make_gps_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_longitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))


def test_resolve_altitude_above_and_below_sea_level(tmp_path):
    _make_gps_image(tmp_path, alt=100.5, alt_ref=0)
    result = _resolve_altitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))
    assert result == "100.5m"

    _make_gps_image(tmp_path, alt=12.0, alt_ref=1)
    result = _resolve_altitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))
    assert result == "-12.0m"


def test_resolve_altitude_missing_raises(tmp_path):
    _make_gps_image(tmp_path)
    with pytest.raises(ValueError):
        _resolve_altitude(ctx(directory=str(tmp_path), file_name="gps.jpg"))


# video


@pytest.fixture
def mock_video_metadata():
    metadata = MagicMock()
    with (
        patch(
            "renux.tags.createParser", MagicMock(return_value=MagicMock())
        ) as mock_parser,
        patch("renux.tags.extractMetadata", MagicMock(return_value=metadata)),
    ):
        mock_parser.return_value.__enter__ = MagicMock(
            return_value=mock_parser.return_value
        )
        mock_parser.return_value.__exit__ = MagicMock(return_value=False)
        yield metadata


def test_resolve_video_width_and_height(mock_video_metadata):
    mock_video_metadata.get.side_effect = lambda key: {
        "width": 1920,
        "height": 1080,
    }.get(key)
    assert _resolve_video_width(ctx(file_name="v.mp4")) == "1920"
    assert _resolve_video_height(ctx(file_name="v.mp4")) == "1080"


def test_resolve_frame_rate(mock_video_metadata):
    mock_video_metadata.get.side_effect = lambda key: {"frame_rate": 29.97}.get(key)
    assert _resolve_frame_rate(ctx(file_name="v.mp4")) == "29.97fps"


def test_resolve_frame_rate_missing_raises(mock_video_metadata):
    mock_video_metadata.get.side_effect = lambda key: None
    with pytest.raises(ValueError):
        _resolve_frame_rate(ctx(file_name="v.mp4"))


def test_resolve_duration(mock_video_metadata):
    import datetime

    mock_video_metadata.get.side_effect = lambda key: {
        "duration": datetime.timedelta(seconds=125)
    }.get(key)
    assert _resolve_duration(ctx(file_name="v.mp4")) == "125s"


def test_resolve_duration_missing_raises(mock_video_metadata):
    mock_video_metadata.get.side_effect = lambda key: None
    with pytest.raises(ValueError):
        _resolve_duration(ctx(file_name="v.mp4"))


def test_video_metadata_no_parser_raises():
    with patch("renux.tags.createParser", MagicMock(return_value=None)):
        with pytest.raises(ValueError):
            _resolve_video_width(ctx(file_name="unreadable.mp4"))
