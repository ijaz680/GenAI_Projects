from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv
import os

# Load .env file from the same directory as this script
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found! Check your .env file.")

# System prompts for each mode
SYSTEM_PROMPTS = {
    "General Chat": """You are a helpful, friendly, and smart AI assistant.
You can answer any question on any topic — general knowledge, science, history,
advice, fun facts, or just casual conversation. Be clear, concise, and helpful.""",

    "Code Generator": """You are an expert code generator.
When the user describes what they want, write clean, well-commented, and working code.
Always explain what the code does after writing it.""",

    "Debugger": """You are an expert code debugger.
When the user shares code with an error or bug, identify the problem clearly,
explain why it happens, and provide the fixed code with explanation.""",

    "Optimizer": """You are an expert code optimizer.
When the user shares code, analyze it for performance, readability, and best practices.
Rewrite it in an optimized way and explain all the improvements you made.""",
}


class GroqClient:
    def __init__(self, model_name: str, mode: str):
        self.model_name = model_name
        self.mode = mode
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model_name=model_name,
        )

    def get_system_prompt(self) -> str:
        return SYSTEM_PROMPTS.get(self.mode, SYSTEM_PROMPTS["General Chat"])

    def chat(self, conversation_history: list) -> str:
        try:
            messages = [SystemMessage(content=self.get_system_prompt())]

            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            raise Exception(f"LLM Error: {e}")