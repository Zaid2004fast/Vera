import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

response = llm.invoke([HumanMessage(content="What is a binary search tree? Answer in 2 sentences.")])
print("✓ Groq API working!")
print(response.content)