import pickle
import struct
import sys

from io import BytesIO
from replay_reader import ReplayReader
from utils import LOGGER

PICKLE_PROTOCOL_2_HEADER = b'\x80\x02'

SAFE_IMPORTS = [("CamouflageInfo", "CamouflageInfo"), ("_codecs", "encode"), ("PlayerModeDef", "PlayerMode"),
                ("collections", "Counter"), ("GameParams", "GPData"), ("GameParams", "TypeInfo"),
                ("Math", "Vector3")]


class ForbiddenImportError(Exception):
    pass


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in SAFE_IMPORTS:
            raise ForbiddenImportError(f"{module},{name}")

        __import__(module, level=0)
        return getattr(sys.modules[module], name)


if __name__ == '__main__':
    data = ReplayReader().read_replay("replays/infected.wowsreplay")

    position = 0
    while position + 1 != len(data):
        if data[position:position + 2] == PICKLE_PROTOCOL_2_HEADER:
            # BLOB (PICKLE WITH SIZE AS START OF THE DATA)
            # IF A HEADER IS FOUND, WE CHECK WHAT'S IN FRONT OF IT. IT COULD BE THE SIZE OF THE WHOLE PICKLE DATA.
            # WE SLICE THE DATA AND TRY-PARSE IT. IF IT FAILS, WE CHECK FOR THE CORRECT SIZE.
            # BLOB W/ PICKLE DATA SIZE < 255 FRAME:
            # SIZE | PICKLE DATA
            # BLOB W/ PICKLE DATA SIZE > 255 FRAME:
            # 1 BYTE SIZE (255) | 2 BYTES (REAL PICKLE DATA SIZE) | 1 BYTE SEPARATOR (\x00) | PICKLE DATA
            # IF IT IS A VALID PICKLE, ANY MODULE IT LOADS WILL BE RESTRICTED TO WHAT A SAFE WORLD OF WARSHIPS REPLAY
            # FILE LOADS.
            # IF IT DETECTS ANY FORBIDDEN IMPORTS THIS WILL RAISE A FORBIDDENIMPORTERROR.

            suspected_size, = struct.unpack('B', data[position - 1].to_bytes(1, 'little'))
            suspected_data = data[position:position + suspected_size]
            try:
                try:
                    RestrictedUnpickler(BytesIO(suspected_data), encoding='bytes').load()
                except (EOFError, ValueError, pickle.UnpicklingError):
                    suspected_size_b, = struct.unpack('H', data[position - 3:position - 1])
                    try:
                        print(RestrictedUnpickler(BytesIO(data[position:position + suspected_size_b])).load())
                    except (EOFError, ValueError, pickle.UnpicklingError):
                        pass
            except ForbiddenImportError as e:
                LOGGER.error(f"Forbidden import detected! {e}")
                break
        position += 1
