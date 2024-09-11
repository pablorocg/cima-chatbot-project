# Pendiente acabar de implementar

from langchain.schema import AIMessage, HumanMessage
import gradio as gr
from langchain_ollama.chat_models import ChatOllama

llm = ChatOllama(model="gemma2:2b", base_url="http://ollama:11434")
def predict(message, history):
    history_langchain_format = []
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=message))
    gpt_response = llm.invoke(history_langchain_format)
    return gpt_response.content

gr.ChatInterface(predict).launch(server_name="0.0.0.0", server_port=9012) # Inicializar en el puerto 9012


    