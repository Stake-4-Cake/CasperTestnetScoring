from celery import shared_task
from asgiref.sync import async_to_sync
from src.casper import services
import asyncio


@shared_task()
def monitoring():
    asyncio.run(services.main())
