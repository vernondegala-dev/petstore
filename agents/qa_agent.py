import os
import json
import logging
from google import genai
from google.genai import types
from api_client.client import PetstoreClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("QA-Agent")

class QATestingAgent:
    def __init__(self, base_url="https://petstore.swagger.io/v2", model_name="gemini-2.5-flash"):
        self.client = PetstoreClient(base_url=base_url)
        self.model_name = model_name
        
        # Initialize Google GenAI client
        # It automatically looks for GEMINI_API_KEY env var
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY or API_KEY environment variable not set. Agent will require an API key to run.")
            self.ai_client = genai.Client()
        else:
            self.ai_client = genai.Client(api_key=api_key)
            
        # Register tools map for local execution lookup
        self.tools_map = {
            "add_pet": self.tool_add_pet,
            "update_pet": self.tool_update_pet,
            "get_pet_by_id": self.tool_get_pet_by_id,
            "find_pets_by_status": self.tool_find_pets_by_status,
            "delete_pet": self.tool_delete_pet,
            "get_inventory": self.tool_get_inventory,
            "place_order": self.tool_place_order,
            "get_order_by_id": self.tool_get_order_by_id,
            "delete_order": self.tool_delete_order,
            "create_user": self.tool_create_user,
            "get_user_by_name": self.tool_get_user_by_name,
            "update_user": self.tool_update_user,
            "delete_user": self.tool_delete_user,
            "login_user": self.tool_login_user,
            "logout_user": self.tool_logout_user,
            "write_pytest_test": self.tool_write_pytest_test
        }

    # --- Tool Definitions ---

    def tool_add_pet(self, pet_id: int, name: str, status: str = "available", category_id: int = 1, category_name: str = "Dogs") -> str:
        """
        Adds a new pet to the petstore.
        
        Args:
            pet_id: Unique identifier for the pet (e.g., 12345).
            name: The name of the pet (e.g., 'Rex').
            status: Pet status, can be 'available', 'pending', or 'sold'.
            category_id: Optional ID for the category.
            category_name: Optional category name.
        """
        data = {
            "id": pet_id,
            "category": {"id": category_id, "name": category_name},
            "name": name,
            "photoUrls": [],
            "tags": [],
            "status": status
        }
        res = self.client.add_pet(data)
        return self._format_response(res)

    def tool_update_pet(self, pet_id: int, name: str, status: str, category_id: int = 1, category_name: str = "Dogs") -> str:
        """
        Updates an existing pet in the store.
        
        Args:
            pet_id: Unique identifier of the pet to update.
            name: Updated name of the pet.
            status: Updated status of the pet ('available', 'pending', or 'sold').
            category_id: Category ID.
            category_name: Category name.
        """
        data = {
            "id": pet_id,
            "category": {"id": category_id, "name": category_name},
            "name": name,
            "photoUrls": [],
            "tags": [],
            "status": status
        }
        res = self.client.update_pet(data)
        return self._format_response(res)

    def tool_get_pet_by_id(self, pet_id: int) -> str:
        """
        Retrieves details of a pet using its ID.
        
        Args:
            pet_id: ID of the pet to fetch.
        """
        res = self.client.get_pet_by_id(pet_id)
        return self._format_response(res)

    def tool_find_pets_by_status(self, status: str) -> str:
        """
        Finds pets by status.
        
        Args:
            status: Status filter ('available', 'pending', or 'sold').
        """
        res = self.client.find_pets_by_status(status)
        return self._format_response(res)

    def tool_delete_pet(self, pet_id: int) -> str:
        """
        Deletes a pet by ID from the petstore.
        
        Args:
            pet_id: ID of the pet to delete.
        """
        res = self.client.delete_pet(pet_id)
        return self._format_response(res)

    def tool_get_inventory(self) -> str:
        """
        Returns a map of status to number of pets in the store.
        """
        res = self.client.get_inventory()
        return self._format_response(res)

    def tool_place_order(self, order_id: int, pet_id: int, quantity: int = 1, ship_date: str = "", status: str = "placed", complete: bool = False) -> str:
        """
        Places an order for a pet.
        
        Args:
            order_id: Unique order identifier.
            pet_id: ID of the pet being ordered.
            quantity: Quantity of the pet being ordered.
            ship_date: Optional shipping date string (e.g. "2026-06-20T12:00:00.000Z").
            status: Order status ('placed', 'approved', 'delivered').
            complete: Whether the order is complete.
        """
        data = {
            "id": order_id,
            "petId": pet_id,
            "quantity": quantity,
            "status": status,
            "complete": complete
        }
        if ship_date:
            data["shipDate"] = ship_date
        res = self.client.place_order(data)
        return self._format_response(res)

    def tool_get_order_by_id(self, order_id: int) -> str:
        """
        Retrieves a purchase order by ID.
        
        Args:
            order_id: Purchase order ID.
        """
        res = self.client.get_order_by_id(order_id)
        return self._format_response(res)

    def tool_delete_order(self, order_id: int) -> str:
        """
        Deletes a purchase order by ID.
        
        Args:
            order_id: ID of the purchase order to delete.
        """
        res = self.client.delete_order(order_id)
        return self._format_response(res)

    def tool_create_user(self, user_id: int, username: str, first_name: str = "", last_name: str = "", email: str = "", password: str = "", phone: str = "", user_status: int = 0) -> str:
        """
        Creates a user account in the system.
        
        Args:
            user_id: Unique user identifier.
            username: Unique username.
            first_name: First name of the user.
            last_name: Last name of the user.
            email: Email address.
            password: User password.
            phone: Phone number.
            user_status: User status.
        """
        data = {
            "id": user_id,
            "username": username,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "phone": phone,
            "userStatus": user_status
        }
        res = self.client.create_user(data)
        return self._format_response(res)

    def tool_get_user_by_name(self, username: str) -> str:
        """
        Retrieves user information by their username.
        
        Args:
            username: The username to query.
        """
        res = self.client.get_user_by_name(username)
        return self._format_response(res)

    def tool_update_user(self, username: str, user_id: int, updated_username: str, first_name: str = "", last_name: str = "", email: str = "", password: str = "", phone: str = "", user_status: int = 0) -> str:
        """
        Updates an existing user.
        
        Args:
            username: Existing username of the target user.
            user_id: User identifier.
            updated_username: New/updated username.
            first_name: First name.
            last_name: Last name.
            email: Email.
            password: Password.
            phone: Phone number.
            user_status: User status.
        """
        data = {
            "id": user_id,
            "username": updated_username,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "phone": phone,
            "userStatus": user_status
        }
        res = self.client.update_user(username, data)
        return self._format_response(res)

    def tool_delete_user(self, username: str) -> str:
        """
        Deletes a user account.
        
        Args:
            username: Username of the user to delete.
        """
        res = self.client.delete_user(username)
        return self._format_response(res)

    def tool_login_user(self, username: str, password: str) -> str:
        """
        Logs user into the system.
        
        Args:
            username: The user's username.
            password: The user's password.
        """
        res = self.client.login_user(username, password)
        return self._format_response(res)

    def tool_logout_user(self) -> str:
        """
        Logs out current logged in user session.
        """
        res = self.client.logout_user()
        return self._format_response(res)

    def tool_write_pytest_test(self, file_name: str, code_content: str) -> str:
        """
        Writes a standard python pytest test to the tests/ directory to persist the QA verification logic.
        Use this tool when you discover a regression, a bug, or want to establish automated tests.
        
        Args:
            file_name: Name of the pytest file to write (must end in .py and start with test_). E.g. 'test_agent_user.py'.
            code_content: Complete valid python pytest code content.
        """
        if not file_name.startswith("test_") or not file_name.endswith(".py"):
            return "Error: file_name must start with 'test_' and end with '.py'."
        
        try:
            # Prevent overwriting core test files
            core_files = ["test_pet.py", "test_store.py", "test_user.py", "conftest.py"]
            if file_name in core_files:
                return f"Error: Overwriting core test file {file_name} is prohibited. Please use a unique filename like 'test_agent_{file_name}'."
            
            file_path = os.path.join("tests", file_name)
            with open(file_path, "w") as f:
                f.write(code_content)
            logger.info(f"Agent successfully wrote test file: {file_path}")
            return f"Successfully wrote pytest file: {file_path}."
        except Exception as e:
            return f"Error writing file: {str(e)}"

    # --- Helper methods ---

    def _format_response(self, response) -> str:
        """Formats standard HTTP response metadata into an agent-friendly string summary."""
        try:
            body = response.json()
        except Exception:
            body = response.text
            
        res_dict = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body
        }
        return json.dumps(res_dict, indent=2)

    # --- Core Execution Loop ---

    def run(self, objective: str):
        """
        Runs the main ReAct loop for the QA Testing Agent with the given high-level QA objective.
        """
        system_instruction = (
            "You are an expert Autonomous QA Automation Testing Agent. "
            "Your goal is to thoroughly validate the Swagger Petstore API endpoints given a test objective. "
            "You are equipped with tools to interact with the actual live Petstore API and to persist "
            "discovered regression tests inside the `tests/` directory.\n\n"
            "CRITICAL PROTOCOLS:\n"
            "1. Run tests step-by-step. Analyze API status codes, response times, and payloads.\n"
            "2. Ensure you check both happy path and edge cases.\n"
            "3. If you find a bug, try to reproduce it, then write a pytest file (using `write_pytest_test`) "
            "so that automated systems can catch regressions in the future. "
            "Your generated test should use the `api_client` fixture and follow standard pytest naming/conventions.\n"
            "4. Maintain proper state. For example, if you add a pet, clean up by deleting it at the end of the run.\n"
            "5. Provide a thorough, structured markdown report of your findings at the very end including status codes, body payloads, and any issues."
        )

        # Assemble the tools list
        tools_list = list(self.tools_map.values())

        logger.info(f"Starting agent run. Objective: '{objective}'")
        
        chat = self.ai_client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=tools_list,
                temperature=0.1
            )
        )

        response = chat.send_message(objective)
        
        # Loop to process tool calls until LLM provides a final text response
        max_turns = 15
        turn = 0
        while response.function_calls and turn < max_turns:
            turn += 1
            for call in response.function_calls:
                tool_name = call.name
                args = call.args
                logger.info(f"Turn {turn} - AI requests tool execution: '{tool_name}' with args {args}")
                
                # Retrieve the actual method mapped to this tool
                tool_fn = self.tools_map.get(tool_name)
                if not tool_fn:
                    logger.error(f"Tool {tool_name} not found in registered tools map.")
                    result = f"Error: Tool {tool_name} is not registered."
                else:
                    try:
                        # Call the tool function with unpacked parameters
                        result = tool_fn(**args)
                    except Exception as e:
                        logger.error(f"Exception executing tool {tool_name}: {str(e)}")
                        result = f"Exception executing tool: {str(e)}"
                
                logger.debug(f"Tool execution response: {result[:200]}...")
                
                # Send the function response back to Gemini
                response = chat.send_message(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": result}
                    )
                )

        logger.info("Agent run finished.")
        return response.text
