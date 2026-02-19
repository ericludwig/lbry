"""PMS integration management endpoints."""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.models.property_manager import PropertyManager
from app.models.property import Property
from app.schemas.property_manager import PMSConfig, PropertyManagerUpdate, PropertyManagerOut
from app.core.security import get_current_pm
from app.services.pms_service import get_pms_adapter

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.post("/pms/configure")
async def configure_pms(
    config: PMSConfig,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Save PMS integration credentials for the property manager."""
    result = await db.execute(
        select(PropertyManager).where(PropertyManager.id == current_user["user_id"])
    )
    pm = result.scalar_one_or_none()
    if not pm:
        raise HTTPException(status_code=404, detail="Not found")

    pm.pms_type = config.pms_type
    pm.pms_api_key = config.pms_api_key
    pm.pms_client_id = config.pms_client_id
    pm.pms_client_secret = config.pms_client_secret
    pm.pms_instance_url = config.pms_instance_url
    db.add(pm)
    await db.commit()
    return {"status": "configured", "pms_type": config.pms_type}


@router.post("/pms/test")
async def test_pms_connection(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Test PMS API connectivity."""
    result = await db.execute(
        select(PropertyManager).where(PropertyManager.id == current_user["user_id"])
    )
    pm = result.scalar_one_or_none()
    if not pm or not pm.pms_type:
        raise HTTPException(status_code=400, detail="PMS not configured")

    adapter = get_pms_adapter(
        pm.pms_type.value,
        api_key=pm.pms_api_key,
        client_id=pm.pms_client_id,
        client_secret=pm.pms_client_secret,
        instance_url=pm.pms_instance_url,
    )

    try:
        # Test by fetching one property's residents
        prop_result = await db.execute(
            select(Property).where(Property.property_manager_id == pm.id).limit(1)
        )
        prop = prop_result.scalar_one_or_none()
        if prop and prop.pms_property_id:
            residents = await adapter.get_residents(prop.pms_property_id)
            return {"status": "connected", "resident_count": len(residents)}
        return {"status": "connected", "note": "No properties with PMS IDs found to test with"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PMS connection failed: {str(e)}")


@router.post("/pms/sync")
async def trigger_pms_sync(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a PMS sync (runs in background)."""
    from app.tasks.reporting_tasks import sync_all_pms_data
    background_tasks.add_task(sync_all_pms_data.delay)
    return {"status": "sync_triggered", "message": "PMS sync started in background"}


@router.get("/pms/status")
async def get_pms_status(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PropertyManager).where(PropertyManager.id == current_user["user_id"])
    )
    pm = result.scalar_one_or_none()
    return {
        "pms_type": pm.pms_type.value if pm.pms_type else None,
        "is_configured": bool(pm.pms_type and (pm.pms_api_key or pm.pms_client_id)),
    }
