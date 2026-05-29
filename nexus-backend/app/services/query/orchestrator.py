import logging
import asyncio
import time
import json
import uuid
from typing import Dict, Any, List
from cachetools import TTLCache

from app.services.graph.builder import build_ephemeral_graph
from app.services.graph.queries import get_sector_emergence, get_company_cognition_path
from app.services.graph.sector_intelligence import inject_sector_emergence
from app.schemas.intelligence import TrajectoryProjection, TemporalCompression, DegradedState

logger = logging.getLogger(__name__)

# Phase 17: Platform Stabilization
MAX_CONCURRENT_BUILDS = 10
graph_semaphore = asyncio.Semaphore(MAX_CONCURRENT_BUILDS)

# Ephemeral Request Cache Layer (Caches the projection, NOT mutable state)
# Normalization: workspace:persona:company:session
projection_cache = TTLCache(maxsize=1000, ttl=60)

def compress_trajectory(signals: List[Dict[str, Any]]) -> TemporalCompression:
    """
    Temporal Trajectory Compression.
    Summarizes a noisy sequence of signals into an executive-grade progression state.
    """
    if not signals:
        return TemporalCompression(summary="Stable", timeframe="0 days", dominant_trend="NONE", signal_count=0)
        
    signal_types = [s.get("type", "") for s in signals]
    
    if "PRICING_COMPRESSION" in signal_types and "TIER_REMOVED" in signal_types:
        dominant_trend = "Market Retreat"
    elif "PRICING_INCREASE" in signal_types:
        dominant_trend = "Aggressive Expansion"
    elif "FEATURE_ADDED" in signal_types:
        dominant_trend = "Feature Escalation"
    elif "PRICING_COMPRESSION" in signal_types:
        dominant_trend = "Pricing Compression"
    else:
        dominant_trend = "Structural Realignment"
        
    timeframe = "Recent Progression" 
        
    return TemporalCompression(
        summary=f"{timeframe}: {dominant_trend}",
        timeframe=timeframe,
        dominant_trend=dominant_trend,
        signal_count=len(signals)
    )

async def _build_and_query_company(company_name: str, trace_id: str) -> TrajectoryProjection:
    start_time = time.perf_counter()
    
    async with graph_semaphore:
        # Note: In an enterprise environment, graph building itself might be blocking and require run_in_executor
        graph = build_ephemeral_graph()
        try:
            mock_signals = [n.attributes for n in graph.nodes.values() if n.node_type == "SIGNAL"]
            compression = compress_trajectory(mock_signals)
            
            projection = TrajectoryProjection(
                company=company_name,
                trace_id=trace_id,
                degraded_state=DegradedState.OK if mock_signals else DegradedState.NO_DATA,
                trajectory_compression=compression,
                raw_signal_count=len(mock_signals)
            )
            return projection
        finally:
            graph.clear()
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(json.dumps({
                "event": "graph_build_complete",
                "trace_id": trace_id,
                "company": company_name,
                "duration_ms": duration_ms,
                "status": "SUCCESS"
            }))

async def orchestrate_company_query(
    company_name: str, 
    workspace: str = "tenant_public", 
    persona_id: str = "SYSTEM", 
    session_id: str = "LIVE",
    trace_id: str = None
) -> TrajectoryProjection:
    """
    Stateless Lifecycle for Company cognition path with Ephemeral Caching and Timeout Boundaries.
    """
    trace_id = trace_id or uuid.uuid4().hex
    cache_key = f"{workspace}:{persona_id}:{company_name}:{session_id}"
    
    # Cache hit check
    if cache_key in projection_cache:
        logger.info(json.dumps({"event": "cache_hit", "trace_id": trace_id, "cache_key": cache_key}))
        cached_proj = projection_cache[cache_key]
        cached_proj.cached = True
        return cached_proj

    # Missing Cache - Build and Query with Failsafe Timeout
    try:
        # Failsafe bound: 5.0 seconds
        projection = await asyncio.wait_for(_build_and_query_company(company_name, trace_id), timeout=5.0)
        projection_cache[cache_key] = projection
        return projection
    except asyncio.TimeoutError:
        logger.error(json.dumps({"event": "graph_build_timeout", "trace_id": trace_id, "company": company_name}))
        return TrajectoryProjection(
            company=company_name,
            trace_id=trace_id,
            degraded_state=DegradedState.TIMEOUT
        )
    except Exception as e:
        logger.error(json.dumps({"event": "graph_build_failed", "trace_id": trace_id, "company": company_name, "error": str(e)}))
        return TrajectoryProjection(
            company=company_name,
            trace_id=trace_id,
            degraded_state=DegradedState.DEGRADED_PROJECTION
        )

async def orchestrate_sector_query(trace_id: str = None) -> List[Dict[str, Any]]:
    """
    Stateless Lifecycle: Load -> Build -> Query -> Dispose.
    Sector cache could also be added similarly.
    """
    trace_id = trace_id or uuid.uuid4().hex
    start_time = time.perf_counter()
    
    async with graph_semaphore:
        graph = build_ephemeral_graph()
        try:
            inject_sector_emergence(graph)
            result = get_sector_emergence(graph)
            return result
        finally:
            graph.clear()
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(json.dumps({
                "event": "sector_build_complete",
                "trace_id": trace_id,
                "duration_ms": duration_ms
            }))
