def ColoredFormatter(message: str):
    color_map = {
        "red"    : "\033[1;31m",
        "green"  : "\033[1;32m",
        "yellow" : "\033[1;33m",
        "blue"   : "\033[1;34m",
        "magenta": "\033[1;35m",
        "cyan"   : "\033[1;36m",
        "white"  : "\033[1;37m",
        "reset"  : "\033[0m",
    }
    for color in color_map:
        message = message.replace(f"<{color}>", color_map[color])
        message = message.replace(f"</{color}>", color_map["reset"])
    return message


class NoUseClass:
    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, _):
        return self

    def __getitem__(self, item):
        return self

    def __setitem__(self, key, value):
        return self

    def __add__(self, other):
        return self

    def __divmod__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mod__(self, other):
        return self
