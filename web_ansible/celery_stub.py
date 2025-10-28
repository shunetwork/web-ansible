"""
Celery stub for testing without Celery installed
"""


def shared_task(*args, **kwargs):
    """Mock shared_task decorator when Celery is not available"""
    def decorator(func):
        return func
    
    if len(args) == 1 and callable(args[0]):
        # @shared_task without parentheses
        return args[0]
    else:
        # @shared_task() with parentheses
        return decorator

