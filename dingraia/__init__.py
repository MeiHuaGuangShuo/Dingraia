from dingraia.module import load_modules
from dingraia.lazy import channel, ListenerSchema, LoadComplete


@channel.use(ListenEvent=ListenerSchema(listening_events=[LoadComplete]))
def init():
    load_modules()
