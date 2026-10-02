from datetime import date

from digest.main import archive_path


def test_archive_never_overwrites(tmp_path):
    day = date(2026, 10, 2)
    first = archive_path(tmp_path, day)
    assert first.name == "2026-10-02.md"
    first.write_text("a")
    second = archive_path(tmp_path, day)
    assert second.name == "2026-10-02-2.md"
    second.write_text("b")
    assert archive_path(tmp_path, day).name == "2026-10-02-3.md"
    assert first.read_text() == "a"
