import streamlit as st
import os
import time
from utils import get_persona_prompt, get_persona_response

# Page configuration
st.set_page_config(
    page_title="Persona App",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'agent_dict' not in st.session_state:
    st.session_state.agent_dict = {}

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Agents", "Persona Chat", "Persona Debate"])

# Home page
if page == "Home":
    st.title("Create a New Agent")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        agent_name = st.text_input("Agent Name", key="new_agent_name")
    
    with col2:
        uploaded_file = st.file_uploader("Upload a file (PDF, DOCX, TXT, or CSV)", 
                                         type=["pdf", "docx", "txt", "csv"])
    
    if st.button("Create Agent", disabled=(not agent_name or uploaded_file is None)):
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            file_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Generate persona prompt
            persona_prompt = get_persona_prompt(agent_name, file_path)
            
            # Add to agent dictionary
            st.session_state.agent_dict[agent_name] = persona_prompt
            
            st.success(f"Agent '{agent_name}' created!")
            
            # Optional: Clean up the temporary file
            os.remove(file_path)

# Agents page
elif page == "Agents":
    st.title("Agent Library")
    
    if not st.session_state.agent_dict:
        st.info("No agents have been created yet. Go to the Home page to create an agent.")
    else:
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent to view:", agent_names)
        
        if selected_agent:
            st.subheader(f"Persona Prompt for {selected_agent}")
            st.text_area("Prompt", st.session_state.agent_dict[selected_agent], 
                         height=400, disabled=True)

# Persona Chat page
elif page == "Persona Chat":
    st.title("Chat with a Persona Agent")
    
    if not st.session_state.agent_dict:
        st.info("No agents have been created yet. Go to the Home page to create an agent.")
    else:
        # Initialize chat-specific session state variables
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        
        if 'current_persona_prompt' not in st.session_state:
            st.session_state.current_persona_prompt = None
        
        if 'current_chat_agent' not in st.session_state:
            st.session_state.current_chat_agent = None
        
        # Agent selection
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent to chat with:", agent_names)
        
        # Reset chat if agent changes
        if selected_agent != st.session_state.current_chat_agent:
            st.session_state.current_chat_agent = selected_agent
            st.session_state.current_persona_prompt = st.session_state.agent_dict[selected_agent]
            st.session_state.chat_messages = []
            st.rerun()
        
        # Display chat messages
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    st.write(f"You: {message['content']}")
                else:
                    st.write(f"{selected_agent}: {message['content']}")
        
        # Chat input
        user_message = st.chat_input("Type your message here...")
        
        if user_message:
            # Add user message to chat
            st.session_state.chat_messages.append({"role": "user", "content": user_message})
            
            with st.spinner(f"{selected_agent} is typing..."):
                # Get response from persona
                persona_response = get_persona_response(
                    st.session_state.current_persona_prompt,
                    st.session_state.chat_messages
                )
                
                # Print response for debugging
                print(f"Persona response: {persona_response}")
                
                # Add persona response to chat
                st.session_state.chat_messages.append({"role": "assistant", "content": persona_response})
            
            st.rerun()

# Persona Debate page
elif page == "Persona Debate":
    st.title("Persona Debate")
    
    if len(st.session_state.agent_dict) < 2:
        st.info("You need at least two agents for a debate. Go to the Home page to create more agents.")
    else:
        # Initialize debate-specific session state variables
        if 'agent_name_1' not in st.session_state:
            st.session_state.agent_name_1 = None
            
        if 'agent_name_2' not in st.session_state:
            st.session_state.agent_name_2 = None
            
        if 'persona_prompt_1' not in st.session_state:
            st.session_state.persona_prompt_1 = None
            
        if 'persona_prompt_2' not in st.session_state:
            st.session_state.persona_prompt_2 = None
            
        if 'messages_1' not in st.session_state:
            st.session_state.messages_1 = []
            
        if 'messages_2' not in st.session_state:
            st.session_state.messages_2 = []
            
        if 'debate_started' not in st.session_state:
            st.session_state.debate_started = False
        
        # Agent selection
        agent_names = list(st.session_state.agent_dict.keys())
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_agent_1 = st.selectbox("Agent 1:", agent_names, key="agent1_select")
            
            if selected_agent_1 != st.session_state.agent_name_1:
                st.session_state.agent_name_1 = selected_agent_1
                st.session_state.persona_prompt_1 = st.session_state.agent_dict[selected_agent_1]
                st.session_state.messages_1 = []
                st.session_state.debate_started = False
        
        with col2:
            # Filter out Agent 1 from the options for Agent 2
            agent2_options = [name for name in agent_names if name != selected_agent_1]
            if agent2_options:
                selected_agent_2 = st.selectbox("Agent 2:", agent2_options, key="agent2_select")
                
                if selected_agent_2 != st.session_state.agent_name_2:
                    st.session_state.agent_name_2 = selected_agent_2
                    st.session_state.persona_prompt_2 = st.session_state.agent_dict[selected_agent_2]
                    st.session_state.messages_2 = []
                    st.session_state.debate_started = False
        
        # Initialize the debate
        if not st.session_state.debate_started and st.session_state.agent_name_1 and st.session_state.agent_name_2:
            # Agent 1 starts with "hi"
            agent_1_message = "hi"
            st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
            st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
            st.session_state.debate_started = True
        
        # Debate conversation container
        debate_container = st.container()
        
        with debate_container:
            # Display the conversation history
            for i in range(len(st.session_state.messages_1)):
                if i % 2 == 0:  # Agent 1's turn
                    st.write(f"{st.session_state.agent_name_1}: {st.session_state.messages_1[i]['content']}")
                else:  # Agent 2's turn
                    st.write(f"{st.session_state.agent_name_2}: {st.session_state.messages_2[i]['content']}")
        
        # Button to make agents converse
        if st.button("Make agents converse") and st.session_state.debate_started:
            # Agent 2's turn
            with st.spinner(f"{st.session_state.agent_name_2} is typing..."):
                agent_2_message = get_persona_response(
                    st.session_state.persona_prompt_2,
                    st.session_state.messages_2
                )
                
                st.session_state.messages_1.append({"role": "user", "content": agent_2_message})
                st.session_state.messages_2.append({"role": "assistant", "content": agent_2_message})
                time.sleep(2)
            
            # Agent 1's turn
            with st.spinner(f"{st.session_state.agent_name_1} is typing..."):
                agent_1_message = get_persona_response(
                    st.session_state.persona_prompt_1,
                    st.session_state.messages_1
                )
                
                st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
                st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
                time.sleep(2)
            
            st.rerun()