"""Two fictional lenders. Names are invented and not tied to any real company."""

from app.db.models import Lender

LENDERS = [
    Lender(lender_id="LND-001", name="Maple Grove Example Credit"),
    Lender(lender_id="LND-002", name="Riverbend Sample Finance"),
]
