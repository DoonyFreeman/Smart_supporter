import asyncio
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.ticket_tasks.process_ticket")
def process_ticket(ticket_id: int) -> None:
    asyncio.run(_run_agent(ticket_id))


async def _run_agent(ticket_id: int) -> None:
    from app.agent.llm_provider import close_http_client
    from app.services import AgentService
    from app.utils.db_manager import DBManager

    db_manager = DBManager()
    try:
        async with db_manager.session() as db:
            service = AgentService(db)
            await service.process_ticket(ticket_id)
    except Exception:
        logger.exception("process_ticket failed for ticket_id=%s", ticket_id)
        raise
    finally:
        # Each Celery task runs in a fresh asyncio loop. The shared httpx
        # client is bound to that loop, so we must close it before the loop
        # is torn down or the next task gets an "attached to different loop" error.
        await close_http_client()
