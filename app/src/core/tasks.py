from celery import shared_task
from src.casper import services
import asyncio


@shared_task()
def monitoring():
    asyncio.run(services.main())
