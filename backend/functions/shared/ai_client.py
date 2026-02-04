"""
Azure AI Foundry client for generating workout recommendations.

Uses AIProjectClient with DefaultAzureCredential per MS Learn docs:
https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/sdk-overview
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

# Default AI Foundry configuration
DEFAULT_AI_ENDPOINT = "https://fit-app-resource.services.ai.azure.com/api/projects/fit-app"
DEFAULT_MODEL = "gpt-5-mini"


class AIClientError(Exception):
    """Exception raised when AI agent communication fails."""
    pass


# System prompt for the AI coach
COACH_SYSTEM_PROMPT = """You are an expert half-marathon running coach. Based on the user's recent training context, recommend today's workout.

Guidelines:
1. The half marathon is May 2nd with a goal of no walking.
2. Polarized Training: Mix easy runs, threshold work, and recovery
3. No running on consecutive days
4. Weekly long run: Recommend at least one longer endurance run per week
5. Recovery: After hard sessions or long runs, prioritize easy/rest days
6. Progression: Gradual volume increase (10% rule)
7. Build a solid cardio base is IMPORTANT in regards to maintaining a steady acceptable heart rate.
8. Activities should be chosen from running, rowing, and rucking.
9. When providing a workout routine provide an alternate.
10. Be sure to check notes in regards to any context.
11. Assume all runs are done on a treadmill unless the notes say otherwise
You MUST respond with valid JSON matching this exact schema:
{
  "title": "string (max 100 chars) - short workout title",
  "workout": {
    "type": "Running" | "Cross-training" | "Rest",
    "durationMinutes": number (0-240),
    "details": ["string array of 1-10 workout steps"]
  },
  "rationale": "string (max 500 chars) - brief explanation referencing recent training",
  "confidence": "low" | "medium" | "high"
}

Do NOT include any text outside the JSON object."""


class AIClient:
    """
    Client for Azure AI Foundry using AIProjectClient.
    
    Uses DefaultAzureCredential for authentication (works with Azure CLI locally,
    managed identity in Azure).
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        credential: Optional[Any] = None
    ):
        """
        Initialize AI Foundry client.
        
        Args:
            endpoint: AI Foundry project endpoint URL.
            model: Model deployment name.
            credential: Azure credential for auth. Defaults to DefaultAzureCredential.
        """
        self.endpoint = endpoint or os.environ.get("AI_FOUNDRY_ENDPOINT", DEFAULT_AI_ENDPOINT)
        self.model = model or os.environ.get("AI_FOUNDRY_MODEL", DEFAULT_MODEL)
        self.credential = credential or DefaultAzureCredential()
        self._project_client = None
        self._openai_client = None
    
    def _get_client(self):
        """
        Get OpenAI client via AIProjectClient.
        
        Per MS Learn docs, AIProjectClient handles authentication properly
        and provides an OpenAI-compatible client.
        """
        if self._openai_client is None:
            try:
                from azure.ai.projects import AIProjectClient
                
                logger.info(f"Initializing AIProjectClient with endpoint: {self.endpoint}")
                
                self._project_client = AIProjectClient(
                    endpoint=self.endpoint,
                    credential=self.credential
                )
                
                # Get OpenAI client from project - this handles auth correctly
                self._openai_client = self._project_client.get_openai_client(
                    api_version="2024-10-21"
                )
                
                logger.info("OpenAI client initialized via AIProjectClient")
                
            except ImportError as e:
                logger.error(f"azure-ai-projects package not installed: {e}")
                raise AIClientError("azure-ai-projects package not installed")
            except Exception as e:
                logger.error(f"Failed to initialize AI client: {e}")
                raise AIClientError(f"Failed to initialize AI client: {e}")
        
        return self._openai_client
    
    def generate_recommendation(self, training_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a workout recommendation based on training context.
        
        Args:
            training_context: Dictionary with training summary data
            
        Returns:
            Dictionary with recommendation fields (title, workout, rationale, confidence)
            
        Raises:
            AIClientError: If AI agent call fails
        """
        try:
            client = self._get_client()
            
            # Format training context as user message
            user_prompt = f"""Based on my recent training context, recommend today's workout:

Training Window: {training_context.get('start_date')} to {training_context.get('end_date')}
Total Activities: {training_context.get('total_activities', 0)}
Total Distance: {training_context.get('total_distance_miles', 0):.1f} miles
Total Duration: {training_context.get('total_duration_minutes', 0)} minutes
Last Hard Workout: {training_context.get('last_hard_workout', 'None')}
Last Long Run: {training_context.get('last_long_run', 'None')}
Rest Days: {training_context.get('rest_days_count', 0)}
Activity Types: {', '.join(training_context.get('activity_types', []))}

Today's date: {training_context.get('end_date')}

Respond with JSON only."""
            
            logger.info(f"Calling AI with model: {self.model}")
            
            # Use OpenAI chat completions API
            # Note: newer models use max_completion_tokens instead of max_tokens
            # GPT-5 mini uses reasoning tokens internally, so we need a larger budget
            # to ensure there are tokens remaining for the actual output content
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": COACH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_completion_tokens=2000
            )
            
            # Extract and parse JSON response
            content = response.choices[0].message.content.strip()
            logger.debug(f"AI response: {content[:200]}...")
            
            # Handle potential markdown code blocks
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            recommendation = json.loads(content)
            
            # Validate required fields
            required_fields = ["title", "workout", "rationale", "confidence"]
            for field in required_fields:
                if field not in recommendation:
                    raise AIClientError(f"AI response missing required field: {field}")
            
            logger.info(f"Generated recommendation: {recommendation.get('title')}")
            return recommendation
            
        except json.JSONDecodeError as e:
            logger.error(f"AI response not valid JSON: {e}")
            raise AIClientError(f"AI response not valid JSON: {e}")
        except Exception as e:
            logger.error(f"AI client error: {e}")
            raise AIClientError(f"AI client error: {e}")
    
    def close(self):
        """Close the client connections."""
        self._openai_client = None
        if self._project_client is not None:
            self._project_client.close()
            self._project_client = None


def get_ai_client() -> AIClient:
    """
    Factory function to create an AI client instance.
    
    Returns:
        Configured AIClient instance
    """
    return AIClient()
