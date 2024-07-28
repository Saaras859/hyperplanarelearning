import streamlit as st
import google.generativeai as genai

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

st.set_page_config(
    page_title="Q&A Demo",
    page_icon=":robot_face:",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .header {
            font-size: 24px;
            color: #4CAF50;
            text-align: center;
        }
        .subheader {
            font-size: 18px;
            color: #2196F3;
        }
        .content {
            font-size: 16px;
            color: #333;
        }
        .streamlit-expanderHeader {
            font-size: 18px;
            font-weight: bold;
        }
        .you-message {
            background-color: #1e1e1e;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .bot-message {
            background-color: #333333;
            color: #ffffff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
    </style>
    <div class="header">League Bot</div>
""", unsafe_allow_html=True)

if 'sessions' not in st.session_state:
    st.session_state['sessions'] = {}
if 'current_session' not in st.session_state:
    st.session_state['current_session'] = None
if 'context' not in st.session_state:
    st.session_state['context'] = (
        "You are a 15-year-old boy with a casual, laid-back style of speaking. "
        "You are also an expert in League of Legends, providing builds and advice for various champions. "
    )

st.sidebar.header("Settings")
user_name = st.sidebar.text_input("Your Name", "")
theme_color = st.sidebar.color_picker("Pick A Color", "#00f900")

session_name = st.sidebar.text_input("Session Name", "")
if st.sidebar.button("Start New Session"):
    if session_name:
        st.session_state['sessions'][session_name] = []
        st.session_state['current_session'] = session_name

current_session = st.session_state['current_session']
if current_session:
    st.sidebar.write(f"Current Session: {current_session}")
    if st.sidebar.button("End Current Session"):
        st.session_state['current_session'] = None

def summarize_chat_history(chat_history):
    summary = "Summary of chat history:\n"
    for role, text in chat_history:
        summary += f"{role}: {text}\n"
    return summary

if current_session:
    context = st.text_area("Update Context", value=st.session_state['context'])
    if st.button("Update Context"):
        chat_history = st.session_state['sessions'][current_session]
        summary = summarize_chat_history(chat_history)
        st.session_state['context'] = context + "\n\n" + summary
        st.success("Context updated successfully!")

def get_gemini_response(question, chat_history):
    try:
        context = st.session_state['context']
        for role, text in chat_history:
            context += f"{role}: {text}\n"
        context += f"You: {question}\nBot: "
        
        response = chat.send_message(context, stream=True)
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []

input_text = st.text_input("Input:", key="input", placeholder="Ask about League of Legends builds or advice...")
submit = st.button("Ask the question", help="Click to get a response from Gemini.")

if submit and input_text and current_session:
    response = get_gemini_response(input_text, st.session_state['sessions'][current_session])
    if response:
        chat_history = st.session_state['sessions'][current_session]
        chat_history.append(("You", input_text))
        st.subheader("The Response is")
        for chunk in response:
            st.write(chunk.text)
            chat_history.append(("Bot", chunk.text))

st.subheader("The Chat History is")
if current_session:
    chat_history = st.session_state['sessions'][current_session]
    for role, text in chat_history:
        if role == "You":
            st.markdown(f"<div class='you-message'>{role}: {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-message'>{role}: {text}</div>", unsafe_allow_html=True)
else:
    st.write("No session selected. Start a new session to chat.")

uploaded_file = st.file_uploader("Choose a text file with questions", type="txt")
if uploaded_file is not None and current_session:
    questions = uploaded_file.read().decode("utf-8").splitlines()
    chat_history = st.session_state['sessions'][current_session]
    st.subheader("Batch Responses")
    for question in questions:
        response = get_gemini_response(question, chat_history)
        chat_history.append(("You", question))
        st.write(f"Question: {question}")
        for chunk in response:
            st.write(chunk.text)
            chat_history.append(("Bot", chunk.text))
