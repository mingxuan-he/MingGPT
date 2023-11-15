import streamlit as st
from openai import OpenAI

import time
import os

from gather import gather_knowledge

st.set_page_config(page_title="MingGPT", page_icon=":robot_face:")

WELCOME = """
    Hi:wave:, Ming here. What would you like to chat about today?
    """
ABOUT = """
    This is MingGPT, the AI clone of Mingxuan He. I can chat with you about:
    - My experiences, research, and education, in either high-level or technical style
    - Discuss various topics in Web3/DeFi and data science/AI
    - My hobbies and interests  
    ## About
    :hammer_and_wrench: I'm powered by OpenAI's latest GPT-4-turbo + assistants framework, and trained on Ming's personal data.
    If you want to learn more about how I'm built, check out [my GitHub repo](https://github.com/mingxuan-he/MingGPT).
    ## Disclaimer
    :brain: All opinions are my own.  
    :books: My knowledge base is still being built, stay tuned for more updates!
    """

# initialize session
    # note: all API variables are stored in session state for persistence
if "messages" not in st.session_state:

    # load openai client
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=OPENAI_API_KEY)
    st.session_state["client"] = client

    # load assistant (prebuilt)
    assistant_id = "asst_LQRRMGpHSNc4go5xHWvKbB54"
    st.session_state["assistant_id"] = assistant_id
    #assistant = client.beta.assistants.retrieve(assistant_id)

    # check for knowledge base update
    with st.spinner("Retrieving knowledge base..."):
        gather_knowledge(client,assistant_id)
            
    # TODO: write "last updated" message
    # TODO: upload updated knowledge base to assitant via OpenAI API
    # TODO: automatic update every week (currently not supported by streamlit)

    # start thread
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id
    
    # write welcome message
    st.session_state["messages"] = [
        # TODO: write welcome message
        {"role": "assistant", "content": WELCOME}
    ]

# side bar
with st.sidebar:
    st.title("Chat with MingGPT :speech_balloon:")
    st.write(ABOUT)

# display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# start chat interface
if prompt := st.chat_input():

    # write & save user prompt
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # retrive info from session state
    client = st.session_state["client"]
    assistant_id = st.session_state["assistant_id"]
    thread_id = st.session_state["thread_id"]

    # send user prompt to assistant
    new_prompt = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    # assistant response
    with st.chat_message("assistant"):

        # wait for response
        with st.spinner("Thinking..."):
            s = None
            while s not in ["completed", "failed", "expired", "cancelled"]:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id, 
                    run_id=run.id
                    )
                s = run.status
                print(f"status:{s}")
        
        # error handling
        if s == "failed":
            st.error("Sorry, something went wrong. Please try again.")
            st.stop()
        elif s == "expired":
            st.error("Sorry, the session has expired. Please refresh the page.")
            st.stop()

        # get response
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        msg = messages.data[0]
        response_text = msg.content[0].text.value

        print(response_text)

        # TODO: avatar

        # write & save assistant response
        st.write(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})

