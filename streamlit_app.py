import os
import requests
import streamlit as st
from openai import AzureOpenAI

# Environment variables setup
endpoint = os.getenv("ENDPOINT_URL", "https://sonatasparkazureopenai.openai.azure.com/")
deployment = os.getenv("DEPLOYMENT_NAME", "Spark")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "6e41006003494c568d613e80046b5680")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=subscription_key,
    api_version="2024-05-01-preview",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
        body {
            background-image: url('https://www.sonata-software.com/sites/default/files/inline-images/home-pg/our-culture-desktop.webp'); /* Replace with your image URL */
            background-size: cover;
        }
        .stApp {
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.7);
            padding: 20px;
            border-radius: 10px;
        }
        @keyframes slow-blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }
        .warning-message {
            color: red;
            font-size: 14px;
            margin-top: 10px;
            font-weight: bold;
            text-shadow: 2px 2px 5px black;
        }
        .user-message {
            color: lightblue;
            margin: 5px 0;
        }
        .assistant-response {
            color: lightgreen;
            margin: 5px 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Function to fetch data from PRTG APIs
def fetch_data():
    api_urls = {
        "sensors": "http://172.29.42.140/api/table.json?content=sensors&columns=objid,sensor,status,message,group,type,location&username=prtgusr1&password=N@nd!$004",
        "devices": "http://172.29.42.140/api/table.json?content=devices&columns=objid,device,group,status,type&username=prtgusr1&password=N@nd!$004",
        "groups": "http://172.29.42.140/api/table.json?content=groups&columns=objid,group,status,location&username=prtgusr1&password=N@nd!$004",
        "notifications": "http://172.29.42.140/api/table.json?content=notifications&columns=objid,subject,status&username=prtgusr1&password=N@nd!$004",
        # Add more endpoints as needed
    }
    
    data = {}
    
    for key, url in api_urls.items():
        try:
            response = requests.get(url, verify=False)  # Disable SSL verification
            response.raise_for_status()  # Raise an error for bad responses
            data[key] = response.json()  # Store the JSON response
        except Exception as e:
            st.error(f"Error fetching {key}: {e}")
    
    return data

# Fetch the data at the beginning
data = fetch_data()

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Streamlit UI
st.title("PRTG AI Assistant")
user_input = st.text_input("PRTG API is integrated for live data analysis. How can I assist you with it today?")

if user_input:
    # Prepare the messages for OpenAI API
    messages = [
        {"role": "system", "content": "You are Astra, an advanced AI assistant exclusively available to IT managers at Sonata Software Limited."},
        {"role": "user", "content": user_input}
    ]

    # Add fetched data context into the message
    if data:
        messages.append({"role": "system", "content": f"Here are the recent data points: {data}"})

    try:
        completion = client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=4096,  # Adjust the token limit based on your requirements
            temperature=1.0,
        )
        
        assistant_response = completion.choices[0].message.content
        
        # Store the chat history
        st.session_state.chat_history.append((user_input, assistant_response))

    except Exception as e:
        st.error(f"Error generating response: {e}")

# Display chat history
if st.session_state.chat_history:
    for user_msg, assistant_msg in st.session_state.chat_history:
        st.markdown(f'<div class="user-message">User: {user_msg}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-response">Astra: {assistant_msg}</div>', unsafe_allow_html=True)
