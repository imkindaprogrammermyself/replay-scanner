from replay_reader import ReplayReader

MODULES = [b'cnt\n', b'ccommands\n', b'cwebbrowser\n', b'c__builtin__\nexec', b'c__builtin__\neval',
           b'c__builtin__\nexecfile']


class ReplayScanner:
    def __init__(self):
        pass

    @staticmethod
    def scan(data: bytes, prohibited_modules: list[bytes]) -> list[tuple[bool, bytes]]:
        result: list[tuple[bool, bytes]] = []
        position = 0
        while position + 1 != len(data):
            for module in prohibited_modules:
                if data[position:position + len(module)] == module:
                    result.append((True, module))
            position += 1
        return result


if __name__ == '__main__':
    import time
    rr = ReplayReader()
    rs = ReplayScanner()
    replay_data = rr.read_replay("replays/infected.wowsreplay")

    start = time.perf_counter()
    scan_result = rs.scan(replay_data, MODULES)
    end = time.perf_counter()
    print(end-start)
    print(scan_result)
