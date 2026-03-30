import pytest
from TARS.agent.tools.cron import CronTool
from TARS.cron.service import CronService
from TARS.cron.types import CronJobState, CronSchedule, CronRunRecord

def _make_tool(tmp_path) -> CronTool:
    service = CronService(tmp_path / "cron" / "jobs.json")
    return CronTool(service)

def test_cron_tool_properties(tmp_path):
    tool = _make_tool(tmp_path)
    assert tool.name == "cron"
    desc = tool.description
    assert "Schedule reminders" in desc
    assert "UTC" in desc

    params = tool.parameters
    assert params["type"] == "object"
    assert "action" in params["properties"]
    assert "UTC" in params["properties"]["tz"]["description"]
    assert "UTC" in params["properties"]["at"]["description"]

def test_cron_context(tmp_path):
    tool = _make_tool(tmp_path)
    assert not tool._in_cron_context.get()

    token = tool.set_cron_context(True)
    assert tool._in_cron_context.get()

    tool.reset_cron_context(token)
    assert not tool._in_cron_context.get()

def test_validate_timezone_invalid():
    err = CronTool._validate_timezone("Invalid/Timezone")
    assert err is not None
    assert "unknown timezone" in err

@pytest.mark.asyncio
async def test_execute_unknown_action(tmp_path):
    tool = _make_tool(tmp_path)
    result = await tool.execute(action="unknown")
    assert "Unknown action: unknown" in result

@pytest.mark.asyncio
async def test_execute_add_in_cron_context(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_cron_context(True)
    result = await tool.execute(action="add", message="test", every_seconds=10)
    assert "cannot schedule new jobs" in result

@pytest.mark.asyncio
async def test_execute_list(tmp_path):
    tool = _make_tool(tmp_path)
    result = await tool.execute(action="list")
    assert result == "No scheduled jobs."

@pytest.mark.asyncio
async def test_execute_list_with_jobs(tmp_path):
    # This verifies _format_state and list functionality together indirectly
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    await tool.execute(action="add", message="Test Job", every_seconds=60)

    # Check job list formatting
    result = await tool.execute(action="list")
    assert "Scheduled jobs" in result
    assert "Test Job" in result
    assert "Next run:" in result

@pytest.mark.asyncio
async def test_execute_remove_missing(tmp_path):
    tool = _make_tool(tmp_path)
    result = await tool.execute(action="remove")
    assert "Error: job_id is required" in result

@pytest.mark.asyncio
async def test_execute_remove_not_found(tmp_path):
    tool = _make_tool(tmp_path)
    result = await tool.execute(action="remove", job_id="12345")
    assert "not found" in result

@pytest.mark.asyncio
async def test_add_job_missing_message(tmp_path):
    tool = _make_tool(tmp_path)
    result = tool._add_job("", every_seconds=10, cron_expr=None, tz=None, at=None)
    assert "message is required" in result

@pytest.mark.asyncio
async def test_add_job_missing_context(tmp_path):
    tool = _make_tool(tmp_path)
    result = tool._add_job("test", every_seconds=10, cron_expr=None, tz=None, at=None)
    assert "no session context" in result

@pytest.mark.asyncio
async def test_add_job_tz_without_cron(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=10, cron_expr=None, tz="UTC", at=None)
    assert "tz can only be used with cron_expr" in result

@pytest.mark.asyncio
async def test_add_job_invalid_tz(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=None, cron_expr="* * * * *", tz="Invalid/Tz", at=None)
    assert "unknown timezone" in result

@pytest.mark.asyncio
async def test_add_job_invalid_effective_tz(tmp_path):
    tool = CronTool(CronService(tmp_path / "cron" / "jobs.json"), default_timezone="Invalid/Tz")
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=None, cron_expr="* * * * *", tz=None, at=None)
    assert "unknown timezone" in result

@pytest.mark.asyncio
async def test_add_job_invalid_at_format(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=None, cron_expr=None, tz=None, at="invalid-time")
    assert "invalid ISO datetime format" in result

@pytest.mark.asyncio
async def test_add_job_invalid_default_tz_for_naive_at(tmp_path):
    tool = CronTool(CronService(tmp_path / "cron" / "jobs.json"), default_timezone="Invalid/Tz")
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=None, cron_expr=None, tz=None, at="2026-03-25T08:00:00")
    assert "unknown timezone" in result

@pytest.mark.asyncio
async def test_add_job_missing_schedule(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    result = tool._add_job("test", every_seconds=None, cron_expr=None, tz=None, at=None)
    assert "either every_seconds, cron_expr, or at is required" in result

@pytest.mark.asyncio
async def test_execute_add_success(tmp_path):
    tool = _make_tool(tmp_path)
    tool.set_context("telegram", "chat-1")
    result = await tool.execute(action="add", message="test", every_seconds=10)
    assert "Created job" in result

    # remove the job
    job_id = result.split("id: ")[1].strip(")")
    res_remove = await tool.execute(action="remove", job_id=job_id)
    assert "Removed job" in res_remove

def test_format_state_active_paused_status_and_consecutive_failures(tmp_path):
    tool = _make_tool(tmp_path)

    # Test paused status and failures > 0
    state_paused = CronJobState()
    state_paused.paused = True
    state_paused.consecutive_failures = 3
    schedule = CronSchedule(kind="every", every_ms=1000)

    res_paused = tool._format_state(state_paused, schedule)

    assert "Status: Paused" in res_paused[0]
    assert "Failures: 3" in res_paused[1]

    # Test active status and failures == 0
    state_active = CronJobState()
    state_active.paused = False
    state_active.consecutive_failures = 0

    res_active = tool._format_state(state_active, schedule)

    assert "Status: Active" in res_active[0]
    assert "Failures: 0" in res_active[1]
