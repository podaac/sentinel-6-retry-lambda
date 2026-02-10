import pytest
from src.sentinel_6_retry_lambda.lambda_function import filter_failed_granules

def test_filter_failed_granules_success():
    mock_event = {
        "fail": [{"package_name": "target_file.zip"}],
        "payload": {
            "granules": [
                {"files": [{"name": "target_file.zip"}], "id": "match"},
                {"files": [{"name": "other_file.zip"}], "id": "no-match"}
            ]
        }
    }
    
    result = filter_failed_granules(mock_event)
    granules = result["payload"]["granules"]
    
    assert len(granules) == 1
    assert granules[0]["id"] == "match"

def test_filter_failed_granules_empty():
    mock_event = {"fail": [], "payload": {"granules": []}}
    result = filter_failed_granules(mock_event)
    assert result["payload"]["granules"] == []