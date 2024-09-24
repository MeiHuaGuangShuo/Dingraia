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


def markdown_color_formatter(text, color_map: dict) -> str:
    for k, v in color_map.items():
        if not isinstance(v, str):
            raise ValueError(f"Value of {k} should be a string, but got {type(v)}")
        if v.startswith("#"):
            if len(v) != 7:
                raise ValueError(f"Invalid color code: {v}")
        else:
            v = "#" + v.lstrip("#")
            if len(v) != 7:
                raise ValueError(f"Invalid color code: {v}")
        color_map[k] = v
    color_map = dict(sorted(color_map.items(), key=lambda x: x[0]))
    for k, v in color_map.items():
        if text < k:
            text = f'<font color="{v}">{text}</font>'
            break
    return text
