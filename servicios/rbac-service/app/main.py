from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app.models import Application, Base, Permission, Position
from app.schemas import (
    ApplicationCreate,
    ApplicationResponse,
    PermissionCreate,
    PermissionResponse,
    PositionCreate,
    PositionResponse,
)

app = FastAPI(
    title="RBAC Service",
    version="0.3.0",
)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {
        "service": "rbac-service",
        "status": "healthy",
    }


@app.get(
    "/applications",
    response_model=list[ApplicationResponse],
)
def list_applications(db: Session = Depends(get_db)):
    return db.scalars(
        select(Application).order_by(Application.id)
    ).all()


@app.post(
    "/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_application(
    application_data: ApplicationCreate,
    db: Session = Depends(get_db),
):
    existing_application = db.scalar(
        select(Application).where(
            (Application.name == application_data.name)
            | (Application.code == application_data.code)
        )
    )

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Application name or code already exists",
        )

    application = Application(
        name=application_data.name,
        code=application_data.code,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application

@app.get(
    "/positions",
    response_model=list[PositionResponse],
)
def list_positions(db: Session = Depends(get_db)):
    return db.scalars(
        select(Position).order_by(Position.id)
    ).all()


@app.post(
    "/positions",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_position(
    position_data: PositionCreate,
    db: Session = Depends(get_db),
):
    existing_position = db.scalar(
        select(Position).where(
            (Position.company_id == position_data.company_id)
            & (Position.code == position_data.code)
        )
    )

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position code already exists for this company",
        )

    position = Position(
        company_id=position_data.company_id,
        name=position_data.name,
        code=position_data.code,
    )

    db.add(position)
    db.commit()
    db.refresh(position)

    return position

@app.get(
    "/permissions",
    response_model=list[PermissionResponse],
)
def list_permissions(db: Session = Depends(get_db)):
    return db.scalars(
        select(Permission).order_by(Permission.id)
    ).all()


@app.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    permission_data: PermissionCreate,
    db: Session = Depends(get_db),
):
    existing_permission = db.scalar(
        select(Permission).where(
            Permission.name == permission_data.name
        )
    )

    if existing_permission:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission name already exists",
        )

    permission = Permission(
        name=permission_data.name,
        detail=permission_data.detail,
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)

    return permission
