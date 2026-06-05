from sqlmodel import Field, SQLModel

class ContactMessage(SQLModel, table=True):
    __tablename__ = "ContactMessages"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str