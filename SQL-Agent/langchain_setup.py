import os
import uuid
from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy import create_engine

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage
    from langchain_postgres import PostgresChatMessageHistory
    from langchain_community.utilities import SQLDatabase
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain.agents import create_agent
    from langchain.agents.middleware import HumanInTheLoopMiddleware
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.types import Command
    import psycopg
except ImportError as exc:
    raise SystemExit(
        "Missing optional packages. Install with: "
        "pip install langchain langgraph langchain-community \"langchain[google-genai]\" "
        "langchain-postgres langchain-ollama sqlalchemy psycopg2-binary psycopg"
    ) from exc


@dataclass(frozen=True)
class Settings:
    model_provider: str
    ollama_model: str
    langsmith_api_key: Optional[str]
    google_api_key: Optional[str]
    database_url: Optional[str]
    session_id: str


def load_settings() -> Settings:
    session_id = os.getenv("SESSION_ID")
    if not session_id:
        session_id = str(uuid.uuid4())
    return Settings(
        model_provider=os.getenv("MODEL_PROVIDER", "ollama").strip().lower(),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        database_url=os.getenv("NEON_DATABASE_URL"),
        session_id=session_id,
    )


def validate_settings(settings: Settings) -> None:
    missing = []
    if not settings.langsmith_api_key:
        missing.append("LANGSMITH_API_KEY")
    if settings.model_provider == "gemini" and not settings.google_api_key:
        missing.append("GOOGLE_API_KEY")
    if not settings.database_url:
        missing.append("NEON_DATABASE_URL")
    if missing:
        missing_list = ", ".join(missing)
        raise SystemExit(f"Missing required environment variables: {missing_list}")


def setup_langsmith_env(settings: Settings) -> None:
    os.environ["LANGSMITH_TRACING"] = "true"
    if settings.langsmith_api_key:
        os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key


def setup_google_env(settings: Settings) -> None:
    if settings.google_api_key:
        os.environ["GOOGLE_API_KEY"] = settings.google_api_key


def init_model(settings: Settings) -> Any:
    if settings.model_provider == "ollama":
        return ChatOllama(model=settings.ollama_model, temperature=0)
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)


def test_model(model: Any, settings: Settings) -> None:
    try:
        response = model.invoke([HumanMessage(content="say hello world")])
    except ChatGoogleGenerativeAIError as exc:
        raise SystemExit(f"Gemini API error: {exc}") from exc
    except Exception as exc:
        provider = "Ollama" if settings.model_provider == "ollama" else "model"
        raise SystemExit(f"{provider} error: {exc}") from exc
    print(response.content)


def init_sql_tools(database_url: str, model: Any) -> tuple[SQLDatabase, list]:
    db = SQLDatabase.from_uri(database_url)
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    return db, toolkit.get_tools()


def build_system_prompt(dialect: str, top_k: int = 5) -> str:
    return (
        "You are an agent designed to interact with a SQL database.\n"
        "Given an input question, create a syntactically correct "
        f"{dialect} query to run,\n"
        "then look at the results of the query and return the answer. Unless the user\n"
        "specifies a specific number of examples they wish to obtain, always limit your\n"
        f"query to at most {top_k} results.\n\n"
        "You can order the results by a relevant column to return the most interesting\n"
        "examples in the database. Never query for all the columns from a specific table,\n"
        "only ask for the relevant columns given the question.\n\n"
        "You MUST double check your query before executing it. If you get an error while\n"
        "executing a query, rewrite the query and try again.\n\n"
        "DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the\n"
        "database.\n\n"
        "To start you should ALWAYS look at the tables in the database to see what you\n"
        "can query. Do NOT skip this step.\n\n"
        "Then you should query the schema of the most relevant tables.\n"
    )


def init_agent(model: Any, db: SQLDatabase, tools: list):
    system_prompt = build_system_prompt(db.dialect, top_k=5)
    return create_agent(
        model,
        tools,
        system_prompt=system_prompt,
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={"sql_db_query": True},
                description_prefix="Tool execution pending approval",
            ),
        ],
        checkpointer=InMemorySaver(),
    )


def run_agent(agent) -> None:
    question = "What is the average order amount?"
    config = {"configurable": {"thread_id": "1"}}

    for step in agent.stream(
        {"messages": [{"role": "user", "content": question}]},
        config,
        stream_mode="values",
    ):
        if "__interrupt__" in step:
            print("INTERRUPTED:")
            interrupt = step["__interrupt__"][0]
            for request in interrupt.value["action_requests"]:
                print(request["description"])
        elif "messages" in step:
            step["messages"][-1].pretty_print()

    for step in agent.stream(
        Command(resume={"decisions": [{"type": "approve"}]}),
        config,
        stream_mode="values",
    ):
        if "__interrupt__" in step:
            print("INTERRUPTED:")
            interrupt = step["__interrupt__"][0]
            for request in interrupt.value["action_requests"]:
                print(request["description"])
        elif "messages" in step:
            step["messages"][-1].pretty_print()


def init_postgres_history(
    database_url: str,
    session_id: str,
) -> tuple[PostgresChatMessageHistory, "psycopg.Connection"]:
    _ = create_engine(database_url)
    connection = psycopg.connect(database_url)
    history = PostgresChatMessageHistory(
        "message_store",
        session_id,
        sync_connection=connection,
    )
    return history, connection


def test_postgres_history(history: PostgresChatMessageHistory) -> None:
    history.add_user_message("Hello, how are you?")
    history.add_ai_message("I am doing well, thank you!")

    print("Messages added and retrieved from DB:")
    for msg in history.messages:
        print(f"  {msg.type.capitalize()}: {msg.content}")


def main() -> None:
    if load_dotenv:
        load_dotenv()
    else:
        print("python-dotenv not installed; .env file will be ignored.")

    settings = load_settings()
    validate_settings(settings)

    setup_langsmith_env(settings)
    setup_google_env(settings)

    model = init_model(settings)
    print(f"Model initialized using provider: {settings.model_provider}")
    test_model(model, settings)

    db, tools = init_sql_tools(settings.database_url, model)
    print("SQL tools initialized:")
    for tool in tools:
        print(f"{tool.name}: {tool.description}\n")

    agent = init_agent(model, db, tools)
    print("SQL agent initialized.")
    run_agent(agent)

    history, connection = init_postgres_history(settings.database_url, settings.session_id)
    try:
        print(f"PostgresChatMessageHistory initialized for session: {settings.session_id}")
        test_postgres_history(history)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
