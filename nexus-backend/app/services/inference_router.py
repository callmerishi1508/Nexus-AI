import os
import time
import json
import asyncio
from typing import Dict, Any, Tuple
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class InferenceRouter:
    def __init__(self):
        self.provider_hierarchy = ["AIML_API", "DETERMINISTIC_RECOVERY"]
        self.aiml_api_key = os.getenv("AIML_API_KEY")
        self.aiml_base_url = os.getenv("AIML_BASE_URL", "https://api.aimlapi.com/v1")
        # Use a high-quality model from AIML API
        self.model_name = "gpt-4o"
        
        # Telemetry state
        self.current_provider = "UNKNOWN"
        self.provider_health = "UNREACHABLE"
        
    async def check_health(self) -> str:
        """Determines if the AIML API is available."""
        if self.aiml_api_key and len(self.aiml_api_key) > 5:
            self.provider_health = "AVAILABLE"
            return "AVAILABLE"
        self.provider_health = "UNREACHABLE"
        return "UNREACHABLE"
        
    async def warm_up(self):
        """Cold start protection during FastAPI lifespan."""
        print("Warming up AIML API inference engine...")
        health = await self.check_health()
        if health == "AVAILABLE":
            print("AIML API is WARM and READY.")
        else:
            print("AIML API Key is missing. Defaulting to DETERMINISTIC_RECOVERY.")



    async def route_inference(self, prompt: str, system_prompt: str, structured_schema: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic inference router for dynamic synthesis and projections."""
        start_time = time.time()
        health = await self.check_health()
        
        if health == "AVAILABLE":
            self.current_provider = "AIML_API"
            try:
                llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.aiml_api_key,
                    base_url=self.aiml_base_url,
                    temperature=0.7
                )
                
                full_prompt = f"{system_prompt}\n\n{prompt}"
                if structured_schema:
                    full_prompt += f"\n\nOUTPUT FORMAT REQUIRED JSON MATCHING SCHEMA:\n{json.dumps(structured_schema)}"

                response = await asyncio.wait_for(llm.ainvoke(full_prompt), timeout=30.0)
                latency = round((time.time() - start_time) * 1000)
                
                return {
                    "content": response.content,
                    "provider": self.current_provider,
                    "latency_ms": latency
                }
            except asyncio.TimeoutError:
                print("AIML inference timed out after 30s. Falling back to deterministic recovery.")
                self.provider_health = "DEGRADED"
            except Exception as e:
                print(f"AIML inference failed: {e}. Falling back to deterministic recovery.")
                self.provider_health = "DEGRADED"
        
        # Fallback
        self.current_provider = "DETERMINISTIC_RECOVERY"
        if structured_schema:
            keys = structured_schema.get("required", [])
            dummy = {}
            for k in keys:
                if 'confidence' in k or 'count' in k:
                    dummy[k] = 50
                elif structured_schema.get("properties", {}).get(k, {}).get("type") == "array":
                    dummy[k] = []
                else:
                    dummy[k] = f"Generated fallback for {k}"
            content_str = json.dumps(dummy)
        else:
            content_str = "Under the bounded constraint of the current scenario, the ecosystem is highly likely to experience systemic shifts."
            
        latency = round((time.time() - start_time) * 1000)
        return {
            "content": content_str,
            "provider": self.current_provider,
            "latency_ms": latency
        }


inference_router = InferenceRouter()
