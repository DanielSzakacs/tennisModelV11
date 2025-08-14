from src.data.entities import _normalize, EntityResolver


def test_normalize():
    assert _normalize("Ábel  ") == "abel"


def test_resolver_suggestions():
    resolver = EntityResolver()
    _, sugg = resolver.resolve("Nonexistent Player")
    assert isinstance(sugg, list)
