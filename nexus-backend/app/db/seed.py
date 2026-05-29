import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AsyncSessionLocal, GraphNode, GraphEdge, TargetRegistry, WebSnapshot, engine, Base

from sqlalchemy import text
from datetime import datetime, timedelta

async def seed_data():
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        existing = await session.execute(text("SELECT COUNT(id) FROM graph_nodes"))
        if existing.scalar() > 0:
            return

        now = datetime.utcnow()
        t_minus_60 = now - timedelta(days=60)
        t_minus_30 = now - timedelta(days=30)
        t_minus_15 = now - timedelta(days=15)
        t_minus_5 = now - timedelta(days=5)

        # =====================================================================
        # TENANT: PUBLIC MARKET INTEL
        # =====================================================================
        t_pub = "tenant_public"
        
        nodes_pub = [
            GraphNode(name="Notion", node_type="Company", sector="Productivity SaaS", tenant_id=t_pub, attributes={"market_share": 45}, created_at=t_minus_60),
            GraphNode(name="Airtable", node_type="Company", sector="Productivity SaaS", tenant_id=t_pub, attributes={"market_share": 30}, created_at=t_minus_60),
            GraphNode(name="Monday", node_type="Company", sector="Productivity SaaS", tenant_id=t_pub, attributes={"market_share": 20}, created_at=t_minus_30),
            GraphNode(name="OpenAI", node_type="Company", sector="AI Foundation", tenant_id=t_pub, attributes={"market_share": 80}, created_at=t_minus_60),
            GraphNode(name="Anthropic", node_type="Company", sector="AI Foundation", tenant_id=t_pub, attributes={"market_share": 15}, created_at=t_minus_15),
            GraphNode(name="Stripe", node_type="Company", sector="Fintech", tenant_id=t_pub, attributes={"market_share": 60}, created_at=t_minus_60),
            GraphNode(name="Ramp", node_type="Company", sector="Fintech", tenant_id=t_pub, attributes={"market_share": 25}, created_at=t_minus_30),
        ]
        
        node_map = {}
        for n in nodes_pub:
            session.add(n)
            await session.flush()
            node_map[n.name] = n
            
            tr = TargetRegistry(
                company_name=n.name,
                normalized_name=n.name.lower(),
                url=f"https://{n.name.lower()}.com",
                sector=n.sector,
                tenant_id=t_pub,
                onboarding_state="ACTIVE",
                validation_state="VERIFIED",
                scheduler_assignment_state="ASSIGNED",
                integrity_score=98.5
            )
            session.add(tr)
            
            # Seed 3 maturity snapshots so they can be simulated
            for i in range(3):
                snap_time = now - timedelta(days=(3-i)*10)
                snap = WebSnapshot(
                    tenant_id=t_pub,
                    competitor_name=n.name,
                    source_url=tr.url,
                    snapshot_status="LIVE",
                    fetch_source="PLAYWRIGHT_CHROMIUM",
                    scraped_data={"pricing": {"tier": "Enterprise", "price": "Contact Sales"}, "features": ["SSO", "Audit Logs"], "raw_html": f"<html><body>{n.name} data snapshot {i}</body></html>"},
                    dom_hash=f"{n.name.lower()}_dom_{int(snap_time.timestamp())}_{i}",
                    created_at=snap_time
                )
                session.add(snap)

        # Create temporal edges
        edges = [
            GraphEdge(source_id=node_map["Notion"].id, target_id=node_map["Airtable"].id, relationship_type="competing_with", strength=0.8, created_at=t_minus_60, tenant_id=t_pub),
            GraphEdge(source_id=node_map["OpenAI"].id, target_id=node_map["Anthropic"].id, relationship_type="accelerating_AI", strength=0.9, created_at=t_minus_15, tenant_id=t_pub),
            GraphEdge(source_id=node_map["Stripe"].id, target_id=node_map["Ramp"].id, relationship_type="competing_with", strength=0.7, created_at=t_minus_30, tenant_id=t_pub),
            GraphEdge(source_id=node_map["Notion"].id, target_id=node_map["OpenAI"].id, relationship_type="integrating_AI", strength=0.6, created_at=t_minus_5, tenant_id=t_pub),
        ]
        for e in edges:
            session.add(e)
            
        await session.commit()
        
        # =====================================================================
        # TENANT: CLASSIFIED SANDBOX
        # =====================================================================
        t_sand = "tenant_sandbox"
        
        nodes_sand = [
            GraphNode(name="Project OMEGA", node_type="Synthetic Target", sector="Defense", tenant_id=t_sand, attributes={"threat_level": "CRITICAL"}, created_at=t_minus_60),
            GraphNode(name="Aegis Subsystem", node_type="Internal Simulation", sector="Defense", tenant_id=t_sand, attributes={"stability": 42.1}, created_at=t_minus_30),
            GraphNode(name="Contradiction Alpha", node_type="Anomaly", sector="Unknown", tenant_id=t_sand, attributes={"pressure": 99.9}, created_at=t_minus_15),
            GraphNode(name="Nexus Telemetry", node_type="Infrastructure", sector="Internal", tenant_id=t_sand, attributes={"status": "ISOLATED"}, created_at=t_minus_5),
        ]
        
        sandbox_map = {}
        for n in nodes_sand:
            session.add(n)
            await session.flush()
            sandbox_map[n.name] = n
            
            tr = TargetRegistry(
                company_name=n.name,
                normalized_name=n.name.lower().replace(" ", "_"),
                url=f"internal://{n.name.lower().replace(' ', '-')}",
                sector=n.sector,
                tenant_id=t_sand,
                onboarding_state="ACTIVE",
                validation_state="VERIFIED",
                scheduler_assignment_state="ASSIGNED",
                integrity_score=100.0
            )
            session.add(tr)
            
            # Seed 3 maturity snapshots so they can be simulated
            for i in range(3):
                snap_time = now - timedelta(days=(3-i)*10)
                snap = WebSnapshot(
                    tenant_id=t_sand,
                    competitor_name=n.name,
                    source_url=tr.url,
                    snapshot_status="LIVE",
                    fetch_source="CLASSIFIED_INTERNAL",
                    scraped_data={"telemetry": {"latency_ms": 15.4, "packet_loss": 0.01}, "status": "NOMINAL", "raw_feed": f"[{n.name}] internal secure feed frame {i}"},
                    dom_hash=f"{n.name.lower().replace(' ', '_')}_sig_{int(snap_time.timestamp())}_{i}",
                    created_at=snap_time
                )
                session.add(snap)
        
        edges_sand = [
            GraphEdge(source_id=sandbox_map["Project OMEGA"].id, target_id=sandbox_map["Aegis Subsystem"].id, relationship_type="depends_on", strength=0.9, created_at=t_minus_30, tenant_id=t_sand),
            GraphEdge(source_id=sandbox_map["Contradiction Alpha"].id, target_id=sandbox_map["Project OMEGA"].id, relationship_type="threatens", strength=0.95, created_at=t_minus_15, tenant_id=t_sand),
            GraphEdge(source_id=sandbox_map["Nexus Telemetry"].id, target_id=sandbox_map["Aegis Subsystem"].id, relationship_type="monitors", strength=1.0, created_at=t_minus_5, tenant_id=t_sand)
        ]
        for e in edges_sand:
            session.add(e)

        await session.commit()
        print("Database seamlessly seeded with isolated tenant data and temporal history.")

if __name__ == "__main__":
    asyncio.run(seed_data())
