"""Shapes shared by ingestion and retrieval."""

from pydantic import BaseModel, ConfigDict, Field

SHARED_LENDER = "shared"


class PolicyDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    doc_id: str = Field(pattern=r"^POL-[A-Z0-9-]+$")
    title: str = Field(min_length=1, max_length=80)
    # A lender ID such as LND-001, or "shared" for every lender.
    lender_id: str = Field(pattern=r"^(LND-\d{3}|shared)$")
    body: str = Field(min_length=1)


class Chunk(BaseModel):
    model_config = ConfigDict(frozen=True)

    chunk_id: str
    doc_id: str
    title: str
    lender_id: str
    section: str
    text: str


class Hit(BaseModel):
    chunk: Chunk
    score: float


class PolicySource(BaseModel):
    """What the API returns to show where an answer came from."""

    doc_id: str
    title: str
    section: str
    score: float

    @classmethod
    def from_hit(cls, hit: Hit) -> "PolicySource":
        c = hit.chunk
        return cls(doc_id=c.doc_id, title=c.title, section=c.section, score=round(hit.score, 3))
