ERROR = object()

def getDeep(d, *args):
    try:
        target = d
        for arg in args:
            match target:
                case dict():
                    target = target[arg]
                case list():
                    target = target[int(arg)]
                case _:
                    target = getattr(target, arg)
                    
        return target
    except: # NOQA
        return ERROR


def setDeep(d, *args):
    for arg in args[:-2]:
        if arg not in d:
            d[arg] = {}
        d = d[arg]

    d[args[-2]] = args[-1]
    