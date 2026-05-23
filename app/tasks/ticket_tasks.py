import asyncio

from app.tasks.celery_app import celery_app


@celery_app.task
def process_ticket(ticket_id: int) -> None:
    asyncio.run(_run_agent(ticket_id))


async def _run_agent(ticket_id: int) -> None:
    from app.services import AgentService
    from app.utils.db_manager import DBManager

    db_manager = DBManager()
    async with db_manager.session() as db:
        service = AgentService(db)
        await service.process_ticket(ticket_id)
