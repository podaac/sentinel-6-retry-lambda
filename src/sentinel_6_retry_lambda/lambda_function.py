import logging
from typing import Any, Dict, List, Set

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def filter_failed_granules(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filters payload.granules to include only items that have a matching 
    package_name in the 'fail' list.
    
    Args:
        data: The input event dictionary containing 'fail' and 'payload'.
        
    Returns:
        A dictionary containing the reconstructed payload.
    """
    # Use a set for O(1) lookups
    failed_package_names: Set[str] = {
        item.get("package_name") for item in data.get("fail", []) if "package_name" in item
    }

    original_granules: List[Dict[str, Any]] = data.get("payload", {}).get("granules", [])
    
    # List comprehension for cleaner filtering
    filtered_granules = [
        granule for granule in original_granules
        if any(f.get("name") in failed_package_names for f in granule.get("files", []))
    ]

    new_payload = data.get("payload", {}).copy()
    new_payload["granules"] = filtered_granules

    return {"payload": new_payload}

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point. Rebuilds the payload based on failures.
    """
    logger.info("Received event: %s", event)

    try:
        result = filter_failed_granules(event)
        event["payload"] = result["payload"]
        
        logger.info("Filtered granules count: %d", len(event["payload"]["granules"]))
        return {"replace": event}
        
    except Exception as e:
        logger.error("Error processing event: %s", str(e), exc_info=True)
        raise