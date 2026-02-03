"""
Azure Function endpoint for AI coach daily recommendations.

GET /api/coach/today - Returns today's half marathon training recommendation.
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import date, timedelta
from typing import Optional

import azure.functions as func

from shared.ai_client import AIClient, AIClientError, get_ai_client
from shared.mcp_client import MCPClient, MCPClientError, get_mcp_client
from shared.models import DailyRecommendation, WorkoutDetails, get_fallback_recommendation
from shared.training_context import build_training_context

# Configuration from environment variables
AI_FOUNDRY_ENDPOINT = os.environ.get(
    "AI_FOUNDRY_ENDPOINT",
    "https://fit-app-resource.services.ai.azure.com/api/projects/fit-app"
)
AI_FOUNDRY_MODEL = os.environ.get("AI_FOUNDRY_MODEL", "gpt-5-mini")
MCP_SERVER_ENDPOINT = os.environ.get(
    "MCP_SERVER_ENDPOINT",
    "https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp"
)

# Timeout budget (3 seconds total)
TOTAL_TIMEOUT_SECONDS = 3.0
MCP_TIMEOUT_SECONDS = 1.5
AI_TIMEOUT_SECONDS = 1.5

# Training context window
TRAINING_WINDOW_DAYS = 14

# Application Insights custom metrics logger
logger = logging.getLogger(__name__)


def _track_metric(name: str, value: float, properties: dict = None):
    """
    Track a custom metric for Application Insights.
    
    In production with Application Insights, this appears as a custom metric.
    The Azure Functions runtime auto-instruments these for App Insights.
    """
    extra = {"custom_dimensions": properties or {}}
    logger.info(
        f"Metric: {name}={value}",
        extra={**extra, "metric_name": name, "metric_value": value}
    )


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET /api/coach/today
    
    Returns today's AI-generated half marathon training recommendation.
    Always returns 200 with either an AI recommendation or a fallback.
    """
    start_time = time.perf_counter()
    
    # Generate correlation ID for request tracing
    correlation_id = req.headers.get("x-correlation-id") or str(uuid.uuid4())
    
    logger.info(
        f"Coach endpoint called: GET /api/coach/today",
        extra={"correlation_id": correlation_id}
    )
    
    today = date.today()
    start_date = today - timedelta(days=TRAINING_WINDOW_DAYS)
    is_fallback = False
    fallback_reason = None
    
    try:
        # Step 1: Fetch activities from MCP server
        mcp_start = time.perf_counter()
        activities, mcp_error = _fetch_activities(start_date, today, correlation_id)
        mcp_latency_ms = (time.perf_counter() - mcp_start) * 1000
        _track_metric("coach.mcp_latency_ms", mcp_latency_ms, {"correlation_id": correlation_id})
        
        if mcp_error:
            fallback_reason = "mcp_unavailable"
        
        # Step 2: Build training context
        training_context = build_training_context(activities, start_date, today)
        logger.info(
            f"Built training context: {training_context.total_activities} activities, "
            f"{training_context.total_distance_miles:.1f} miles",
            extra={"correlation_id": correlation_id}
        )
        
        # Step 3: Generate AI recommendation
        ai_start = time.perf_counter()
        recommendation, ai_fallback_reason = _generate_recommendation(
            training_context, today, correlation_id, existing_fallback_reason=fallback_reason
        )
        ai_latency_ms = (time.perf_counter() - ai_start) * 1000
        _track_metric("coach.ai_latency_ms", ai_latency_ms, {"correlation_id": correlation_id})
        
        is_fallback = recommendation.fallback
        
        logger.info(
            f"Returning recommendation: {recommendation.title} (fallback={recommendation.fallback})",
            extra={"correlation_id": correlation_id}
        )
        
        response = func.HttpResponse(
            body=json.dumps(recommendation.model_dump(mode="json")),
            mimetype="application/json",
            status_code=200,
            headers={"x-correlation-id": correlation_id}
        )
        
    except Exception as e:
        logger.error(
            f"Unexpected error in coach endpoint: {e}",
            extra={"correlation_id": correlation_id},
            exc_info=True
        )
        
        is_fallback = True
        # Always return fallback on error
        fallback = get_fallback_recommendation(today, reason="error")
        response = func.HttpResponse(
            body=json.dumps(fallback.model_dump(mode="json")),
            mimetype="application/json",
            status_code=200,
            headers={"x-correlation-id": correlation_id}
        )
    
    # Track overall metrics
    total_latency_ms = (time.perf_counter() - start_time) * 1000
    _track_metric("coach.total_latency_ms", total_latency_ms, {"correlation_id": correlation_id})
    _track_metric("coach.fallback_used", 1.0 if is_fallback else 0.0, {"correlation_id": correlation_id})
    
    return response


def _fetch_activities(start_date: date, end_date: date, correlation_id: str) -> tuple:
    """
    Fetch recent activities from MCP server.
    
    Returns tuple of (activities list, had_error bool).
    Returns empty list on failure (triggers fallback recommendation).
    """
    try:
        with get_mcp_client() as client:
            activities = client.query_activities(start_date, end_date, limit=100)
            logger.info(
                f"Fetched {len(activities)} activities from MCP",
                extra={"correlation_id": correlation_id}
            )
            return activities, False
            
    except MCPClientError as e:
        logger.warning(
            f"MCP client error, will use fallback: {e}",
            extra={"correlation_id": correlation_id}
        )
        return [], True
    except Exception as e:
        logger.error(
            f"Unexpected error fetching activities: {e}",
            extra={"correlation_id": correlation_id}
        )
        return [], True


def _generate_recommendation(
    training_context,
    today: date,
    correlation_id: str,
    existing_fallback_reason: Optional[str] = None
) -> tuple:
    """
    Generate AI recommendation or return fallback.
    
    Returns tuple of (DailyRecommendation, fallback_reason or None).
    """
    # If no activities, still try AI but expect fallback-like response
    if training_context.total_activities == 0:
        logger.info(
            "No activities in training context, AI may suggest beginner workout",
            extra={"correlation_id": correlation_id}
        )
    
    try:
        ai_client = get_ai_client()
        try:
            context_dict = training_context.model_dump(mode="json")
            ai_result = ai_client.generate_recommendation(context_dict)
            
            # Validate and construct recommendation
            workout = WorkoutDetails(**ai_result["workout"])
            recommendation = DailyRecommendation(
                date=today,
                goal="half-marathon",
                title=ai_result["title"],
                workout=workout,
                rationale=ai_result["rationale"],
                confidence=ai_result["confidence"],
                fallback=False,
                fallback_reason=None
            )
            
            logger.info(
                f"AI generated recommendation: {recommendation.title}",
                extra={"correlation_id": correlation_id}
            )
            return recommendation, None
            
        finally:
            ai_client.close()
            
    except AIClientError as e:
        logger.warning(
            f"AI client error, returning fallback: {e}",
            extra={"correlation_id": correlation_id}
        )
        # Use existing fallback reason (MCP issue) or AI unavailable
        reason = existing_fallback_reason or "ai_unavailable"
        return get_fallback_recommendation(today, reason=reason), reason
        
    except Exception as e:
        logger.error(
            f"Error generating recommendation: {e}",
            extra={"correlation_id": correlation_id}
        )
        reason = existing_fallback_reason or "error"
        return get_fallback_recommendation(today, reason=reason), reason
