from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app import models
from backend.app import schemas
from backend.app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.SchedulingStrategy)
def create_scheduling_strategy(
    strategy: schemas.SchedulingStrategyCreate, db: Session = Depends(get_db)
):
    db_strategy = models.SchedulingStrategy(**strategy.dict())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.get("/", response_model=List[schemas.SchedulingStrategy])
def read_scheduling_strategies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    strategies = db.query(models.SchedulingStrategy).offset(skip).limit(limit).all()
    return strategies

@router.get("/{strategy_id}", response_model=schemas.SchedulingStrategy)
def read_scheduling_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(models.SchedulingStrategy).filter(models.SchedulingStrategy.id == strategy_id).first()
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="SchedulingStrategy not found")
    return db_strategy

@router.put("/{strategy_id}", response_model=schemas.SchedulingStrategy)
def update_scheduling_strategy(
    strategy_id: int,
    strategy: schemas.SchedulingStrategyUpdate,
    db: Session = Depends(get_db),
):
    db_strategy = db.query(models.SchedulingStrategy).filter(models.SchedulingStrategy.id == strategy_id).first()
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="SchedulingStrategy not found")
    
    update_data = strategy.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_strategy, key, value)
        
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.delete("/{strategy_id}", response_model=schemas.SchedulingStrategy)
def delete_scheduling_strategy(strategy_id: int, db: Session = Depends(get_db)):
    db_strategy = db.query(models.SchedulingStrategy).filter(models.SchedulingStrategy.id == strategy_id).first()
    if db_strategy is None:
        raise HTTPException(status_code=404, detail="SchedulingStrategy not found")
    db.delete(db_strategy)
    db.commit()
    return db_strategy