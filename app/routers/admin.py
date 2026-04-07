from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import APIRouter
from ..database import get_db
from .. import models
from ..dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/test")
def test_admin():
    return {"message": "Admin is working"}

def ensure_admin(user):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

@router.get("/tickets")
def admin_all_tickets(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ensure_admin(current_user)

    tickets = db.query(models.Ticket).all()
    return tickets
@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ensure_admin(current_user)

    total_tickets = db.query(models.Ticket).count()

    open_tickets = db.query(models.Ticket).filter(
        models.Ticket.status == "open"
    ).count()

    closed_tickets = db.query(models.Ticket).filter(
        models.Ticket.status == "closed"
    ).count()

    grouped_data = db.query(
        models.User.username.label("username"),
        func.count(models.Ticket.id).label("ticket_count")
    ).join(
        models.Ticket,
        models.User.id == models.Ticket.created_by
    ).group_by(
        models.User.username
    ).all()

    user_ticket_counts = []
    for row in grouped_data:
        user_ticket_counts.append({
            "username": row.username,
            "ticket_count": row.ticket_count
        })

    return {
        "total": total_tickets,
        "open": open_tickets,
        "closed": closed_tickets,
        "user_ticket_counts": user_ticket_counts
    }