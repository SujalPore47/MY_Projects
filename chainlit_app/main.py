import chainlit as cl
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import os
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from dotenv import load_dotenv
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

@cl.on_chat_start
async def on_chat_start():
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        api_key=google_api_key
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions."),
        ("human", "{question}")
    ])
    
    runnable = prompt | model | StrOutputParser()
    # Store the runnable object in the user session
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    # Retrieve the runnable object from the user session
    runnable = cl.user_session.get("runnable")  # type: Runnable
    if runnable is None:
        await cl.Message(content="Runnable not initialized. Please restart the session.").send()
        return
    msg = cl.Message(content="")
    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)
    await msg.send()