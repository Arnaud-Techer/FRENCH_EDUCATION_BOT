from llama_index.core.tools import FunctionTool
import os 

# file name in which the answer can be written for the user
register_prompt_file_name = "notes.txt"

def register(prompt:str) -> str :
    """Create a notes.txt file and write the prompt in it.

    Args:
        prompt (str): prompt that will be written in the file for the user

    Returns:
        str: return a message to be sure that the file is well written.
    """
    if not os.path.exists(register_prompt_file_name):
        open(register_prompt_file_name,'w')
    with open(register_prompt_file_name,"a") as f:
        f.writelines([prompt + "\n"])
    return "register prompt file saved."

# create the engine to be query if the user want to write an answer in a notes.txt file.
register_prompt_engine = FunctionTool.from_defaults(
    fn=register,
    name="registering_prompt",
    description="this tool can save the answer / prompt of the AI Agent in a text file for the user. "
)