"""Function(s) for querying LLM."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from llm_podcast.settings import Settings


def query_llm(
    *,
    system: str,
    input: str,
    temperature: float,
) -> str:
    """Query LLM for a response.

    Args:
        system: System prompt.
        input: User input for model to work on.
        temperature: Temperature setting for model.

    Returns:
        Response from LLM.
    """
    settings = Settings()
    chat = ChatOpenAI(
        api_key=settings.openai_api_key,
        model="gpt-4o-mini",
        temperature=temperature,
        stop_sequences=None,
    )
    prompt = ChatPromptTemplate.from_messages(
        messages=[
            ("system", system),
            ("human", "{input}"),
        ],
    )
    chain = prompt | chat
    message = chain.invoke({"input": input})

    return str(message.content)


if __name__ == "__main__":
    print(
        query_llm(
            system="Antworte in Kölschem Dialekt",
            input="Was ist 1 plus 1?",
            temperature=2.0,
        )
    )
