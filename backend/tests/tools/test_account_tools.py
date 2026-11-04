from app.tools import get_account, get_payment_options
from app.tools.get_account import GetAccountArgs
from app.tools.get_payment_options import PaymentOptionsArgs
from tests.fakes.context import make_ctx


async def test_get_account_lists_only_the_verified_borrowers_accounts():
    ctx = await make_ctx(verified_as="BRW-001")
    outcome = await get_account.run(ctx, GetAccountArgs())
    ids = [a["account_id"] for a in outcome.data["accounts"]]
    assert ids == ["ACC-1001", "ACC-1007"]
    assert outcome.data["accounts"][0]["balance"] == "4200.00"


async def test_another_borrowers_account_is_not_accessible():
    ctx = await make_ctx(verified_as="BRW-001")
    for account_id in ("ACC-1002", "ACC-9999"):
        outcome = await get_account.run(ctx, GetAccountArgs(account_id=account_id))
        # Missing and someone else's look identical, so nothing leaks.
        assert outcome.error == "account_not_accessible"
        assert "accounts" not in outcome.data


async def test_payment_options_come_from_the_lenders_rules():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await get_payment_options.run(ctx, PaymentOptionsArgs(account_id="ACC-1002"))
    data = outcome.data
    assert data["balance"] == "850.50"
    assert [o["installments"] for o in data["options"]] == [1, 3, 6, 12]
    assert data["options"][1]["payments"] == ["283.50", "283.50", "283.50"]
    assert data["first_payment_between"] == ["2026-11-05", "2026-12-05"]


async def test_payment_options_for_someone_elses_account_are_rejected():
    ctx = await make_ctx(verified_as="BRW-002")
    outcome = await get_payment_options.run(ctx, PaymentOptionsArgs(account_id="ACC-1001"))
    assert outcome.error == "account_not_accessible"
