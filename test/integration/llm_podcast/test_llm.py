"""Tests for 'llm' module."""

from llm_podcast.llm import query_llm


def test_query_llm():
    system = "give the response for a calculation."
    input = "1+1"

    response = query_llm(
        system=system,
        input=input,
        temperature=0.5,
    )

    print(response)
    assert "2" in response
