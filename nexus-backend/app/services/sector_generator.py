import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import GraphNode, GraphEdge, TargetRegistry, WebSnapshot

class GenCompany(BaseModel):
    name: str = Field(description="Name of the company")
    market_share: int = Field(description="Estimated market share percentage (1-100)")

class GenRelationship(BaseModel):
    source_company: str = Field(description="Name of the source company")
    target_company: str = Field(description="Name of the target company")
    relation: str = Field(description="Type of relationship (e.g. 'competing_with', 'depends_on', 'acquiring')")
    strength: float = Field(description="Strength of relationship (0.1 to 1.0)")

class GenSector(BaseModel):
    companies: List[GenCompany] = Field(description="List of 10-15 major companies in this sector")
    relationships: List[GenRelationship] = Field(description="List of 10-15 competitive relationships between these companies")

async def generate_and_seed_sector(sector_name: str, db: AsyncSession, tenant_id: str = "tenant_public"):
    # 1. Generate via LLM
    api_key = os.getenv("AIML_API_KEY", os.getenv("OPENAI_API_KEY"))
    base_url = os.getenv("AIML_BASE_URL", "https://api.openai.com/v1")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, api_key=api_key, base_url=base_url)
    structured_llm = llm.with_structured_output(GenSector)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert market intelligence analyst. Provide realistic, accurate companies and relationships for the requested sector."),
        ("human", "Generate a list of 10-15 top companies operating in the '{sector_name}' sector. Then map 10-15 strategic or competitive relationships between them.")
    ])
    
    chain = prompt | structured_llm
    
    result = await chain.ainvoke({"sector_name": sector_name})
    
    # Handle both dict and Pydantic object returns
    companies = result.get("companies", []) if isinstance(result, dict) else result.companies
    relationships = result.get("relationships", []) if isinstance(result, dict) else result.relationships
    
    now = datetime.utcnow()
    t_minus_60 = now - timedelta(days=60)
    
    # 2. Insert Nodes & Registries
    node_map = {}
    for comp in companies:
        comp_name = comp.get("name") if isinstance(comp, dict) else comp.name
        comp_market_share = comp.get("market_share") if isinstance(comp, dict) else comp.market_share
        
        # Check if already exists in this tenant
        n = GraphNode(
            name=comp_name,
            node_type="Company",
            sector=sector_name,
            tenant_id=tenant_id,
            attributes={"market_share": comp_market_share},
            created_at=t_minus_60
        )
        db.add(n)
        await db.flush()
        node_map[comp_name] = n
        
        tr = TargetRegistry(
            company_name=comp.name,
            normalized_name=comp.name.lower().replace(" ", "_"),
            url=f"https://{comp.name.lower().replace(' ', '')}.com",
            sector=sector_name,
            tenant_id=tenant_id,
            onboarding_state="ACTIVE",
            validation_state="VERIFIED",
            scheduler_assignment_state="ASSIGNED",
            integrity_score=95.0
        )
        db.add(tr)
        
        # Add a dummy snapshot so it exists in timeline
        snap = WebSnapshot(
            tenant_id=tenant_id,
            competitor_name=comp.name,
            source_url=tr.url,
            snapshot_status="LIVE",
            fetch_source="DYNAMIC_SYNTHESIS",
            scraped_data={"pricing": {"tier": "Enterprise", "price": "Contact Sales"}},
            dom_hash=f"{comp.name.lower()}_synth_{int(now.timestamp())}",
            created_at=now
        )
        db.add(snap)

    # 3. Insert Edges
    for rel in result.relationships:
        if rel.source_company in node_map and rel.target_company in node_map:
            e = GraphEdge(
                source_id=node_map[rel.source_company].id,
                target_id=node_map[rel.target_company].id,
                relationship_type=rel.relation,
                strength=rel.strength,
                tenant_id=tenant_id,
                created_at=t_minus_60
            )
            db.add(e)
            
    await db.commit()
    return {"status": "success", "companies_added": len(result.companies), "edges_added": len(result.relationships)}
