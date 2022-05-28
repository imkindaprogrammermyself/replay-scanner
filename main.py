import struct
import logging
from io import BytesIO
from typing import Callable

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
LOGGER = logging.getLogger("pickle-condom")


def op_proto(io: BytesIO):
    protocol_ver, = struct.unpack('B', io.read(1))
    LOGGER.info(f"PROTOCOL {protocol_ver}")


def op_empty_list(io: BytesIO):
    LOGGER.info("EMPTY LIST")


def op_binput(io: BytesIO):
    LOGGER.info(f"BINPUT {io.read(1)}")


def op_mark(io: BytesIO):
    LOGGER.info("MARK")


def op_binint1(io: BytesIO):
    val, = struct.unpack('B', io.read(1))
    LOGGER.info(f"BININT1 {val}")


def op_binint(io: BytesIO):
    val, = struct.unpack('i', io.read(4))
    LOGGER.info(f"BININT {val}")


def op_tuple1(io: BytesIO):
    LOGGER.info("TUPLE1")


def op_tuple2(io: BytesIO):
    LOGGER.info("TUPLE2")


def op_newtrue(io: BytesIO):
    LOGGER.info("NEWTRUE")


def op_empty_tuple(io: BytesIO):
    LOGGER.info("EMPTY TUPLE")


def op_new_obj(io: BytesIO):
    LOGGER.info("NEWOBJ")


def op_bin_unicode(io: BytesIO):
    size, = struct.unpack('I', io.read(4))
    LOGGER.info(f"BINUNICODE {io.read(size)}")


def op_long1(io: BytesIO):
    size, = struct.unpack('B', io.read(1))
    val = int.from_bytes(io.read(size), 'little')
    LOGGER.info(f"LONG1 {val}")


def op_appends(io: BytesIO):
    LOGGER.info("APPENDS")


def op_newfalse(io: BytesIO):
    LOGGER.info("NEWFALSE")


def op_binint2(io: BytesIO):
    val, = struct.unpack('H', io.read(2))
    LOGGER.info(f"BININT2 {val}")


def op_append(io: BytesIO):
    LOGGER.info("APPEND")


def op_build(io: BytesIO):
    LOGGER.info("BUILD")


def op_empty_dict(io: BytesIO):
    LOGGER.info("EMPTY DICT")


def op_reduce(io: BytesIO):
    LOGGER.info("REDUCE")


def op_set_items(io: BytesIO):
    LOGGER.info("REDUCE")


def op_stop(io: BytesIO):
    LOGGER.info("STOP")


def op_binget(io: BytesIO):
    val = int.from_bytes(io.read(1), 'little')
    LOGGER.info(f"BINGET {val}")


def op_long_binput(io: BytesIO):
    val = int.from_bytes(io.read(4), 'little')
    LOGGER.info(f"LONG_BINPUT {val}")


def op_long_binget(io: BytesIO):
    val = int.from_bytes(io.read(4), 'little')
    LOGGER.info(f"LONG_BINGET {val}")


def op_none(io: BytesIO):
    LOGGER.info("NONE")


def op_setitem(io: BytesIO):
    LOGGER.info("SETITEM")


def op_global(io: BytesIO):  # global (loads modules)
    module_name = io.readline().replace(b'\n', b'').decode('latin1')
    obj_name = io.readline().replace(b'\n', b'').decode('latin1')
    LOGGER.info(f"GLOBAL {module_name}, {obj_name}")


oc_mapping: dict[bytes, Callable[[BytesIO, ], None]] = {
    b'(': op_mark,
    b')': op_empty_tuple,
    b'.': op_stop,
    b'J': op_binint,
    b'K': op_binint1,
    b'M': op_binint2,
    b'N': op_none,
    b'R': op_reduce,
    b'X': op_bin_unicode,
    b']': op_empty_list,
    b'a': op_append,
    b'b': op_build,
    b'c': op_global,  # global (loads modules)
    b'e': op_appends,
    b'h': op_binget,
    b'j': op_long_binget,
    b'q': op_binput,
    b'r': op_long_binput,
    b's': op_setitem,
    b'u': op_set_items,
    b'}': op_empty_dict,
    b'\x80': op_proto,
    b'\x81': op_new_obj,
    b'\x85': op_tuple1,
    b'\x86': op_tuple2,
    b'\x88': op_newtrue,
    b'\x89': op_newfalse,
    b'\x8a': op_long1
}

if __name__ == '__main__':
    with open("sample.dat", "rb") as f:  # playerState with payload
        data = f.read()

    # data = pickle.dumps([], protocol=2)

    with BytesIO(data) as reader:
        while reader.tell() != len(reader.getvalue()):
            oc = reader.read(1)
            oc_mapping[oc](reader)
