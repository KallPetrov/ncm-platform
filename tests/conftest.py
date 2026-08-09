import pytest
from app.core.database import Base, engine

@pytest.fixture(autouse=True, scope="function")
def clean_database():
    """Ensure database is completely clean before each test to prevent cross-test contamination."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
