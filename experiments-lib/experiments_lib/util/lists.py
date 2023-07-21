from itertools import chain
from itertools import zip_longest


def lmap(map_func, list_):
    return list(map(map_func, list_))


def lfilter(filter_func, list_):
    return list(filter(filter_func, list_))


def flatmap(map_func, list_):
    return list(chain.from_iterable(map(map_func, list_)))


def flatten(list_):
    return flatmap(lambda x: x, list_)


def flatten_rec(list_):
    if list_ == []:
        return list_
    if isinstance(list_[0], list):
        return flatten_rec(list_[0]) + flatten_rec(list_[1:])
    return list_[:1] + flatten_rec(list_[1:])


def lreversed(list_):
    return list(reversed(list_))


def lforeach(foreach_func, list_):
    for i in list_:
        foreach_func(i)


def lzip(*args, **kwargs):
    return list(zip(*args, *kwargs))


def lenumerate(list_):
    return list(enumerate(list_))


def first(iterable):
    return next(iter(iterable), None)


def last(iterable):
    return first(reversed(iterable))


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def find_slice(seq, subseq):
    n = len(seq)
    m = len(subseq)
    for i in range(n - m + 1):
        if seq[i : i + m] == subseq:
            yield i
