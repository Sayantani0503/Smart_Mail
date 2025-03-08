import streamlit as st
from email_functions import get_email, llama_call  # Importing your email processing module

# Set up Streamlit page
st.set_page_config(page_title="Email Assistant", page_icon="📧", layout="wide")

st.title("📧 Smart Email Assistant")
st.write("An AI-powered assistant to help you manage and respond to emails efficiently.")

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["📥 Inbox", "🤖 AI Assistant"])

# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Initialize chat history

if page == "📥 Inbox":
    st.header("📥 Your Emails")
    
    # Fetch emails using get_email function
    emails = get_email()
    
    if emails:
        for mail in emails:
            with st.expander(f"📩 {mail['subject']} - {mail['from']}"):
                st.write(f"**From:** {mail['from']}")
                st.write(f"**Date:** {mail.get('date', 'Unknown Date')}")
                st.write(f"**Content:** {mail['body']}")
    else:
        st.info("No new emails found.")

elif page == "🤖 AI Assistant":
    st.header("🤖 AI Email Assistant")
    
    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Ask me anything about your emails...")
    
    if user_input:
        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append(f"User: {user_input}")  # Add to chat history
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate AI response using llama_call with history context
        context = "\n".join(st.session_state.chat_history)  # Combine chat history
        response = llama_call(f"{context}\nUser: {user_input}")  # Pass context
        
        # Display AI response
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Store response in chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append(f"Assistant: {response}")  
