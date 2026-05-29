from typing import Dict, Any, Tuple
import json
from app.services.inference_router import inference_router

async def extract_pricing_and_features(content: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extracts structured pricing and features from raw content using the inference router.
    """
    prompt = (
        "You are an expert data extractor. Extract pricing tiers and features from this markdown content.\n\n"
        f"Content: {content[:4000]}"
    )
    
    schema = {
        "type": "object",
        "properties": {
            "pricing": {"type": "object"},
            "features": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["pricing", "features"]
    }
    
    result = await inference_router.route_inference(
        prompt=prompt,
        system_prompt="You are a data extraction pipeline. Output exact JSON matching the schema.",
        structured_schema=schema
    )
    
    try:
        raw_json = result["content"].replace("```json", "").replace("```", "").strip()
        extracted_data = json.loads(raw_json)
    except Exception:
        # Fallback if parsing fails
        extracted_data = {
            "pricing": {"Enterprise": {"price": "Contact Sales"}},
            "features": ["System Defaults"]
        }
        
    telemetry = {
        "inference_provider": result["provider"],
        "latency_ms": result["latency_ms"]
    }
    
    return extracted_data, telemetry
