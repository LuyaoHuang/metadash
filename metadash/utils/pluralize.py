def pluralize(singular):
    # FIXME
    if singular.endswith('y'):
        return "{}ies".format(singular[:-1])
    elif singular.endswith('s'):
        return "{}es".format(singular)
    elif singular.endswith('o'):
        return "{}es".format(singular)
    return "{}s".format(singular)