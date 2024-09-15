from openai import OpenAI
from dotenv import load_dotenv
import pathlib
from pprint import pprint
import json

load_dotenv()

client = OpenAI()

class Parser:

    current_file_id = None
    current_thread_id = None

    def __init__(self):

        try:
            self.parser = self.retrieve_parser()
        except:
            self.parser = self.create_parser()
            try:
                parseInfo_path = pathlib.Path(__file__).parent/f"data/parserInfo.txt"
                with open(parseInfo_path, "w") as file:
                    file.write(self.parser.id)
            except:
                raise ValueError
        

    def retrieve_parser(self):

        parseInfo_path = pathlib.Path(__file__).parent/f"data/parserInfo.txt"
        with open(parseInfo_path, "r") as file:
            data = file.readlines()

        if len(data) == 0:
            raise ValueError("No Id Stored")
        else:
            return client.beta.assistants.retrieve(
                assistant_id=data[0]
            )


    def create_parser(self):
        
        parserInstruct_path = pathlib.Path(__file__).parent/f"data/parserInstructions.txt"
        with open(parserInstruct_path, 'r') as inst:
            data = inst.read()

        return client.beta.assistants.create(
            name="Assignment Parser",
            instructions=data,
            model="gpt-4o",
            tools=[{"type": "file_search"}]
            # response_format={ "type": "json_object" }
        )


    def create_message(self, file_path, extra_instructions):

        
        message_file = client.files.create(
            file=open(file_path, "rb"), purpose="assistants"
        )
        
        self.current_file_id = message_file.id

        thread = client.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": f"List all the assignments/tasks/projects/exams/labs or any tasks that has deadlines along with it's deadlines. {extra_instructions}",
                "attachments": [
                    { "file_id": message_file.id, "tools": [{"type": "file_search"}] }
                ],
                }
            ]
        )

        self.current_thread_id = thread.id

    def get_parsed_data(self):

        run = client.beta.threads.runs.create_and_poll(
            thread_id=self.current_thread_id, assistant_id=self.parser.id
        )

        messages = list(client.beta.threads.messages.list(thread_id=self.current_thread_id, run_id=run.id))

        client.files.delete(
            file_id = self.current_file_id
        )


        return (messages[0].content[0].text.value).strip()

    
def final_parse(partial_parse):

    finalParse_path = pathlib.Path(__file__).parent/f"data/finalParse.txt"
    with open(finalParse_path, 'r') as f:
        prompt = f.read()

    fPrompt = prompt + partial_parse

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":'user', "content":fPrompt}],
        response_format={ "type": "json_object" }
    )

    return (response.choices[0].message.content).strip('\n')

if __name__ == "__main__":

    ...