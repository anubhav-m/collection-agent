"""One code check's outcome."""

from pydantic import BaseModel


class CheckResult(BaseModel):
    name: str
    passed: bool
    detail: str = ""


def check(name: str, passed: bool, detail: str = "") -> CheckResult:
    return CheckResult(name=name, passed=passed, detail="" if passed else detail)
