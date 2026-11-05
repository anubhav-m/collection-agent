from app.llm.key_pool import KeyPool
from app.llm.quota import is_daily_quota, quota_ids
from tests.helpers import DAILY, PER_MINUTE, api_error


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_quota_kind_is_read_from_the_error():
    assert is_daily_quota(api_error(429, quota_id=DAILY))
    assert not is_daily_quota(api_error(429, quota_id=PER_MINUTE))
    assert not is_daily_quota(api_error(429))
    assert quota_ids(api_error(429, "5s", DAILY)) == [DAILY]


def test_daily_limit_retires_a_key_for_good():
    pool = KeyPool(["k1", "k2", "k3"], Clock())
    assert pool.on_rate_limit(api_error(429, quota_id=DAILY)) and pool.slot == 2
    assert pool.on_rate_limit(api_error(429, quota_id=DAILY)) and pool.slot == 3
    assert pool.on_rate_limit(api_error(429, quota_id=DAILY)) is False
    assert pool.all_exhausted


def test_per_minute_limit_returns_to_the_earlier_key_after_it_rests():
    clock = Clock()
    pool = KeyPool(["k1", "k2", "k3"], clock)
    assert pool.on_rate_limit(api_error(429, quota_id=DAILY)) and pool.slot == 2
    assert pool.on_rate_limit(api_error(429, "30s", PER_MINUTE)) and pool.slot == 3
    clock.now += 31  # key 2's per-minute limit has passed; key 1 stays retired
    assert pool.on_rate_limit(api_error(429, quota_id=DAILY)) and pool.slot == 2
    assert not pool.all_exhausted


def test_all_live_keys_resting_means_wait_on_the_soonest():
    clock = Clock()
    pool = KeyPool(["k1", "k2"], clock)
    assert pool.on_rate_limit(api_error(429, "50s", PER_MINUTE)) and pool.slot == 2
    assert pool.on_rate_limit(api_error(429, "10s", PER_MINUTE)) is False
    assert pool.slot == 2 and not pool.all_exhausted  # key 2 recovers first
