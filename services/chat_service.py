import logging
import json
from services.openai_services import generate_chatgpt_response
from services.advising_service import AdvisingService
from services.degree_audit_service import DegreeAuditService


logger = logging.getLogger(__name__)








class ChatService:
    """Handles interactive conversations with the GPT API."""

    def __init__(self, conversation_id=None, conversation_history=None, context=None):
        """
        Initialize the ChatService with optional conversation ID, history, and context.

        Args:
            conversation_id (str): Unique identifier for the conversation.
            conversation_history (list): List of previous messages in the conversation.
            context (dict): Shared context for storing degree audit or advising results.
        """
        self.conversation_id = conversation_id or "default_conversation"
        self.conversation_history = conversation_history if conversation_history is not None else []
        self.context = context if context is not None else {}
        logger.info(f"ChatService initialized with conversation_id: {self.conversation_id}")

    def handle_action(self, action, major_name, file_paths):
        """
        Handle specific actions like degree audit or advising.

        Args:
            action (str): The action to perform (e.g., "degree_audit", "advising").
            major_name (str): The user's major.
            file_paths (list): List of file paths for processing.

        Returns:
            dict: The assistant's structured response.
        """
        try:
            if action.lower() == "degree_audit":
                degree_audit_service = DegreeAuditService(major_name=major_name, file_paths=file_paths)
                result = degree_audit_service.perform_audit()

                if result.get("status") == "success":
                    self.context["degree_audit"] = result["audit_info"]
                    audit_summary = f"Degree audit results for {major_name}: {json.dumps(result['audit_info'], indent=2)}"
                    self._append_to_history("assistant", audit_summary)
                    return {"status": "success", "response": audit_summary, "history": self.conversation_history}
                else:
                    error_message = result.get("message", "Error performing degree audit.")
                    self._append_to_history("assistant", error_message)
                    return {"status": "error", "response": error_message, "history": self.conversation_history}

            elif action.lower() == "advising":
                advising_service = AdvisingService(major_name=major_name, file_paths=file_paths)
                result = advising_service.process_advising_request()

                if result.get("status") == "success":
                    self.context["advising"] = result["advising_notes"]
                    advising_summary = f"Advising results for {major_name}: {json.dumps(result['advising_notes'], indent=2)}"
                    self._append_to_history("assistant", advising_summary)
                    return {"status": "success", "response": advising_summary, "history": self.conversation_history}
                else:
                    error_message = result.get("message", "Error performing academic advising.")
                    self._append_to_history("assistant", error_message)
                    return {"status": "error", "response": error_message, "history": self.conversation_history}

            error_message = "Unsupported action provided. Valid actions: 'degree_audit', 'advising'."
            self._append_to_history("assistant", error_message)
            return {"status": "error", "response": error_message, "history": self.conversation_history}

        except Exception as e:
            logger.error(f"Error during handling action: {e}", exc_info=True)
            error_message = "An error occurred while processing your request. Please try again later."
            self._append_to_history("assistant", error_message)
            return {"status": "error", "response": error_message, "history": self.conversation_history}

    def continue_conversation(self, user_message):
        """
        Continue the conversation with the GPT API.

        Args:
            user_message (str): The user's input to the assistant.

        Returns:
            dict: The GPT response and updated conversation history.
        """
        try:
            self._append_to_history("user", user_message)
            logger.debug(f"Updated conversation history: {self.conversation_history}")

            system_prompt = self._build_system_prompt()

            gpt_response = generate_chatgpt_response(
                prompt=None,  
                conversation_history=self.conversation_history,
                system_prompt=system_prompt,
                max_tokens=3000,
                temperature=0.7
            )

            if isinstance(gpt_response, dict) and gpt_response.get("status") == "error":
                error_message = gpt_response.get("message", "Error connecting to GPT API.")
                self._append_to_history("assistant", error_message)
                return {"status": "error", "response": error_message, "history": self.conversation_history}

            if gpt_response and hasattr(gpt_response, "choices") and gpt_response.choices:
                assistant_reply = gpt_response.choices[0].message.content.strip()

                self._append_to_history("assistant", assistant_reply)
                return {"status": "success", "response": assistant_reply, "history": self.conversation_history}

            logger.error("GPT API response was invalid or empty.")
            error_message = "Error connecting to GPT API."
            self._append_to_history("assistant", error_message)
            return {"status": "error", "response": error_message, "history": self.conversation_history}

        except Exception as e:
            logger.error(f"Error during GPT API interaction: {e}", exc_info=True)
            error_message = "An error occurred while communicating with GPT API. Please try again later."
            self._append_to_history("assistant", error_message)
            return {"status": "error", "response": error_message, "history": self.conversation_history}

    def reset_conversation(self):
        """Reset the conversation history and context."""
        self.conversation_history = []
        self.context = {}
        logger.info("Conversation history and context reset.")

    def _append_to_history(self, role, content):
        """Helper to append a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def _build_system_prompt(self):
        """
        Build the system prompt based on the current context.

        Returns:
            str: The system prompt string or None if no context is present.
        """
        if not self.context:
            return None

        context_items = []
        if "degree_audit" in self.context:
            degree_audit_info = json.dumps(self.context["degree_audit"], indent=2)
            context_items.append(f"Degree Audit Information:\n{degree_audit_info}")

        if "advising" in self.context:
            advising_notes = json.dumps(self.context["advising"], indent=2)
            context_items.append(f"Advising Notes:\n{advising_notes}")

        system_prompt = "\n\n".join(context_items)
        logger.debug(f"Constructed system prompt: {system_prompt}")
        return system_prompt if system_prompt else None
