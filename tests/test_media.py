"""Unit tests for workspace.core.ops.read_media and write_media."""

from workspace.core.ops import read_media, write_media


def test_write_then_read_media_roundtrips_bytes(tmp_path):
    data = bytes(range(256))

    write_media(tmp_path, "blob.bin", data)
    media = read_media(tmp_path, "blob.bin")

    assert media.data == data


def test_read_media_guesses_mime_type_from_extension(tmp_path):
    write_media(tmp_path, "photo.jpg", b"not a real jpeg, just bytes")

    media = read_media(tmp_path, "photo.jpg")

    assert media.mime_type == "image/jpeg"


def test_read_media_falls_back_to_octet_stream(tmp_path):
    write_media(tmp_path, "blob.bin", b"\x00\x01\x02")

    media = read_media(tmp_path, "blob.bin")

    assert media.mime_type == "application/octet-stream"
