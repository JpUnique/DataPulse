from celery import shared_task
@shared_task
def add_numbers(a: int, b: int) -> int:
    """Simple task to verify Celery worker execution."""
    return a + b