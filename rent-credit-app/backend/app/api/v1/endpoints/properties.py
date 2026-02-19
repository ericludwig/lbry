from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.db.base import get_db
from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate, PropertyOut
from app.core.security import get_current_pm

router = APIRouter(prefix="/properties", tags=["properties"])


@router.post("/", response_model=PropertyOut)
async def create_property(
    data: PropertyCreate,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    prop = Property(
        property_manager_id=current_user["user_id"],
        **data.model_dump(),
    )
    db.add(prop)
    await db.commit()
    await db.refresh(prop)
    return prop


@router.get("/", response_model=list[PropertyOut])
async def list_properties(
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property).where(
            and_(
                Property.property_manager_id == current_user["user_id"],
                Property.is_active == True,
            )
        )
    )
    return result.scalars().all()


@router.get("/{property_id}", response_model=PropertyOut)
async def get_property(
    property_id: str,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.property_manager_id == current_user["user_id"],
            )
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.patch("/{property_id}", response_model=PropertyOut)
async def update_property(
    property_id: str,
    data: PropertyUpdate,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.property_manager_id == current_user["user_id"],
            )
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(prop, k, v)
    await db.commit()
    await db.refresh(prop)
    return prop


@router.delete("/{property_id}")
async def delete_property(
    property_id: str,
    current_user=Depends(get_current_pm),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Property).where(
            and_(
                Property.id == property_id,
                Property.property_manager_id == current_user["user_id"],
            )
        )
    )
    prop = result.scalar_one_or_none()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop.is_active = False
    await db.commit()
    return {"status": "deleted"}
