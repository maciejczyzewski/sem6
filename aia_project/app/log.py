_print = print


def xprint(*args, **kwargs):
    _print("\033[94m" + " ".join(map(str, args)) + "\033[0m", **kwargs)


print = xprint
