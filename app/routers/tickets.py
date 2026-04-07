from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from typing import Optional, List , Literal
from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user
from ..logging_config import logger

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# PROTECTED ROUTE
@router.get("/protected")
def protected_route(current_user = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user_id": current_user.id,
        "role": current_user.role
    }


# CREATE TICKET
@router.post("/")
def create_ticket(
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    new_ticket = models.Ticket(
        title=ticket.title,
        description=ticket.description,
        priority=ticket.priority,
        category=ticket.category,
        created_by=current_user.id
    )

    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    logger.info(f"Ticket created: id={new_ticket.id}, user={current_user.id}")
    return new_ticket

# LIST TICKETS
from typing import Optional, List

@router.get("/", response_model=List[schemas.TicketOut])
def list_tickets(
        status_filter: Optional[Literal["open", "in_progress", "closed"]] = Query(default=None),
        priority: Optional[Literal["low", "medium", "high"]] = Query(default=None),
        category: Optional[Literal["bug", "feature", "support", "other"]] = Query(default=None),
        search: Optional[str] = Query(default=None, min_length=1, max_length=200),
        sort_by: Literal["created_at", "updated_at", "priority", "status", "title"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
        limit: int = Query(default=10, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    query = db.query(models.Ticket)

    # role-based filter
    if current_user.role != "admin":
        query = query.filter(models.Ticket.created_by == current_user.id)

    # filters
    if status_filter:
        query = query.filter(models.Ticket.status == status_filter)

    if priority:
        query = query.filter(models.Ticket.priority == priority)

    if category:
        query = query.filter(models.Ticket.category == category)

    # search (title + description)
    if search:
        query = query.filter(
            models.Ticket.title.ilike(f"%{search}%") |
            models.Ticket.description.ilike(f"%{search}%")
        )

    # sorting
    sort_column = getattr(models.Ticket, sort_by, models.Ticket.created_at)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # pagination
    query = query.offset(offset).limit(limit)

    return query.all()

# GET SINGLE TICKET
@router.get("/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket_by_id(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ticket

# UPDATE TICKET
@router.put("/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(
    ticket_id: int,
    payload: schemas.TicketEdit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    data = payload.dict(exclude_unset=True)

    for field in data:
        setattr(ticket, field, data[field])

    db.commit()
    db.refresh(ticket)
    logger.info(f"Ticket updated: id={ticket.id}, user={current_user.id}")
    return ticket

# UPDATE STATUS
@router.patch("/{ticket_id}/status", response_model=schemas.TicketOut)
def change_ticket_status(
    ticket_id: int,
    payload: schemas.TicketStatusChange,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    ticket.status = payload.status

    db.commit()
    db.refresh(ticket)

    return ticket

# DELETE TICKET
@router.delete("/{ticket_id}")
def remove_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    if current_user.role != "admin" and ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    ticket_id_value = ticket.id
    db.delete(ticket)
    db.commit()
    logger.info(f"Ticket deleted: id={ticket_id_value}, user={current_user.id}")
    return {"detail": "Ticket deleted"}

# ASSIGN TICKET
@router.patch("/{ticket_id}/assign/{user_id}", response_model=schemas.TicketOut)
def assign_ticket(
    ticket_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin allowed")

    ticket = db.query(models.Ticket).filter(
        models.Ticket.id == ticket_id
    ).first()

    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    ticket.assigned_to = user.id

    db.commit()
    db.refresh(ticket)

    return ticket