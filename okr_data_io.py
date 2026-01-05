import json
from pathlib import Path
from typing import Dict, List

def load_okr_from_json(file_path: str) -> Dict:
    """
    Load OKR data from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing OKR data
        
    Returns:
        Dictionary containing OKR data with 'objective' and 'key_results'
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            okr_data = json.load(file)
            
        # Validate basic structure
        if "objective" not in okr_data:
            raise ValueError("OKR data must contain 'objective' field")
        if "key_results" not in okr_data:
            raise ValueError("OKR data must contain 'key_results' field")
            
        print(f"✓ Successfully loaded OKR: '{okr_data['objective']}'")
        print(f"✓ Number of Key Results: {len(okr_data['key_results'])}")
        
        return okr_data
        
    except FileNotFoundError:
        print(f"✗ Error: File '{file_path}' not found")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Error: Invalid JSON format - {e}")
        raise
    except Exception as e:
        print(f"✗ Error: {e}")
        raise


def load_multiple_okrs(file_path: str) -> List[Dict]:
    """
    Load multiple OKRs from a JSON file (expects array of OKR objects).
    
    Args:
        file_path: Path to the JSON file containing array of OKRs
        
    Returns:
        List of OKR dictionaries
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            okrs_data = json.load(file)
            
        if not isinstance(okrs_data, list):
            raise ValueError("File must contain an array of OKR objects")
            
        print(f"✓ Successfully loaded {len(okrs_data)} OKR(s)")
        
        return okrs_data
        
    except Exception as e:
        print(f"✗ Error loading OKRs: {e}")
        raise


def save_okr_to_json(okr_data: Dict, file_path: str):
    """
    Save OKR data to a JSON file.
    
    Args:
        okr_data: Dictionary containing OKR data
        file_path: Path where the JSON file will be saved
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(okr_data, file, indent=4, ensure_ascii=False)
            
        print(f"✓ Successfully saved OKR to '{file_path}'")
        
    except Exception as e:
        print(f"✗ Error saving OKR: {e}")
        raise