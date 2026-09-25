from app.core.config import settings
from app.services.base_grader import BaseGraderAgent
from app.services.cursor_grader import CursorGraderAgent


def create_grader_agent() -> BaseGraderAgent:
    return CursorGraderAgent(model_name=settings.CURSOR_MODEL)
