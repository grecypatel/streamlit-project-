# import streamlit as st
# import ollama
# from typing import List, Dict
# import time
# from datetime import datetime
# import hashlib
# import json
# import os
# from pathlib import Path

# # Configure page
# st.set_page_config(
#     page_title="Coder Chat",
#     page_icon="💬",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # User data file path
# USER_DATA_FILE = Path("user_data.json")

# # Initialize user data file if it doesn't exist
# def init_user_data():
#     if not USER_DATA_FILE.exists():
#         with open(USER_DATA_FILE, "w") as f:
#             json.dump({}, f)

# # Hash password for security
# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# # Check if user exists
# def user_exists(username):
#     with open(USER_DATA_FILE, "r") as f:
#         users = json.load(f)
#     return username in users

# # Register a new user
# def register_user(username, password, email):
#     with open(USER_DATA_FILE, "r") as f:
#         users = json.load(f)
    
#     users[username] = {
#         "password": hash_password(password),
#         "email": email,
#         "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "chat_history": []
#     }
    
#     with open(USER_DATA_FILE, "w") as f:
#         json.dump(users, f)
#     return True

# # Authenticate user
# def authenticate_user(username, password):
#     with open(USER_DATA_FILE, "r") as f:
#         users = json.load(f)
    
#     if username in users and users[username]["password"] == hash_password(password):
#         return True
#     return False

# # Get user data
# def get_user_data(username):
#     with open(USER_DATA_FILE, "r") as f:
#         users = json.load(f)
#     return users.get(username, {})

# # Update user data
# def update_user_data(username, data):
#     with open(USER_DATA_FILE, "r") as f:
#         users = json.load(f)
    
#     users[username] = data
    
#     with open(USER_DATA_FILE, "w") as f:
#         json.dump(users, f)

# # Initialize session state
# def init_session_state():
#     if "logged_in" not in st.session_state:
#         st.session_state.logged_in = False
#     if "username" not in st.session_state:
#         st.session_state.username = None
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "chat_history" not in st.session_state:
#         st.session_state.chat_history = []
#     if "current_chat_id" not in st.session_state:
#         st.session_state.current_chat_id = None
#     if "debug_mode" not in st.session_state:
#         st.session_state.debug_mode = False
#     if "selected_model" not in st.session_state:
#         st.session_state.selected_model = "qwen3"  # Default model
#     if "show_delete_confirm" not in st.session_state:
#         st.session_state.show_delete_confirm = None
#     if "show_clear_confirm" not in st.session_state:
#         st.session_state.show_clear_confirm = False

# # Test Ollama connection and check if models are available
# def check_models():
#     try:
#         models = ollama.list()
#         available_models = [model['name'].split(':')[0] for model in models['models']]
#         return available_models
#     except Exception as e:
#         st.error(f"Error checking available models: {str(e)}")
#         return []

# def generate_response_stream(messages: List[Dict[str, str]], model: str):
#     try:
#         # Add system instruction at the beginning of messages
#         system_message = {
#             "role": "system", 
#             "content": "You are a coding tutor who specializes in programming and computer science topics. Your purpose is to ONLY answer questions related to coding, programming languages, algorithms, data structures, software development, debugging, and other technical computer science concepts. If a user asks a question that is not related to coding or programming, politely decline and explain that you can only assist with coding-related questions. For coding questions, explain concepts step by step, assume the user is learning, provide analogies, examples, and small exercises. Always encourage the user and avoid just giving answers without explanation."
#         }
        
#         # Check if system message is already in the messages
#         if not messages or messages[0].get("role") != "system":
#             messages_with_system = [system_message] + messages
#         else:
#             messages_with_system = messages
            
#         # Generate streaming response with the selected model
#         response = ollama.chat(
#             model=model,
#             messages=messages_with_system,
#             stream=True  # Enable streaming
#         )
        
#         return response
#     except Exception as e:
#         return None, str(e)

# # Save chat to history
# def save_chat(chat_id: str, title: str, messages: List[Dict[str, str]], model: str):
#     chat_data = {
#         "id": chat_id,
#         "title": title,
#         "messages": messages,
#         "model": model,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     }
    
#     # Remove existing chat with same ID
#     st.session_state.chat_history = [c for c in st.session_state.chat_history if c["id"] != chat_id]
#     st.session_state.chat_history.append(chat_data)
    
#     # Update user data with new chat history
#     if st.session_state.logged_in:
#         user_data = get_user_data(st.session_state.username)
#         user_data["chat_history"] = st.session_state.chat_history
#         update_user_data(st.session_state.username, user_data)

# # Load chat from history
# def load_chat(chat_id: str):
#     for chat in st.session_state.chat_history:
#         if chat["id"] == chat_id:
#             st.session_state.messages = chat["messages"]
#             st.session_state.current_chat_id = chat_id
#             # Load the model used for this chat if available
#             if "model" in chat:
#                 st.session_state.selected_model = chat["model"]
#             return True
#     return False

# # Delete a specific chat from history
# def delete_chat(chat_id: str):
#     st.session_state.chat_history = [c for c in st.session_state.chat_history if c["id"] != chat_id]
    
#     # If the deleted chat was the current chat, reset the current chat
#     if st.session_state.current_chat_id == chat_id:
#         st.session_state.messages = []
#         st.session_state.current_chat_id = None
    
#     # Update user data with updated chat history
#     if st.session_state.logged_in:
#         user_data = get_user_data(st.session_state.username)
#         user_data["chat_history"] = st.session_state.chat_history
#         update_user_data(st.session_state.username, user_data)
    
#     st.session_state.show_delete_confirm = None
#     st.rerun()

# # Clear all chat history
# def clear_chat_history():
#     st.session_state.chat_history = []
#     st.session_state.messages = []
#     st.session_state.current_chat_id = None
    
#     # Update user data with empty chat history
#     if st.session_state.logged_in:
#         user_data = get_user_data(st.session_state.username)
#         user_data["chat_history"] = []
#         update_user_data(st.session_state.username, user_data)
    
#     st.session_state.show_clear_confirm = False
#     st.rerun()

# # Generate chat title
# def get_chat_title(messages: List[Dict[str, str]]) -> str:
#     if not messages:
#         return "New Chat"
    
#     user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
#     if user_msg:
#         return user_msg[:30] + ("..." if len(user_msg) > 30 else "")
#     return "New Chat"

# # Login page
# def login_page():
#     st.title("Welcome to Coder Chat 💻")
    
#     tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
#     with tab1:
#         st.subheader("Sign In")
#         username = st.text_input("Username", key="login_username")
#         password = st.text_input("Password", type="password", key="login_password")
        
#         if st.button("Sign In", use_container_width=True):
#             if not username or not password:
#                 st.error("Please enter both username and password")
#             elif authenticate_user(username, password):
#                 st.session_state.logged_in = True
#                 st.session_state.username = username
                
#                 # Load user's chat history
#                 user_data = get_user_data(username)
#                 st.session_state.chat_history = user_data.get("chat_history", [])
                
#                 st.success(f"Welcome back, {username}!")
#                 st.rerun()
#             else:
#                 st.error("Invalid username or password")
    
#     with tab2:
#         st.subheader("Sign Up")
#         new_username = st.text_input("Username", key="signup_username")
#         new_email = st.text_input("Email", key="signup_email")
#         new_password = st.text_input("Password", type="password", key="signup_password")
#         confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
#         if st.button("Sign Up", use_container_width=True):
#             if not new_username or not new_email or not new_password or not confirm_password:
#                 st.error("Please fill all fields")
#             elif new_password != confirm_password:
#                 st.error("Passwords do not match")
#             elif len(new_password) < 6:
#                 st.error("Password must be at least 6 characters long")
#             elif user_exists(new_username):
#                 st.error("Username already exists")
#             else:
#                 if register_user(new_username, new_password, new_email):
#                     st.success(f"Account created successfully for {new_username}! Please sign in.")
#                 else:
#                     st.error("Failed to create account")

# # Main app
# def main_app():
#     # Custom CSS with only sidebar model info background color changed
#     st.markdown("""
#     <style>
#         /* Chat message styling */
#         .chat-message {
#             padding: 1rem;
#             border-radius: 0.5rem;
#             margin-bottom: 1rem;
#             display: flex;
#             align-items: flex-start;
#         }
#         .user-message {
#             background-color: #4a6572;  /* Darker blue background for user messages */
#             margin-left: auto;
#             max-width: 70%;
#         }
#         .assistant-message {
#             background-color: #2c3e50;  /* Dark blue background for AI messages */
#             margin-right: auto;
#             max-width: 70%;
#         }
#         .avatar {
#             width: 40px;
#             height: 40px;
#             border-radius: 50%;
#             display: flex;
#             align-items: center;
#             justify-content: center;
#             margin-right: 12px;
#             font-weight: bold;
#             color: white;
#             flex-shrink: 0;
#         }
#         .user-avatar {
#             background-color: #1e3a8a;  /* Darker blue to match user message background */
#         }
#         .assistant-avatar {
#             background-color: #1a5276;  /* Darker blue to match AI message background */
#         }
#         .message-content {
#             flex: 1;
#         }
#         .stDeployButton {
#             display: none;
#         }
#         .model-info {
#             background-color: #000000;  /* Changed from #f0f7ff to a soft gray */
#             padding: 10px;
#             border-radius: 5px;
#             margin-bottom: 15px;
#             text-align: left;  /* Align text to the left */
#         }
#         .model-info-container {
#             display: flex;
#             justify-content: space-between;
#             align-items: center;
#         }
#         .model-name {
#             font-weight: bold;
#         }
#         .typing-indicator {
#             display: inline-flex;
#             align-items: center;
#         }
#         .typing-indicator span {
#             height: 8px;
#             width: 8px;
#             background-color: #1a5276;
#             border-radius: 50%;
#             display: inline-block;
#             margin: 0 2px;
#             animation: pulse 1.4s infinite ease-in-out both;
#         }
#         .typing-indicator span:nth-child(1) {
#             animation-delay: -0.32s;
#         }
#         .typing-indicator span:nth-child(2) {
#             animation-delay: -0.16s;
#         }
#         @keyframes pulse {
#             0%, 80%, 100% {
#                 transform: scale(0);
#                 opacity: 0.5;
#             }
#             40% {
#                 transform: scale(1);
#                 opacity: 1;
#             }
#         }
#         .chat-item {
#             display: flex;
#             align-items: center;
#             justify-content: space-between;
#         }
#         .delete-button {
#             background-color: transparent;
#             border: none;
#             color: #ff6b6b;
#             cursor: pointer;
#             font-size: 16px;
#             padding: 0;
#             margin-left: 5px;
#         }
#         .delete-button:hover {
#             color: #ff5252;
#         }
#     </style>
#     """, unsafe_allow_html=True)
    
#     # Sidebar
#     with st.sidebar:
#         st.title("💬 Coder Chat")
        
#         # User info
#         if st.session_state.logged_in:
#             user_data = get_user_data(st.session_state.username)
#             st.markdown(f"""
#             <div class="model-info">
#                 <div class="model-info-container">
#                     <div>
#                         <strong class="model-name">User:</strong> {st.session_state.username}<br>
#                         <small>Member since: {user_data.get('created_at', 'Unknown')}</small>
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
            
#             if st.button("🚪 Logout", use_container_width=True):
#                 st.session_state.logged_in = False
#                 st.session_state.username = None
#                 st.session_state.messages = []
#                 st.session_state.chat_history = []
#                 st.session_state.current_chat_id = None
#                 st.rerun()
        
#         # Model selection
#         st.subheader("Model Selection")
#         available_models = ["llama3.2", "qwen3"]
#         selected_model = st.selectbox(
#             "Choose a model:",
#             available_models,
#             index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
#         )
        
#         # Update the selected model in session state
#         if selected_model != st.session_state.selected_model:
#             st.session_state.selected_model = selected_model
#             st.rerun()
        
#         # Model info - changed background color to soft gray
#         model_info = {
#             "llama3.2": {
#                 "name": "Llama 3.2",
#                 "description": "Meta's advanced language model"
#             },
#             "qwen3": {
#                 "name": "Qwen 3",
#                 "description": "Alibaba's efficient language model"
#             }
#         }
        
#         current_model = model_info.get(st.session_state.selected_model, {"name": "Unknown", "description": ""})
        
#         st.markdown(f"""
#         <div class="model-info">
#             <div class="model-info-container">
#                 <div>
#                     <strong class="model-name">Model:</strong> {current_model["name"]}<br>
#                     <small>{current_model["description"]}</small>
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
        
#         # Performance settings
#         st.subheader("Performance Settings")
#         batch_size = st.slider("Response Update Frequency", min_value=1, max_value=10, value=3, 
#                                help="Higher values update less frequently but may feel faster")
        
#         # Debug info
#         if st.checkbox("Debug Mode", key="debug_checkbox"):
#             st.session_state.debug_mode = True
#             st.subheader("Debug Information")
            
#             st.write(f"Messages count: {len(st.session_state.messages)}")
#             st.write(f"Chat history count: {len(st.session_state.chat_history)}")
#             st.write(f"Selected model: {st.session_state.selected_model}")
#         else:
#             st.session_state.debug_mode = False
        
#         # New chat button
#         if st.button("🆕 New Chat", use_container_width=True):
#             st.session_state.messages = []
#             st.session_state.current_chat_id = None
#             st.rerun()
        
#         # Chat history
#         st.subheader("Chat History")
        
#         # Clear all history button
#         if st.session_state.chat_history:
#             if st.button("🗑️ Clear All History", use_container_width=True):
#                 st.session_state.show_clear_confirm = True
#                 st.rerun()
        
#         # Confirmation dialog for clearing all history
#         if st.session_state.show_clear_confirm:
#             st.warning("Are you sure you want to delete all chat history? This action cannot be undone.")
#             col1, col2 = st.columns(2)
#             with col1:
#                 if st.button("Yes, delete all", key="confirm_clear_all"):
#                     clear_chat_history()
#             with col2:
#                 if st.button("Cancel", key="cancel_clear_all"):
#                     st.session_state.show_clear_confirm = False
#                     st.rerun()
        
#         # Display chat history with delete buttons
#         if st.session_state.chat_history:
#             for chat in reversed(st.session_state.chat_history):
#                 is_current = chat["id"] == st.session_state.current_chat_id
#                 button_type = "primary" if is_current else "secondary"
                
#                 # Display model icon next to chat title if available
#                 model_icon = ""
#                 if "model" in chat:
#                     if chat["model"] == "llama3.2":
#                         model_icon = "🦙 "
#                     elif chat["model"] == "qwen3":
#                         model_icon = "🌟 "
                
#                 # Chat item container
#                 chat_container = st.container()
#                 with chat_container:
#                     col1, col2 = st.columns([4, 1])
                    
#                     with col1:
#                         if st.button(
#                             f"📝 {model_icon}{chat['title']}",
#                             key=f"chat_{chat['id']}",
#                             help=chat.get("timestamp", ""),
#                             use_container_width=True,
#                             type=button_type
#                         ):
#                             load_chat(chat["id"])
#                             st.rerun()
                    
#                     with col2:
#                         if st.button(
#                             "🗑️",
#                             key=f"delete_{chat['id']}",
#                             help="Delete this chat",
#                             use_container_width=True
#                         ):
#                             st.session_state.show_delete_confirm = chat["id"]
#                             st.rerun()
                
#                 # Confirmation dialog for deleting a specific chat
#                 if st.session_state.show_delete_confirm == chat["id"]:
#                     st.warning(f"Are you sure you want to delete '{chat['title']}'? This action cannot be undone.")
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         if st.button("Yes, delete", key=f"confirm_delete_{chat['id']}"):
#                             delete_chat(chat["id"])
#                     with col2:
#                         if st.button("Cancel", key=f"cancel_delete_{chat['id']}"):
#                             st.session_state.show_delete_confirm = None
#                             st.rerun()
#         else:
#             st.info("No chat history yet")
    
#     # Main chat area
#     st.title(f"Chat with CodeMate 💻 ")
    
#     # Add a notice about the coding-only restriction
#     st.info("🔒 **Note**: This AI assistant is specialized for coding-related questions only. It will not respond to non-programming queries.")
    
#     # Display messages
#     for message in st.session_state.messages:
#         with st.container():
#             if message["role"] == "user":
#                 st.markdown(f"""
#                 <div class="chat-message user-message">
#                     <div class="avatar user-avatar">U</div>
#                     <div class="message-content">{message["content"]}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
#             else:
#                 st.markdown(f"""
#                 <div class="chat-message assistant-message">
#                     <div class="avatar assistant-avatar">AI</div>
#                     <div class="message-content">{message["content"]}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
    
#     # Chat input
#     user_input = st.chat_input("Ask a coding question...")
    
#     if user_input:
#         # Add user message
#         st.session_state.messages.append({"role": "user", "content": user_input})
        
#         # Create chat ID if new chat
#         if st.session_state.current_chat_id is None:
#             st.session_state.current_chat_id = f"chat_{int(time.time())}"
        
#         # Display user message immediately
#         with st.container():
#             st.markdown(f"""
#             <div class="chat-message user-message">
#                 <div class="avatar user-avatar">U</div>
#                 <div class="message-content">{user_input}</div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Create a placeholder for the streaming response
#         message_placeholder = st.empty()
#         full_response = ""
        
#         # Show typing indicator initially
#         with message_placeholder.container():
#             st.markdown(f"""
#             <div class="chat-message assistant-message">
#                 <div class="avatar assistant-avatar">AI</div>
#                 <div class="message-content">
#                     <div class="typing-indicator">
#                         <span></span>
#                         <span></span>
#                         <span></span>
#                     </div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
        
#         # Get the streaming response from Ollama with the selected model
#         response_stream = generate_response_stream(st.session_state.messages, st.session_state.selected_model)
        
#         if response_stream:
#             # Process the streaming response with batching
#             chunk_count = 0
#             batch_content = ""
            
#             for chunk in response_stream:
#                 # Extract content from the chunk
#                 if "message" in chunk and "content" in chunk["message"]:
#                     content = chunk["message"]["content"]
#                     batch_content += content
#                     chunk_count += 1
                    
#                     # Update the displayed response after collecting batch_size chunks
#                     if chunk_count % batch_size == 0:
#                         full_response += batch_content
                        
#                         # Update the displayed response
#                         with message_placeholder.container():
#                             st.markdown(f"""
#                             <div class="chat-message assistant-message">
#                                 <div class="avatar assistant-avatar">AI</div>
#                                 <div class="message-content">{full_response}</div>
#                             </div>
#                             """, unsafe_allow_html=True)
                        
#                         batch_content = ""  # Reset batch content
            
#             # Add any remaining content from the last batch
#             if batch_content:
#                 full_response += batch_content
#                 with message_placeholder.container():
#                     st.markdown(f"""
#                     <div class="chat-message assistant-message">
#                         <div class="avatar assistant-avatar">AI</div>
#                         <div class="message-content">{full_response}</div>
#                     </div>
#                     """, unsafe_allow_html=True)
            
#             # Add the complete response to the session state
#             st.session_state.messages.append({"role": "assistant", "content": full_response})
            
#             # Save chat with the model information
#             if st.session_state.current_chat_id:
#                 title = get_chat_title(st.session_state.messages)
#                 save_chat(st.session_state.current_chat_id, title, st.session_state.messages, st.session_state.selected_model)
#         else:
#             error_message = "I'm sorry, but I couldn't generate a response. Please try again."
#             st.session_state.messages.append({"role": "assistant", "content": error_message})
            
#             with message_placeholder.container():
#                 st.markdown(f"""
#                 <div class="chat-message assistant-message">
#                     <div class="avatar assistant-avatar">AI</div>
#                     <div class="message-content">{error_message}</div>
#                 </div>
#                 """, unsafe_allow_html=True)
        
#         # Rerun to update the interface
#         st.rerun()
    
#     # Footer
#     st.markdown("---")
#     st.markdown("AI-Powered Coding Companion ⚡")

# # Main app
# def main():
#     init_session_state()
#     init_user_data()
    
#     # Check if user is logged in
#     if not st.session_state.logged_in:
#         login_page()
#     else:
#         main_app()

# if __name__ == "__main__":
#     main()

import streamlit as st
import ollama
from typing import List, Dict
import time
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Coder Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# User data file path
USER_DATA_FILE = Path("user_data.json")

# Initialize user data file if it doesn't exist
def init_user_data():
    if not USER_DATA_FILE.exists():
        with open(USER_DATA_FILE, "w") as f:
            json.dump({}, f)

# Hash password for security
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Check if user exists
def user_exists(username):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
    return username in users

# Register a new user
def register_user(username, password, email):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "chat_history": []
    }
    
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)
    return True

# Authenticate user
def authenticate_user(username, password):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
    
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

# Get user data
def get_user_data(username):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
    return users.get(username, {})

# Update user data
def update_user_data(username, data):
    with open(USER_DATA_FILE, "r") as f:
        users = json.load(f)
    
    users[username] = data
    
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

# Initialize session state
def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "qwen3"  # Default model
    if "show_delete_confirm" not in st.session_state:
        st.session_state.show_delete_confirm = None
    if "show_clear_confirm" not in st.session_state:
        st.session_state.show_clear_confirm = False
    if "auto_save_enabled" not in st.session_state:
        st.session_state.auto_save_enabled = True  # Enable auto-save by default

# Test Ollama connection and check if models are available
def check_models():
    try:
        models = ollama.list()
        available_models = [model['name'].split(':')[0] for model in models['models']]
        return available_models
    except Exception as e:
        st.error(f"Error checking available models: {str(e)}")
        return []

def generate_response_stream(messages: List[Dict[str, str]], model: str):
    try:
        # Add system instruction at the beginning of messages
        system_message = {
            "role": "system", 
            "content": "You are a coding tutor who specializes in programming and computer science topics. Your purpose is to ONLY answer questions related to coding, programming languages, algorithms, data structures, software development, debugging, and other technical computer science concepts. If a user asks a question that is not related to coding or programming, politely decline and explain that you can only assist with coding-related questions. For coding questions, explain concepts step by step, assume the user is learning, provide analogies, examples, and small exercises. Always encourage the user and avoid just giving answers without explanation."
        }
        
        # Check if system message is already in the messages
        if not messages or messages[0].get("role") != "system":
            messages_with_system = [system_message] + messages
        else:
            messages_with_system = messages
            
        # Generate streaming response with the selected model
        response = ollama.chat(
            model=model,
            messages=messages_with_system,
            stream=True  # Enable streaming
        )
        
        return response
    except Exception as e:
        return None, str(e)

# Save chat to history
def save_chat(chat_id: str, title: str, messages: List[Dict[str, str]], model: str):
    chat_data = {
        "id": chat_id,
        "title": title,
        "messages": messages,
        "model": model,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Remove existing chat with same ID
    st.session_state.chat_history = [c for c in st.session_state.chat_history if c["id"] != chat_id]
    st.session_state.chat_history.append(chat_data)
    
    # Update user data with new chat history
    if st.session_state.logged_in:
        user_data = get_user_data(st.session_state.username)
        user_data["chat_history"] = st.session_state.chat_history
        update_user_data(st.session_state.username, user_data)

# Load chat from history
def load_chat(chat_id: str):
    for chat in st.session_state.chat_history:
        if chat["id"] == chat_id:
            st.session_state.messages = chat["messages"]
            st.session_state.current_chat_id = chat_id
            # Load the model used for this chat if available
            if "model" in chat:
                st.session_state.selected_model = chat["model"]
            return True
    return False

# Delete a specific chat from history
def delete_chat(chat_id: str):
    st.session_state.chat_history = [c for c in st.session_state.chat_history if c["id"] != chat_id]
    
    # If the deleted chat was the current chat, reset the current chat
    if st.session_state.current_chat_id == chat_id:
        st.session_state.messages = []
        st.session_state.current_chat_id = None
    
    # Update user data with updated chat history
    if st.session_state.logged_in:
        user_data = get_user_data(st.session_state.username)
        user_data["chat_history"] = st.session_state.chat_history
        update_user_data(st.session_state.username, user_data)
    
    st.session_state.show_delete_confirm = None
    st.rerun()

# Clear all chat history
def clear_chat_history():
    st.session_state.chat_history = []
    st.session_state.messages = []
    st.session_state.current_chat_id = None
    
    # Update user data with empty chat history
    if st.session_state.logged_in:
        user_data = get_user_data(st.session_state.username)
        user_data["chat_history"] = []
        update_user_data(st.session_state.username, user_data)
    
    st.session_state.show_clear_confirm = False
    st.rerun()

# Generate chat title
def get_chat_title(messages: List[Dict[str, str]]) -> str:
    if not messages:
        return "New Chat"
    
    user_msg = next((m["content"] for m in messages if m["role"] == "user"), "")
    if user_msg:
        return user_msg[:30] + ("..." if len(user_msg) > 30 else "")
    return "New Chat"

# Load user's chat history
def load_user_chat_history():
    if st.session_state.logged_in:
        user_data = get_user_data(st.session_state.username)
        st.session_state.chat_history = user_data.get("chat_history", [])
        return True
    return False

# Login page
def login_page():
    st.title("Welcome to Coder Chat 💻")
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        st.subheader("Sign In")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Sign In", use_container_width=True):
            if not username or not password:
                st.error("Please enter both username and password")
            elif authenticate_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                
                # Load user's chat history
                load_user_chat_history()
                
                st.success(f"Welcome back, {username}! Your chat history has been loaded.")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Sign Up", use_container_width=True):
            if not new_username or not new_email or not new_password or not confirm_password:
                st.error("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            elif user_exists(new_username):
                st.error("Username already exists")
            else:
                if register_user(new_username, new_password, new_email):
                    st.success(f"Account created successfully for {new_username}! Please sign in.")
                else:
                    st.error("Failed to create account")

# Main app
def main_app():
    # Load user's chat history if not already loaded
    if st.session_state.logged_in and not st.session_state.chat_history:
        load_user_chat_history()
        if st.session_state.chat_history:
            st.info(f"Loaded {len(st.session_state.chat_history)} previous chat sessions.")
    
    # Custom CSS with only sidebar model info background color changed
    st.markdown("""
    <style>
        /* Chat message styling */
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: flex-start;
        }
        .user-message {
            background-color: #4a6572;  /* Darker blue background for user messages */
            margin-left: auto;
            max-width: 70%;
        }
        .assistant-message {
            background-color: #2c3e50;  /* Dark blue background for AI messages */
            margin-right: auto;
            max-width: 70%;
        }
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-weight: bold;
            color: white;
            flex-shrink: 0;
        }
        .user-avatar {
            background-color: #1e3a8a;  /* Darker blue to match user message background */
        }
        .assistant-avatar {
            background-color: #1a5276;  /* Darker blue to match AI message background */
        }
        .message-content {
            flex: 1;
        }
        .stDeployButton {
            display: none;
        }
        .model-info {
            background-color: #000000;  /* Changed from #f0f7ff to a soft gray */
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 15px;
            text-align: left;  /* Align text to the left */
        }
        .model-info-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .model-name {
            font-weight: bold;
        }
        .typing-indicator {
            display: inline-flex;
            align-items: center;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            background-color: #1a5276;
            border-radius: 50%;
            display: inline-block;
            margin: 0 2px;
            animation: pulse 1.4s infinite ease-in-out both;
        }
        .typing-indicator span:nth-child(1) {
            animation-delay: -0.32s;
        }
        .typing-indicator span:nth-child(2) {
            animation-delay: -0.16s;
        }
        @keyframes pulse {
            0%, 80%, 100% {
                transform: scale(0);
                opacity: 0.5;
            }
            40% {
                transform: scale(1);
                opacity: 1;
            }
        }
        .chat-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .delete-button {
            background-color: transparent;
            border: none;
            color: #ff6b6b;
            cursor: pointer;
            font-size: 16px;
            padding: 0;
            margin-left: 5px;
        }
        .delete-button:hover {
            color: #ff5252;
        }
        .save-indicator {
            font-size: 0.8em;
            color: #4CAF50;
            margin-top: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.title("💬 Coder Chat")
        
        # User info
        if st.session_state.logged_in:
            user_data = get_user_data(st.session_state.username)
            st.markdown(f"""
            <div class="model-info">
                <div class="model-info-container">
                    <div>
                        <strong class="model-name">User:</strong> {st.session_state.username}<br>
                        <small>Member since: {user_data.get('created_at', 'Unknown')}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.messages = []
                st.session_state.chat_history = []
                st.session_state.current_chat_id = None
                st.rerun()
        
        # Model selection
        st.subheader("Model Selection")
        available_models = ["llama3.2", "qwen3"]
        selected_model = st.selectbox(
            "Choose a model:",
            available_models,
            index=available_models.index(st.session_state.selected_model) if st.session_state.selected_model in available_models else 0
        )
        
        # Update the selected model in session state
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.rerun()
        
        # Model info - changed background color to soft gray
        model_info = {
            "llama3.2": {
                "name": "Llama 3.2",
                "description": "Meta's advanced language model"
            },
            "qwen3": {
                "name": "Qwen 3",
                "description": "Alibaba's efficient language model"
            }
        }
        
        current_model = model_info.get(st.session_state.selected_model, {"name": "Unknown", "description": ""})
        
        st.markdown(f"""
        <div class="model-info">
            <div class="model-info-container">
                <div>
                    <strong class="model-name">Model:</strong> {current_model["name"]}<br>
                    <small>{current_model["description"]}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-save setting
        st.subheader("Chat Settings")
        auto_save_enabled = st.checkbox("Auto-save chats", value=st.session_state.auto_save_enabled, 
                                        help="Automatically save your chats to history")
        if auto_save_enabled != st.session_state.auto_save_enabled:
            st.session_state.auto_save_enabled = auto_save_enabled
        
        # Performance settings
        st.subheader("Performance Settings")
        batch_size = st.slider("Response Update Frequency", min_value=1, max_value=10, value=3, 
                               help="Higher values update less frequently but may feel faster")
        
        # Debug info
        if st.checkbox("Debug Mode", key="debug_checkbox"):
            st.session_state.debug_mode = True
            st.subheader("Debug Information")
            
            st.write(f"Messages count: {len(st.session_state.messages)}")
            st.write(f"Chat history count: {len(st.session_state.chat_history)}")
            st.write(f"Selected model: {st.session_state.selected_model}")
            st.write(f"Auto-save enabled: {st.session_state.auto_save_enabled}")
        else:
            st.session_state.debug_mode = False
        
        # New chat button
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.current_chat_id = None
            st.rerun()
        
        # Chat history
        st.subheader("Chat History")
        
        # Show save status
        if st.session_state.auto_save_enabled:
            st.markdown('<div class="save-indicator">✓ Auto-save enabled</div>', unsafe_allow_html=True)
        
        # Clear all history button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear All History", use_container_width=True):
                st.session_state.show_clear_confirm = True
                st.rerun()
        
        # Confirmation dialog for clearing all history
        if st.session_state.show_clear_confirm:
            st.warning("Are you sure you want to delete all chat history? This action cannot be undone.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete all", key="confirm_clear_all"):
                    clear_chat_history()
            with col2:
                if st.button("Cancel", key="cancel_clear_all"):
                    st.session_state.show_clear_confirm = False
                    st.rerun()
        
        # Display chat history with delete buttons
        if st.session_state.chat_history:
            for chat in reversed(st.session_state.chat_history):
                is_current = chat["id"] == st.session_state.current_chat_id
                button_type = "primary" if is_current else "secondary"
                
                # Display model icon next to chat title if available
                model_icon = ""
                if "model" in chat:
                    if chat["model"] == "llama3.2":
                        model_icon = "🦙 "
                    elif chat["model"] == "qwen3":
                        model_icon = "🌟 "
                
                # Chat item container
                chat_container = st.container()
                with chat_container:
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        if st.button(
                            f"📝 {model_icon}{chat['title']}",
                            key=f"chat_{chat['id']}",
                            help=chat.get("timestamp", ""),
                            use_container_width=True,
                            type=button_type
                        ):
                            load_chat(chat["id"])
                            st.rerun()
                    
                    with col2:
                        if st.button(
                            "🗑️",
                            key=f"delete_{chat['id']}",
                            help="Delete this chat",
                            use_container_width=True
                        ):
                            st.session_state.show_delete_confirm = chat["id"]
                            st.rerun()
                
                # Confirmation dialog for deleting a specific chat
                if st.session_state.show_delete_confirm == chat["id"]:
                    st.warning(f"Are you sure you want to delete '{chat['title']}'? This action cannot be undone.")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Yes, delete", key=f"confirm_delete_{chat['id']}"):
                            delete_chat(chat["id"])
                    with col2:
                        if st.button("Cancel", key=f"cancel_delete_{chat['id']}"):
                            st.session_state.show_delete_confirm = None
                            st.rerun()
        else:
            st.info("No chat history yet")
    
    # Main chat area
    st.title(f"Chat with CodeMate 💻 ")
    
    # Add a notice about the coding-only restriction
    st.info("🔒 **Note**: This AI assistant is specialized for coding-related questions only. It will not respond to non-programming queries.")
    
    # Display messages
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="avatar user-avatar">U</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="avatar assistant-avatar">AI</div>
                    <div class="message-content">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask a coding question...")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Create chat ID if new chat
        if st.session_state.current_chat_id is None:
            st.session_state.current_chat_id = f"chat_{int(time.time())}"
        
        # Display user message immediately
        with st.container():
            st.markdown(f"""
            <div class="chat-message user-message">
                <div class="avatar user-avatar">U</div>
                <div class="message-content">{user_input}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Create a placeholder for the streaming response
        message_placeholder = st.empty()
        full_response = ""
        
        # Show typing indicator initially
        with message_placeholder.container():
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <div class="avatar assistant-avatar">AI</div>
                <div class="message-content">
                    <div class="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Get the streaming response from Ollama with the selected model
        response_stream = generate_response_stream(st.session_state.messages, st.session_state.selected_model)
        
        if response_stream:
            # Process the streaming response with batching
            chunk_count = 0
            batch_content = ""
            
            for chunk in response_stream:
                # Extract content from the chunk
                if "message" in chunk and "content" in chunk["message"]:
                    content = chunk["message"]["content"]
                    batch_content += content
                    chunk_count += 1
                    
                    # Update the displayed response after collecting batch_size chunks
                    if chunk_count % batch_size == 0:
                        full_response += batch_content
                        
                        # Update the displayed response
                        with message_placeholder.container():
                            st.markdown(f"""
                            <div class="chat-message assistant-message">
                                <div class="avatar assistant-avatar">AI</div>
                                <div class="message-content">{full_response}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        batch_content = ""  # Reset batch content
            
            # Add any remaining content from the last batch
            if batch_content:
                full_response += batch_content
                with message_placeholder.container():
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="avatar assistant-avatar">AI</div>
                        <div class="message-content">{full_response}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Add the complete response to the session state
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save chat with the model information if auto-save is enabled
            if st.session_state.auto_save_enabled and st.session_state.current_chat_id:
                title = get_chat_title(st.session_state.messages)
                save_chat(st.session_state.current_chat_id, title, st.session_state.messages, st.session_state.selected_model)
        else:
            error_message = "I'm sorry, but I couldn't generate a response. Please try again."
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            
            with message_placeholder.container():
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <div class="avatar assistant-avatar">AI</div>
                    <div class="message-content">{error_message}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Rerun to update the interface
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("AI-Powered Coding Companion ⚡")

# Main app
def main():
    init_session_state()
    init_user_data()
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()