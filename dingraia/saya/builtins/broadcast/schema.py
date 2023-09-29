class ListenerSchema:
    
    def __init__(
            self,
            listening_events: list,
            namespace: str = '',
            inline_dispatchers=None,
            decorators=None,
            priority: int = 16,
            extra_priorities=None
    ):
        if extra_priorities is None:
            extra_priorities = {}
        if decorators is None:
            decorators = []
        if inline_dispatchers is None:
            inline_dispatchers = []
        self.listening_events = listening_events
        self.namespace = namespace
        self.inline_dispatchers = inline_dispatchers
        self.decorators = decorators
        self.priority = priority
        self.extra_priorities = extra_priorities
