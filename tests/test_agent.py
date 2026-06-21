import os
import json
import pytest
from unittest.mock import MagicMock, patch, mock_open
from agents.qa_agent import QATestingAgent

@pytest.fixture
def mock_agent():
    # Patch the genai.Client so it doesn't try to authenticate with Google's servers during test runs.
    with patch("agents.qa_agent.genai.Client") as mock_genai_client:
        agent = QATestingAgent()
        # Mock the underlying PetstoreClient methods
        agent.client = MagicMock()
        yield agent

def test_format_response_json(mock_agent):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": 123, "name": "Buddy"}
    
    formatted = mock_agent._format_response(mock_response)
    data = json.loads(formatted)
    
    assert data["status_code"] == 200
    assert data["headers"] == {"Content-Type": "application/json"}
    assert data["body"] == {"id": 123, "name": "Buddy"}

def test_format_response_text(mock_agent):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.json.side_effect = Exception("Not JSON")
    mock_response.text = "Pet not found"
    
    formatted = mock_agent._format_response(mock_response)
    data = json.loads(formatted)
    
    assert data["status_code"] == 404
    assert data["body"] == "Pet not found"

def test_tool_add_pet(mock_agent):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 123, "name": "Rex", "status": "available"}
    mock_agent.client.add_pet.return_value = mock_response
    
    res = mock_agent.tool_add_pet(pet_id=123, name="Rex", status="available")
    
    # Verify the underlying client was called correctly
    mock_agent.client.add_pet.assert_called_once_with({
        "id": 123,
        "category": {"id": 1, "name": "Dogs"},
        "name": "Rex",
        "photoUrls": [],
        "tags": [],
        "status": "available"
    })
    
    assert "Rex" in res
    assert '"status_code": 200' in res

def test_tool_delete_pet(mock_agent):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"code": 200, "message": "123"}
    mock_agent.client.delete_pet.return_value = mock_response
    
    res = mock_agent.tool_delete_pet(pet_id=123)
    
    mock_agent.client.delete_pet.assert_called_once_with(123)
    assert "123" in res

def test_tool_write_pytest_test_safety(mock_agent):
    # Test that writing to a core file is blocked
    res = mock_agent.tool_write_pytest_test("test_pet.py", "def test_fail(): assert False")
    assert "Error: Overwriting core test file" in res
    
    # Test invalid file naming
    res2 = mock_agent.tool_write_pytest_test("not_a_test_file.txt", "some content")
    assert "Error: file_name must start with 'test_' and end with '.py'." in res2

def test_tool_write_pytest_test_success(mock_agent):
    test_file_name = "test_agent_temp_run.py"
    dummy_code = "def test_dummy(): pass"
    
    m = mock_open()
    with patch("builtins.open", m):
        res = mock_agent.tool_write_pytest_test(test_file_name, dummy_code)
        
        assert "Successfully wrote pytest file" in res
        m.assert_called_once_with(os.path.join("tests", test_file_name), "w")
        m().write.assert_called_once_with(dummy_code)

def test_agent_run_loop(mock_agent):
    # Mocking Gemini Chat flow response
    mock_chat = MagicMock()
    mock_agent.ai_client.chats.create.return_value = mock_chat
    
    # Set up consecutive response mocks to simulate ReAct loop
    # Turn 1: AI decides to call 'get_pet_by_id'
    mock_call = MagicMock()
    mock_call.name = "get_pet_by_id"
    mock_call.args = {"pet_id": 999}
    
    response_1 = MagicMock()
    response_1.function_calls = [mock_call]
    
    # Turn 2: AI outputs the final report
    response_2 = MagicMock()
    response_2.function_calls = []
    response_2.text = "All tests successfully executed. The pet with ID 999 does not exist (received 404 as expected)."
    
    mock_chat.send_message.side_effect = [response_1, response_2]
    
    # Mock tool response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.side_effect = Exception()
    mock_response.text = "Not Found"
    mock_agent.client.get_pet_by_id.return_value = mock_response
    
    report = mock_agent.run("Verify pet 999 returns 404")
    
    # Check assertions
    mock_agent.ai_client.chats.create.assert_called_once()
    assert mock_agent.client.get_pet_by_id.called
    assert "All tests successfully executed" in report
