import json
import logging
from datetime import datetime
from typing import Dict, List, Any

def optimize_scraped_data(raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Optimizes and structures the scraped program data.
    Args:
        raw_data: List of dictionaries containing scraped data
    Returns:
        Dict containing structured program data
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if not raw_data:
        logger.warning("Empty raw data received")
        return create_empty_structure()

    optimized_data = {
        "masters_programs": [],
        "metadata": {
            "total_programs": 0,
            "last_updated": datetime.now().isoformat(),
            "university": "LMU Munich"
        }
    }
    
    for item in raw_data:
        try:
            # Safe get title and description with fallbacks
            title = item.get("title", "") or ""
            description = item.get("description", "") or ""

            # Only process if we have valid title or description
            if "master" in title.lower() or "master" in description.lower():
                program = {
                    "name": title.strip(),
                    "url": item.get("url", ""),
                    "details": {
                        "description": description.strip(),
                        "language": detect_language(description),
                        "duration": extract_duration(description),
                        "location": "Munich, Germany",
                        "degree": extract_degree(title),
                    },
                    "requirements": extract_requirements(description)
                }
                optimized_data["masters_programs"].append(program)
        except Exception as e:
            logger.error(f"Error processing item: {str(e)}")
            continue

    optimized_data["metadata"]["total_programs"] = len(optimized_data["masters_programs"])
    return optimized_data

def create_empty_structure() -> Dict[str, Any]:
    """Creates empty data structure when no valid data is found"""
    return {
        "masters_programs": [],
        "metadata": {
            "total_programs": 0,
            "last_updated": datetime.now().isoformat(),
            "university": "LMU Munich"
        }
    }

def detect_language(text):
    """
    Detects if program is taught in English or German.
    """
    text = text.lower()
    if "taught in english" in text or "english-taught" in text:
        return "English"
    elif "deutsch" in text or "german" in text:
        return "German"
    return "Not specified"

def extract_duration(text):
    """
    Extracts program duration if mentioned.
    """
    if "two years" in text.lower() or "4 semester" in text.lower():
        return "2 years"
    elif "one year" in text.lower() or "2 semester" in text.lower():
        return "1 year"
    return "Not specified"

def extract_degree(title):
    """
    Extracts the degree type.
    """
    if "M.Sc" in title or "Master of Science" in title:
        return "M.Sc."
    elif "M.A" in title or "Master of Arts" in title:
        return "M.A."
    return "Master's Degree"

def extract_requirements(text):
    """
    Extracts key requirements if mentioned.
    """
    requirements = []
    if "bachelor" in text.lower():
        requirements.append("Bachelor's degree")
    if "english" in text.lower() and "b2" in text.lower():
        requirements.append("English B2 level")
    if "german" in text.lower() and "dsh" in text.lower():
        requirements.append("German language skills")
    return requirements if requirements else ["Not specified"]

# Main script
if __name__ == "__main__":
    # Load raw data from `output.json`
    input_file = "output.json"
    output_file = "optimized_output.json"

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        
        # Optimize the data
        optimized_data = optimize_scraped_data(raw_data)
        
        # Save the optimized data
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(optimized_data, f, indent=2, ensure_ascii=False)
        
        print(f"Optimized data saved to {output_file}")
    except Exception as e:
        print(f"Error processing data: {e}")
