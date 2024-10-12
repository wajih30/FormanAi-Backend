import logging
import sys
print(sys.path)  # This will print the directories Python is searching for modules



from utils.prompt_builder import PromptHandler  # Import the class

import logging
import openai
import os

# Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.FileHandler('chat_service.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ChatService:
    """Handles all manual query-based interactions for academic advising."""

    def __init__(self, major_name):
        """Initialize the service for the given major."""
        logger.info(f"Initializing ChatService for major: {major_name}")
        self.major_name = major_name
        self.prompt_handler = PromptHandler()  # Instantiate PromptHandler

    def handle_query(self, parsed_data):
        """
        Handle the user query and build a prompt for OpenAI based on the parsed data.

        Args:
        - parsed_data (dict): The user's query in structured form.

        Returns:
        - str: OpenAI's response to the user query.
        """
        logger.info(f"Handling user query: {parsed_data}")
        try:
            # Call the build_manual_query_prompt method from the PromptHandler instance
            prompt = self.prompt_handler.build_manual_query_prompt(parsed_data)

            # Send the prompt to OpenAI and get the response
            return self._generate_openai_response(prompt)
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            return f"An error occurred: {str(e)}"

    def _generate_openai_response(self, prompt):
        """Generate a response using OpenAI for the given prompt."""
        try:
            logger.info("Generating OpenAI response for manual query.")
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an academic advisor bot specialized in handling academic queries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return f"An error occurred while generating a response: {str(e)}"

def test_chat_service():
    print("Chat Service is working!")

# Add this block to test the file independently
if __name__ == '__main__':
    print("Chat service script is running")
    test_chat_service()
