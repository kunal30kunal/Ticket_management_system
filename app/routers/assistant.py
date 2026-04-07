from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..dependencies import get_current_user
from .. import models, schemas

router = APIRouter(prefix="/assistant", tags=["Assistant"])


def extract_first_number(text: str):
    cleaned_text = text.replace("?", " ").replace(",", " ").replace(".", " ")
    parts = cleaned_text.split()

    for part in parts:
        if part.isdigit():
            return int(part)

    return None


def get_ticket_query(db: Session, current_user):
    query = db.query(models.Ticket)

    if current_user.role != "admin":
        query = query.filter(models.Ticket.created_by == current_user.id)

    return query


@router.get("/ask", response_model=schemas.AssistantResponse)
def ask_assistant(
    question: str = Query(..., min_length=3),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    original_question = question.strip()
    lowered_question = original_question.lower()

    query = get_ticket_query(db, current_user)

    if "status of ticket" in lowered_question:
        ticket_id = extract_first_number(lowered_question)

        if ticket_id is None:
            raise HTTPException(status_code=400, detail="Ticket id not found in question")

        ticket = query.filter(models.Ticket.id == ticket_id).first()

        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        return {
            "question": original_question,
            "answer": f"Ticket {ticket.id} is currently {ticket.status}."
        }

    if "summarize ticket" in lowered_question or "summary of ticket" in lowered_question:
        ticket_id = extract_first_number(lowered_question)

        if ticket_id is None:
            raise HTTPException(status_code=400, detail="Ticket id not found in question")

        ticket = query.filter(models.Ticket.id == ticket_id).first()

        if ticket is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        summary = (
            f"Ticket {ticket.id} has title '{ticket.title}'. "
            f"It belongs to category '{ticket.category}', "
            f"has priority '{ticket.priority}', "
            f"and its current status is '{ticket.status}'. "
            f"Description: {ticket.description}"
        )

        return {
            "question": original_question,
            "answer": summary
        }

    if "open tickets" in lowered_question:
        tickets = query.filter(models.Ticket.status == "open").all()

        if not tickets:
            return {
                "question": original_question,
                "answer": "No open tickets were found."
            }

        lines = []
        for ticket in tickets:
            lines.append(
                f"Ticket {ticket.id}: {ticket.title} | priority={ticket.priority} | category={ticket.category}"
            )

        return {
            "question": original_question,
            "answer": "Open tickets:\n" + "\n".join(lines)
        }

    if "closed tickets" in lowered_question:
        tickets = query.filter(models.Ticket.status == "closed").all()

        if not tickets:
            return {
                "question": original_question,
                "answer": "No closed tickets were found."
            }

        lines = []
        for ticket in tickets:
            lines.append(
                f"Ticket {ticket.id}: {ticket.title} | priority={ticket.priority} | category={ticket.category}"
            )

        return {
            "question": original_question,
            "answer": "Closed tickets:\n" + "\n".join(lines)
        }

    if "high priority" in lowered_question:
        tickets = query.filter(models.Ticket.priority == "high").all()

        if not tickets:
            return {
                "question": original_question,
                "answer": "No high priority tickets were found."
            }

        lines = []
        for ticket in tickets:
            lines.append(
                f"Ticket {ticket.id}: {ticket.title} | status={ticket.status} | category={ticket.category}"
            )

        return {
            "question": original_question,
            "answer": "High priority tickets:\n" + "\n".join(lines)
        }

    if "created by user" in lowered_question:
        user_id = extract_first_number(lowered_question)

        if user_id is None:
            raise HTTPException(status_code=400, detail="User id not found in question")

        tickets = query.filter(models.Ticket.created_by == user_id).all()

        if not tickets:
            return {
                "question": original_question,
                "answer": f"No tickets were found for user {user_id}."
            }

        lines = []
        for ticket in tickets:
            lines.append(
                f"Ticket {ticket.id}: {ticket.title} | status={ticket.status} | priority={ticket.priority}"
            )

        return {
            "question": original_question,
            "answer": f"Tickets created by user {user_id}:\n" + "\n".join(lines)
        }

    matched_tickets = query.filter(
        or_(
            models.Ticket.title.ilike(f"%{original_question}%"),
            models.Ticket.description.ilike(f"%{original_question}%"),
            models.Ticket.status.ilike(f"%{original_question}%"),
            models.Ticket.priority.ilike(f"%{original_question}%"),
            models.Ticket.category.ilike(f"%{original_question}%")
        )
    ).all()

    if matched_tickets:
        lines = []
        for ticket in matched_tickets:
            lines.append(
                f"Ticket {ticket.id}: {ticket.title} | status={ticket.status} | priority={ticket.priority}"
            )

        return {
            "question": original_question,
            "answer": "Related tickets found:\n" + "\n".join(lines)
        }

    return {
        "question": original_question,
        "answer": (
            "I could not understand the request clearly. "
            "Try questions like: "
            "What is the status of ticket 1, "
            "Show all open tickets, "
            "Summarize ticket 2, "
            "or Which tickets were created by user 5."
        )
    }