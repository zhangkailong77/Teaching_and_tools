from sqlalchemy.orm import Session

from app.models.school_config import SchoolConfig


def ensure_school_config(db: Session, school_id: str, school_name: str) -> str:
    """
    Ensure a single school_config row exists and is synced with runtime settings.
    Returns one of: "created", "updated", "unchanged".
    """
    existing = db.query(SchoolConfig).first()
    if existing:
        if existing.school_id == school_id and existing.school_name == school_name:
            return "unchanged"

        existing.school_id = school_id
        existing.school_name = school_name
        db.add(existing)
        db.commit()
        return "updated"

    row = SchoolConfig(school_id=school_id, school_name=school_name)
    db.add(row)
    db.commit()
    return "created"
