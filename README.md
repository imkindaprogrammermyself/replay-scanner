
# Replay file scanner  
  
### What it does  
It scans for malicious module imports in a pickled data.
  
### How it does it  
A World of Warships replay file consists of packets. Packets that can contain pickles. Pickle is Python's very own object serialization/deserialization. Basically, an object will be converted into binary data which can be saved, stored, transferred and loaded somewhere else. So why are we here? Pickle isn’t safe. It can execute code, code that can be malicious and we’re here to mitigate that.

  

So how do we search for pickles and check whether it contains malicious codes? Well, we start by decrypting and decompressing the replay file, and after that, we search for the pickles.

  

A replay file can only contain Python pickle protocol 2 (World of Warships runs on Python 2 and its maximum pickle protocol is 2) which has a header `\x80\x02`. The first byte is the opcode `PROTO` and the second byte is its argument which is the protocol version which in this case, version `2`. We search for the header by traversing the whole replay data.

  

A pickle is stored in a `Blob`. Blob is just a pickle which contains the pickle size plus the pickle data. A `Blob` is framed like this:

  

**Pickle size < 255 bytes:**

	Pickle data size (unsigned char) (1 byte) | Pickle data

**Pickle size >= 255 bytes:**

	Pickle data size (can be used to tell if the pickle data size is >= 255) (unsigned char) (1 byte) | Real pickle data size (unsigned short) (2 bytes) | Padding (\x00) (1 byte) | Pickle data

  

We search for the picke data by taking advantage of how `Blob`'s work. While we’re traversing the replay data, we parse slices of it to check if it’s a valid pickle. A valid pickle, once loaded, will try to import any module it wants. To catch any forbidden module loads, we use a custom unpickler which only allows what a safe replay file loads. If any forbidden module is requested to be loaded, it’ll throw an error.