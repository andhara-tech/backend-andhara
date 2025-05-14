class SchedulerState:
    _instance = None

    def __new__(cls) -> object:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.success = False
            cls._instance.message = "Not initialized"
        return cls._instance
