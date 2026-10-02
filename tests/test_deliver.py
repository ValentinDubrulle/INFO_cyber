from digest.deliver import parse_recipients


def test_parse_recipients():
    assert parse_recipients("a@x.fr, b@y.fr;c@z.fr  d@w.fr,") == ["a@x.fr", "b@y.fr", "c@z.fr", "d@w.fr"]
    assert parse_recipients("a@x.fr") == ["a@x.fr"]
    assert parse_recipients(" ") == []
