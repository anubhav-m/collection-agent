from app.db.seed import seed
from tests.db.fake_mongo import FakeDatabase


async def test_first_run_inserts_everything():
    summary = await seed(FakeDatabase())
    assert summary == {
        "lenders": {"inserted": 2, "total": 2},
        "borrowers": {"inserted": 12, "total": 12},
        "accounts": {"inserted": 14, "total": 14},
    }


async def test_second_run_creates_no_duplicates_and_keeps_created_at():
    db = FakeDatabase()
    await seed(db)
    created = db["accounts"].docs[0]["created_at"]
    summary = await seed(db)
    assert all(part["inserted"] == 0 for part in summary.values())
    assert summary["accounts"]["total"] == 14
    assert db["accounts"].docs[0]["created_at"] == created


async def test_indexes_are_created_for_each_collection():
    db = FakeDatabase()
    await seed(db)
    assert all(db[name].indexes for name in ("lenders", "borrowers", "accounts"))
