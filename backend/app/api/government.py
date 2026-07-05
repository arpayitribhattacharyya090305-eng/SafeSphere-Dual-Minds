from fastapi import APIRouter, Query
from backend.app.tools.agent_tools import get_gov_schemes
from typing import List, Optional, Dict, Any

router = APIRouter(prefix="/government", tags=["Government Relief Schemes"])

@router.get("/schemes", response_model=List[Dict[str, Any]])
def list_government_schemes(
    category: Optional[str] = Query(
        None,
        description="Filter by category: Compensation, Medical Aid, Housing, Relief Fund"
    )
):
    """
    Returns all available government disaster relief schemes.
    Optionally filter by category.
    """
    return get_gov_schemes(category)
