import streamlit as st
from openai import OpenAI
import time
import dotenv

# TODO: check if knowledge base needs update

st.title("Chat with MingGPT 💬")

WELCOME = """
    Hi, I'm MingGPT. How can I help you?
    """

# initialize session
    # note: all API variables are stored in session state for persistence
if "messages" not in st.session_state:

    # load openai client
    dotenv.load_dotenv()
    client = OpenAI()
    st.session_state["client"] = client

    # load assistant (prebuilt)
    assistant_id = "asst_LQRRMGpHSNc4go5xHWvKbB54"
    st.session_state["assistant_id"] = assistant_id
    #assistant = client.beta.assistants.retrieve(assistant_id)

    # start thread
    thread = client.beta.threads.create()
    st.session_state["thread_id"] = thread.id
    
    # write welcome message
    st.session_state["messages"] = [
        # TODO: write welcome message
        {"role": "assistant", "content": WELCOME}
    ]

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

    # wait for response
    # TODO: spinner & waiting message with st.status
    s = None
    while s != "completed":
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id, 
            run_id=run.id
            )
        s = run.status
        print(f"status:{s}")

    # get assistant response
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    msg = messages.data[0]
    response_text = msg.content[0].text.value

    for m in reversed(messages.data):
        print(m.role)
        print(m.content[0].text.value)
        print("\n")

    # TODO: avatar

    # write & save assistant response
    st.chat_message("assistant").write(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})

