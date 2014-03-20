def first(x, none=None):
    return next(iter(x), none)


def ip_long_to_str(ip):
    ip_bytes = [
        ip & 0xFF,
        (ip >> 8) & 0xFF,
        (ip >> 16) & 0xFF,
        (ip >> 24) & 0xFF
    ]
    return '.'.join(map(str, ip_bytes))


def ip_str_to_long(ip):
    l = 0
    ip = map(int, ip.split('.'))
    for i in range(4):
        l += ip[i] << (8 * (3 - i))
    return l
