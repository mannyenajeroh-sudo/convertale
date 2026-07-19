import uuid

import pytest

from showrunner_api.agents.base import BaseAgent


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.commits = 0

    def add(self, value) -> None:
        self.added.append(value)

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, value) -> None:
        return None


class FailingAgent(BaseAgent):
    async def run(self, input_json):
        raise RuntimeError("forced failure")


@pytest.mark.asyncio
async def test_base_agent_records_error_job_when_run_raises():
    session = FakeSession()
    agent = FailingAgent(db=session)

    with pytest.raises(RuntimeError, match="forced failure"):
        await agent.execute(
            project_id=uuid.uuid4(),
            workspace_id=uuid.uuid4(),
            input_json={"prompt": "test"},
        )

    job = session.added[0]
    assert job.status == "error"
    assert job.error_text == "forced failure"
    assert job.completed_at is not None
    assert session.commits >= 2
