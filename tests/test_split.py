from chatterbox_studio.text_split import split_script
import pytest


def test_preserves_all_sentences_and_paragraphs():
    result = split_script("A short start. Another statement.\n\nSecond paragraph!", 60)
    assert result == ["A short start. Another statement.", "Second paragraph!"]


def test_chunks_are_bounded_and_words_preserved():
    text = " ".join(["This is sentence number %s." % i for i in range(80)])
    result = split_script(text, 90)
    assert len(result) > 3
    assert all(0 < len(chunk) <= 90 for chunk in result)
    assert " ".join(" ".join(result).split()) == text


def test_degenerate_long_token():
    assert split_script("a" * 145, 60) == ["a" * 60, "a" * 60, "a" * 25]


def test_empty():
    assert split_script("   \n") == []


def test_bad_budget():
    with pytest.raises(ValueError):
        split_script("Text", 20)
