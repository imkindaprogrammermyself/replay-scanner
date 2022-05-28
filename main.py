from utils import LOGGER
from replay_reader import ReplayReader
from concurrent.futures import ThreadPoolExecutor

search = [b'cnt\n', b'ccommands\n', b'cwebbrowser\n', b'c__builtin__\nexec', b'c__builtin__\neval',
          b'c__builtin__\nexecfile']


def scanner(a):
    _replay_dat, _search_str = a
    _pos = 0
    while _pos + 1 != len(_replay_dat):
        if _replay_dat[_pos:_pos + len(_search_str)] == _search_str:
            return True, _search_str
        _pos += 1
    return False, _search_str


if __name__ == '__main__':
    rr = ReplayReader()
    dat = rr.read_replay("replays/infected.wowsreplay")

    with ThreadPoolExecutor() as tpe:
        for result in tpe.map(scanner, [(dat, s) for s in search]):
            is_infected, infected_by = result
            if is_infected:
                LOGGER.info(f"INFECTED: {is_infected}, INFECTED BY: {infected_by}")