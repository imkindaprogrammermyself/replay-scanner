import json
import zlib
import struct
from Crypto.Cipher import Blowfish
from io import BytesIO
from utils import LOGGER

WOWS_BLOWFISH_KEY = b')\xb7\xc9\t8?\x84\x88\xfa\x98\xecN\x13\x19y\xfb'
BLOWFISH = Blowfish.new(WOWS_BLOWFISH_KEY, Blowfish.MODE_ECB)


class ReplayReader:
    def __init__(self):
        self._replay_header = b''
        self._replay_block_count = 0
        self._replay_block_size = 0
        self._replay_json_data = dict()
        self._unused = b''

    def read_replay(self, replay_path: str) -> bytes:
        with open(replay_path, 'rb') as reader:
            self._replay_header = reader.read(4)
            self._replay_block_count, = struct.unpack("i", reader.read(4))
            self._replay_block_size, = struct.unpack("i", reader.read(4))
            self._replay_json_data = json.loads(reader.read(self._replay_block_size))

            LOGGER.info(f"Replay header: {self._replay_header}")
            LOGGER.info(f"Replay block count: {self._replay_block_count}")
            LOGGER.info(f"Replay block size: {self._replay_block_size}")
            LOGGER.info(f"Replay json data: {str(self._replay_json_data)[:16]}...")

            extra_data = []
            for i in range(self._replay_block_count - 1):
                block_size, = struct.unpack("i", reader.read(4))
                data = json.loads(reader.read(block_size))
                extra_data.append(data)

            if extra_data:
                LOGGER.info("Replay extra data found...")

            LOGGER.info("Reading encrypted data...")
            data_encrypted = reader.read()
            LOGGER.info(f"Encrypted data size: {len(data_encrypted)}")
            LOGGER.info("Decrypting compressed data...")
            data_decrypted_compressed, self._unused = self._decrypt_data(data_encrypted)
            LOGGER.info(f"Decrypted compressed data size: {len(data_decrypted_compressed)}")
            LOGGER.info(f"Decompressing decrypted data...")
            data_decrypted_decompressed = zlib.decompress(data_decrypted_compressed)
            LOGGER.info(f"Decompressed data size: {len(data_decrypted_decompressed)}")
            compressed_per = (1 - (len(data_decrypted_compressed) / len(data_decrypted_decompressed))) * 100
            LOGGER.info(f"Data was compressed by {round(compressed_per, 2)}%")

            return data_decrypted_decompressed

    @staticmethod
    def _chunk_data(string, length=8):
        for i in range(0, len(string), length):
            yield i, string[0 + i:length + i]

    def _decrypt_data(self, dirty_data):
        previous_block = b''
        decrypted_data = BytesIO()
        unused = b''

        for index, chunk in self._chunk_data(dirty_data):
            if index == 0:
                unused = chunk
                continue

            decrypted_block, = struct.unpack('q', BLOWFISH.decrypt(chunk))
            if previous_block:
                decrypted_block ^= previous_block
            previous_block = decrypted_block
            decrypted_data.write(struct.pack('q', decrypted_block))

        return decrypted_data.getvalue(), unused