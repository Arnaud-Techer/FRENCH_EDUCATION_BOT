import streamlit as st 
from agent import agent,generate_fiches_storage,generate_bo_storage

# Button to generate data storage
if st.button("Generate the data storage"):
    st.write("Generating the data storage...")
    generate_fiches_storage()
    st.write("Data storage generated successfully!")

# Button to generate BO storage
if st.button("Generate the BO storage"):
    st.write("Generating the BO storage...")
    generate_bo_storage()
    st.write("BO storage generated successfully!")
    
st.title("French Education System Bot")
prompt = st.text_input("Enter a question / request about the education system : ")

if st.button("Get the answer"):
    st.write("Processing the request...")
    result = agent.query(prompt)
    st.write(result)
    
