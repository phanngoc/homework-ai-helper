import os
import streamlit as st
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from mem0 import Memory
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()
# Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["MEM0_API_KEY"] =  os.getenv("MEM0_API_KEY")

# Initialize LangChain and Mem0
llm = ChatOpenAI(model="gpt-4o-mini")
# mem0 = MemoryClient(api_key=os.environ["MEM0_API_KEY"])
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o",
            "temperature": 0.1,
            "max_tokens": 2000,
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j", 
            "password": "ttt@123ASD"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "localhost",
            "port": 6333,
        }
    },
    "version": "v1.1"
}

memory = Memory.from_config(config_dict=config)

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""You are a helpful travel agent AI. Use the provided context to personalize your responses and remember user preferences and past interactions. 
    Provide travel recommendations, itinerary suggestions, and answer questions about destinations. 
    If you don't have specific information, you can make general suggestions based on common travel knowledge."""),
    MessagesPlaceholder(variable_name="context"),
    HumanMessage(content="{input}")
])

def retrieve_context(query: str, user_id: str) -> List[Dict]:
    """Retrieve relevant context from Mem0"""
    memories = memory.search(query, user_id=user_id)
    print('retrieve_context:memories', memories)
    # Process memories and relations
    relation_texts = []
    if 'relations' in memories:
        for rel in memories['relations']:
            relation_texts.append(f"{rel['source']} {rel['relationship']} {rel['destination']}")

    # Combine memory results and relations
    memory_texts = []
    if 'results' in memories:
        memory_texts = [mem["memory"] for mem in memories['results']]
    
    seralized_memories = ' '.join(memory_texts + relation_texts)
    print('context', seralized_memories)
    context = [
        {
            "role": "system", 
            "content": f"Relevant information: {seralized_memories}"
        },
        {
            "role": "user",
            "content": query
        }
    ]
    return context

def generate_response(input: str, context: List[Dict]) -> str:
    """Generate a response using the language model"""
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "input": input
    })
    print('generate_response', response)
    return response.content

def save_interaction(user_id: str, user_input: str, assistant_response):
    """Save the interaction to Mem0"""
    print('save_interaction:user_id:', user_id)
    print('save_interaction:user_input:', user_input)
    print('save_interaction:assistant_response:', assistant_response)
    interaction = [
        {
          "role": "user",
          "content": user_input
        },
        {
            "role": "assistant",
            "content": assistant_response
        }
    ]
    try:
        memory.add(interaction, user_id=user_id)
    except Exception as e:
        print(f"Error saving interaction:", e)
        memory.add(user_input, user_id=user_id)
        memory.add(assistant_response, user_id=user_id)


def chat_turn(user_input, user_id) -> str:
    # Retrieve context
    print(f"User input:", user_input, user_id)
    context = retrieve_context(user_input, user_id)
    
    # Generate response
    response = generate_response(user_input, context)
    
    # Save interaction
    save_interaction(user_id, user_input, response)
    
    return response


if __name__ == "__main__":
    st.title("Travel Agent Planner")
    st.write("How can I assist you with your travel plans today?")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_id = "john"  # You can modify this to handle multiple users
    if user_mes := st.chat_input("Enter your message"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_mes)
        st.session_state.messages.append({"role": "user", "content": user_mes})
        
        # Get AI response
        response = chat_turn(user_mes, user_id)
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


