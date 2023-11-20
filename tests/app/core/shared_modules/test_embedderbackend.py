"""Created by agarc at 04/10/2023
Features:
"""
import pytest

from app.core.shared_modules.embedderbackend import EmbedderBackend
from app.settings import Settings

settings = Settings()
embedder = EmbedderBackend(settings)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_embed_string_valid():
    string = r"""
    This is a very long string with a lot of wierd characters
    !@#$%^ &*()_+-= {}[]|\:;"' <>,.? /~
    And we will embed this
    """
    embedded = embedder.embed_string(string)
    assert len(embedded) == 1536
    assert isinstance(embedded[0], float)


@pytest.mark.skip_this(
    reason="Skipping test from running because it is calling OpenAI-API",
)
def test_embed_string_empty():
    string = ""
    embedded = embedder.embed_string(string)
    assert embedded is None


if __name__ == "__main__":
    pytest.main()
