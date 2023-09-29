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


s = 0
for colour in range(256):
    if s > 16:
        s = 0
        print()
    print(f"\x1b[38;5;{colour}m\u25a0\x1b[0m", end="")
    s += 1
