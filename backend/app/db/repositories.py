"""Wire the Mongo repositories together for the app."""

from pymongo.asynchronous.database import AsyncDatabase

from app.db.accounts import MongoBorrowerRepo
from app.db.conversations import MongoConversationRepo, MongoEventRepo
from app.db.interfaces import Repositories
from app.db.plans import MongoEscalationRepo, MongoPlanRepo


def mongo_repositories(db: AsyncDatabase) -> Repositories:
    return Repositories(
        conversations=MongoConversationRepo(db),
        events=MongoEventRepo(db),
        borrowers=MongoBorrowerRepo(db),
        plans=MongoPlanRepo(db),
        escalations=MongoEscalationRepo(db),
    )
