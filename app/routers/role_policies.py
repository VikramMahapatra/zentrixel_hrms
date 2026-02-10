from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RolePolicy
from app.schemas import (
    RolePolicyRequest,
    RolePolicyListResponse
)
from app.security import has_role

router = APIRouter(
    prefix="/api/role-policies",
    tags=["Role Policies"]
)



@router.get("/", response_model=RolePolicyListResponse)
def get_role_policies(
    role_id: int,
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"]))
):
    policies = db.query(RolePolicy).filter(
        RolePolicy.role_id == role_id
    ).all()

    return {"policies": policies}


@router.post("/")
def save_role_policies(
    request: RolePolicyRequest,
    db: Session = Depends(get_db),
    user = Depends(has_role(["admin"]))
):
    existing = db.query(RolePolicy).filter(
        RolePolicy.role_id == request.role_id
    ).all()

    existing_map = {(p.resource, p.action): p for p in existing}
    incoming_keys = set()

    # Add new / keep existing
    for p in request.policies:
        key = (p.resource, p.action)
        incoming_keys.add(key)

        if key not in existing_map:
            db.add(
                RolePolicy(
                    role_id=request.role_id,
                    resource=p.resource,
                    action=p.action
                )
            )

    # Delete unchecked
    for key, policy in existing_map.items():
        if key not in incoming_keys:
            db.delete(policy)

    db.commit()
    return {"success": True}
