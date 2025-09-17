from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# 1. State Graph Definition and Creation
# A state graph is a state machine that contains the nodes and edges. 
class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    # Annotated[0] specifies the type of the key.
    # Annotated[1] can either contain a comment describing the key or
    # a funciton that will be called to update the key. In this case, langgraph's add_messages function.
    messages: Annotated[list, add_messages] #This is the conversation history. Will be continually updated.

#Create an empty State Graph.
graph_builder = StateGraph(State)

# 2. Node Definition and Creation
# Each node is a function that takes a state and returns a state.
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
print("Google API Key:", google_api_key[:5] + "..." if google_api_key else "MISSING")


llm = init_chat_model("google_genai:gemini-2.0-flash")

def chatbot(state: State):
    """
    Represents a node of the chatbot.
    Input: State, ie. a previous node.
    Output: A Dictionary containing an updated list of messages under the key "messages".
    """
    return {"messages": [llm.invoke(state["messages"])]} #Update the messages list with the new message.


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)


#Entry point specifies where the run is started
graph_builder.add_edge(START, "chatbot")



#Exit point specifies where the run is ended
graph_builder.add_edge("chatbot", END)

#Compile the graph
graph = graph_builder.compile()

#Run the graph
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break