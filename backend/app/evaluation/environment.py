"""Real dependencies for an evaluation run: Gemini without cache, and a scratch database.

Each scenario gets a fresh database: the eval database is dropped and re-seeded first.
"""

import asyncio
from datetime import date

from app.core.settings import PROJECT_ROOT, Settings
from app.db.interfaces import Repositories
from app.db.mongo import MongoDatabase
from app.db.repositories import mongo_repositories
from app.db.seed import seed
from app.evaluation.recorder import RecordingLLM
from app.llm.factory import build_llm
from app.policy.loader import PolicyStore
from app.rag.retriever import PolicyRetriever
from app.rag.startup import build_retriever

# Fixed "today" so plan dates in the scenarios stay valid on every rerun.
EVAL_TODAY = date(2026, 11, 5)
REPORTS_DIR = PROJECT_ROOT / "reports" / "evaluation"
SCENARIOS_DIR = PROJECT_ROOT / "backend" / "data" / "eval_scenarios"


class EvalEnvironment:
    def __init__(self, settings: Settings) -> None:
        self.db_name = f"{settings.mongodb_db}_eval"
        uri = settings.mongodb_uri.get_secret_value()
        self.mongo = MongoDatabase(uri, self.db_name, settings.mongodb_timeout_ms)
        self.policies = PolicyStore.from_directory(settings.lender_policy_dir)
        no_cache = settings.model_copy(update={"llm_cache_enabled": False})
        self.llm = RecordingLLM(build_llm(no_cache))
        self.model = settings.gemini_model
        self._settings = settings
        self.retriever: PolicyRetriever | None = None

    async def start(self) -> None:
        if not await self.mongo.ping():
            raise RuntimeError("MongoDB is not reachable; check MONGODB_URI.")
        self.retriever = await asyncio.to_thread(build_retriever, self._settings, self.policies)
        if self.retriever is None:
            raise RuntimeError("Policy search failed to start; see the log.")

    async def fresh_repos(self) -> Repositories:
        # Guard: only ever drop the dedicated evaluation database.
        if not self.db_name.endswith("_eval"):
            raise RuntimeError("refusing to drop a non-evaluation database")
        await self.mongo.db.client.drop_database(self.db_name)
        await seed(self.mongo.db)
        return mongo_repositories(self.mongo.db)

    async def close(self) -> None:
        await self.mongo.close()
