import asyncio
from datetime import datetime, timedelta
import uuid
import json
import os
import sys

# Add the parent directory to the path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.db.models import AsyncSessionLocal, GraphNode, GraphEdge, TargetRegistry

async def seed_demo_stories():
    print("Seeding Unified Demo Narrative Dataset...")
    
    tenant_id = "tenant_demo"
    now = datetime.utcnow()
    
    async with AsyncSessionLocal() as session:
        # Clear existing demo data
        from sqlalchemy import delete
        await session.execute(delete(GraphEdge).where(GraphEdge.tenant_id == tenant_id))
        await session.execute(delete(GraphNode).where(GraphNode.tenant_id == tenant_id))
        await session.execute(delete(TargetRegistry).where(TargetRegistry.tenant_id == tenant_id))
        
        # ---------------------------------------------------------
        # TARGET REGISTRY
        # ---------------------------------------------------------
        targets = [
            TargetRegistry(tenant_id=tenant_id, company_name="NovaFlow", normalized_name="novaflow", url="https://novaflow.io", sector="Data Operations", onboarding_state="ACTIVE", active=1),
            TargetRegistry(tenant_id=tenant_id, company_name="VectorHQ", normalized_name="vectorhq", url="https://vectorhq.com", sector="Data Operations", onboarding_state="ACTIVE", active=1),
            TargetRegistry(tenant_id=tenant_id, company_name="NimbusCore", normalized_name="nimbuscore", url="https://nimbuscore.ai", sector="Data Operations", onboarding_state="ACTIVE", active=1),
        ]
        session.add_all(targets)
        
        # ---------------------------------------------------------
        # TIME HORIZONS (Months 1-6)
        # ---------------------------------------------------------
        t_month_1 = now - timedelta(days=150) # Month 1: NovaFlow launches enterprise
        t_month_2 = now - timedelta(days=120) # Month 2: VectorHQ cuts pricing
        t_month_3 = now - timedelta(days=90)  # Month 3: NimbusCore removes features
        t_month_4 = now - timedelta(days=60)  # Month 4: Sector Pricing Compression
        t_month_5 = now - timedelta(days=30)  # Month 5: Market Retreat
        t_month_6 = now - timedelta(days=0)   # Month 6: Consolidation Opportunity
        
        # ---------------------------------------------------------
        # NODES
        # ---------------------------------------------------------
        # Entities
        n_nova = GraphNode(tenant_id=tenant_id, node_type="Company", name="NovaFlow", sector="Data Operations", created_at=t_month_1 - timedelta(days=1))
        n_vector = GraphNode(tenant_id=tenant_id, node_type="Company", name="VectorHQ", sector="Data Operations", created_at=t_month_1 - timedelta(days=1))
        n_nimbus = GraphNode(tenant_id=tenant_id, node_type="Company", name="NimbusCore", sector="Data Operations", created_at=t_month_1 - timedelta(days=1))
        
        # Features & Pricing
        n_nova_ent = GraphNode(tenant_id=tenant_id, node_type="Feature", name="Enterprise Tier ($99)", sector="Data Operations", created_at=t_month_1)
        n_vector_price = GraphNode(tenant_id=tenant_id, node_type="PricingModel", name="Aggressive Discount (-30%)", sector="Data Operations", created_at=t_month_2)
        n_nimbus_feat = GraphNode(tenant_id=tenant_id, node_type="Feature", name="Deprecated: Advanced Analytics", sector="Data Operations", created_at=t_month_3)
        n_nimbus_tier = GraphNode(tenant_id=tenant_id, node_type="PricingModel", name="Tier Consolidation", sector="Data Operations", created_at=t_month_3)
        
        # Emerging Trends
        n_compression = GraphNode(tenant_id=tenant_id, node_type="SectorTrend", name="Pricing Compression", sector="Data Operations", created_at=t_month_4)
        n_retreat = GraphNode(tenant_id=tenant_id, node_type="SectorTrend", name="Market Retreat", sector="Data Operations", created_at=t_month_5)
        n_consolidation = GraphNode(tenant_id=tenant_id, node_type="SectorTrend", name="Consolidation Opportunity", sector="Data Operations", created_at=t_month_6)
        
        nodes = [n_nova, n_vector, n_nimbus, n_nova_ent, n_vector_price, n_nimbus_feat, n_nimbus_tier, n_compression, n_retreat, n_consolidation]
        session.add_all(nodes)
        await session.flush() # flush to get IDs
        
        # ---------------------------------------------------------
        # EDGES (Causal & Correlational)
        # ---------------------------------------------------------
        edges = [
            # Month 1
            GraphEdge(tenant_id=tenant_id, source_id=n_nova.id, target_id=n_nova_ent.id, relationship_type="launched", created_at=t_month_1, last_updated_at=t_month_1, strength=0.9),
            
            # Month 2
            GraphEdge(tenant_id=tenant_id, source_id=n_vector.id, target_id=n_vector_price.id, relationship_type="implemented", created_at=t_month_2, last_updated_at=t_month_2, strength=0.8),
            GraphEdge(tenant_id=tenant_id, source_id=n_vector_price.id, target_id=n_nova_ent.id, relationship_type="defensive_response_to", created_at=t_month_2, last_updated_at=t_month_2, strength=0.7),
            
            # Month 3
            GraphEdge(tenant_id=tenant_id, source_id=n_nimbus.id, target_id=n_nimbus_feat.id, relationship_type="removed", created_at=t_month_3, last_updated_at=t_month_3, strength=0.8),
            GraphEdge(tenant_id=tenant_id, source_id=n_nimbus.id, target_id=n_nimbus_tier.id, relationship_type="implemented", created_at=t_month_3, last_updated_at=t_month_3, strength=0.75),
            
            # Month 4: Pricing Compression Emerges
            GraphEdge(tenant_id=tenant_id, source_id=n_vector_price.id, target_id=n_compression.id, relationship_type="drives", created_at=t_month_4, last_updated_at=t_month_4, strength=0.85),
            GraphEdge(tenant_id=tenant_id, source_id=n_nimbus_tier.id, target_id=n_compression.id, relationship_type="drives", created_at=t_month_4, last_updated_at=t_month_4, strength=0.8),
            
            # Month 5: Market Retreat Emerges
            GraphEdge(tenant_id=tenant_id, source_id=n_nimbus_feat.id, target_id=n_retreat.id, relationship_type="signals", created_at=t_month_5, last_updated_at=t_month_5, strength=0.9),
            GraphEdge(tenant_id=tenant_id, source_id=n_compression.id, target_id=n_retreat.id, relationship_type="catalyzes", created_at=t_month_5, last_updated_at=t_month_5, strength=0.7),
            
            # Month 6: Consolidation
            GraphEdge(tenant_id=tenant_id, source_id=n_retreat.id, target_id=n_consolidation.id, relationship_type="creates", created_at=t_month_6, last_updated_at=t_month_6, strength=0.9),
            GraphEdge(tenant_id=tenant_id, source_id=n_nova.id, target_id=n_consolidation.id, relationship_type="capitalizes_on", created_at=t_month_6, last_updated_at=t_month_6, strength=0.8),
        ]
        
        session.add_all(edges)
        
        await session.commit()
        print(f"Successfully seeded Demo Narrative Dataset for tenant_demo. Created {len(nodes)} nodes and {len(edges)} edges.")

if __name__ == "__main__":
    asyncio.run(seed_demo_stories())
