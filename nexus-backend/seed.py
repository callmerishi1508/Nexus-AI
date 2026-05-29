import asyncio
import uuid
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import GraphNode, GraphEdge, TargetRegistry, GovernanceReview, Base

engine = create_async_engine('sqlite+aiosqlite:///./nexus.db')
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sector Data Definitions
public_sectors_data = {
    'AI Technology': ['OpenAI', 'Anthropic', 'DeepMind', 'Mistral AI', 'Cohere', 'Hugging Face', 'Stability AI', 'Scale AI', 'Midjourney', 'Adept', 'Inflection AI', 'Runway', 'xAI', 'Perplexity'],
    'Agriculture Technology': ['John Deere', 'Trimble', 'Climate Corp', 'Farmers Business Network', 'Indigo Agriculture', 'Bayer Crop Science', 'Pivot Bio', 'Cibus', 'AgriWebb', 'CropX', 'Taranis', 'Blue River Technology', 'Bowery Farming', 'Plenty'],
    'Cyber Security': ['CrowdStrike', 'Palo Alto Networks', 'Fortinet', 'Zscaler', 'Cloudflare', 'Okta', 'SentinelOne', 'Check Point', 'CyberArk', 'Trend Micro', 'Tenable', 'Proofpoint', 'Wiz', 'Snyk'],
    'Fintech': ['Stripe', 'Square', 'Plaid', 'Coinbase', 'Adyen', 'Revolut', 'Klarna', 'Brex', 'Chime', 'Robinhood', 'Affirm', 'NuBank', 'Marqeta', 'Toast'],
    'Healthcare SaaS': ['Veeva Systems', 'Epic Systems', 'Cerner', 'Athenahealth', 'Teladoc', 'Doximity', 'Tempus', 'Ro', 'Oscar Health', 'Hims & Hers', 'Flatiron Health', 'Zocdoc', 'Color', 'Oura']
}

sandbox_sectors_data = {
    'Classified Defense Tech': ['Palantir', 'Anduril', 'Shield AI', 'Rebellion Defense', 'Epirus', 'HawkEye 360', 'Vannevar Labs', 'Helsing', 'Saildrone', 'Echodyne'],
    'AI Technology': ['OpenAI', 'Anthropic', 'DeepMind', 'Scale AI'], # Overlap for context
}

SIGNAL_TYPES = ["PRICING_COMPRESSION", "PRICING_INCREASE", "FEATURE_ADDED", "TIER_REMOVED", "EXECUTIVE_DEPARTURE", "MARKET_EXPANSION", "REGULATORY_FILING"]

async def seed_tenant(db: AsyncSession, tenant_id: str, sectors_data: dict):
    now = datetime.utcnow()
    
    # Store nodes temporarily to build edges
    sector_nodes = {}
    
    for sector, companies in sectors_data.items():
        sector_nodes[sector] = []
        for i, comp in enumerate(companies):
            t_minus = now - timedelta(days=random.randint(1, 60))
            
            # 1. Company Node
            node_id = str(uuid.uuid4())
            n = GraphNode(
                id=node_id,
                name=comp,
                node_type='Company',
                sector=sector,
                tenant_id=tenant_id,
                attributes={'market_share': max(1, 100 - i * 5)},
                created_at=t_minus
            )
            db.add(n)
            sector_nodes[sector].append(n)
            
            # 2. Target Registry
            tr = TargetRegistry(
                company_name=comp,
                normalized_name=f"{tenant_id}_{comp.lower().replace(' ', '_')}",
                url=f'https://www.{comp.lower().replace(" ", "")}.com',
                sector=sector,
                tenant_id=tenant_id,
                onboarding_state='ACTIVE',
                validation_state='VALIDATED',
                scheduler_assignment_state='ASSIGNED',
                created_at=t_minus
            )
            db.add(tr)
            
            # 3. Signals for this Company (Creates the intelligence context)
            num_signals = random.randint(2, 5)
            for s_idx in range(num_signals):
                sig_type = random.choice(SIGNAL_TYPES)
                s_id = str(uuid.uuid4())
                sig_node = GraphNode(
                    id=s_id,
                    name=f"Signal_{comp}_{sig_type}",
                    node_type='SIGNAL',
                    sector=sector,
                    tenant_id=tenant_id,
                    attributes={"type": sig_type, "confidence": random.uniform(80, 100), "impact": random.uniform(50, 100)},
                    created_at=t_minus + timedelta(days=s_idx)
                )
                db.add(sig_node)
                
                # Link Signal to Company
                edge = GraphEdge(
                    tenant_id=tenant_id,
                    source_id=s_id,
                    target_id=node_id,
                    relationship_type="impacts",
                    strength=random.uniform(0.5, 1.0)
                )
                db.add(edge)
                
        # 4. Generate Edges between companies in the same sector
        companies_in_sector = sector_nodes[sector]
        if len(companies_in_sector) > 1:
            for _ in range(len(companies_in_sector) * 2): # random number of connections
                c1 = random.choice(companies_in_sector)
                c2 = random.choice(companies_in_sector)
                if c1.id != c2.id:
                    rel = random.choice(["competing_with", "mirrors_pricing", "accelerating", "stealing_market_share"])
                    edge = GraphEdge(
                        tenant_id=tenant_id,
                        source_id=c1.id,
                        target_id=c2.id,
                        relationship_type=rel,
                        strength=random.uniform(0.4, 0.9)
                    )
                    db.add(edge)

    # 5. Governance Reviews
    for sector in sectors_data.keys():
        for _ in range(2):
            rev = GovernanceReview(
                tenant_id=tenant_id,
                status="REVIEW_REQUIRED",
                brief_data=f'{{"summary": "Anomalous pricing cluster detected in {sector}.", "action": "Requires executive arbitration."}}',
                priority_score=random.uniform(85, 99),
                review_reason="Automated trigger: Market threshold crossed.",
                risk_level="HIGH",
                escalation_priority="URGENT",
                evidence_anchors='["Signal_A", "Signal_B"]'
            )
            db.add(rev)


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        print("Seeding Public Tenant...")
        await seed_tenant(db, 'tenant_public', public_sectors_data)
        
        print("Seeding Sandbox Tenant...")
        await seed_tenant(db, 'tenant_sandbox', sandbox_sectors_data)

        await db.commit()
        print('Seeding complete!')

asyncio.run(seed())
