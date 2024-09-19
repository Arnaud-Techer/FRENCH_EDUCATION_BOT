import streamlit as st 
from agent import agent
st.title("French Education System Bot")
prompt = st.text_input("Enter a question / request about the education system : ")

if st.button("Get the answer"):
    st.write("Processing the request...")
    result = agent.query(prompt)
    st.write(result)
    