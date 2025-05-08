# Protobuf Decoder Library

This library provides a simple Protobuf decoder that can convert Protobuf messages from bytes or a hex string into a Python dictionary. It also supports encoding the dictionary back to Protobuf bytes or a hex string.

## Features

- Decode Protobuf messages from raw bytes or a hex string.
- Output decoded fields as a structured dictionary.
- Output decoded fields in a JSON-friendly format.
- Encode a dictionary of fields back into Protobuf message (bytes or hex string).
- Supports VARINT, I64 (64-bit), LEN (length-delimited), and I32 (32-bit) wire types.

## Installation

To use this library, you can include the `protobuf_decoder` directory in your project or install it using pip install proto-decoder.

## Usage

```python
from protobuf_decoder import ProtobufDecoder

# Initialize the decoder
decoder = ProtobufDecoder()

# Example hex data (replace with your actual Protobuf hex string)
hex_data = "089601"

# Decode the hex data
decoded_fields = decoder.decode(hex_data)
print("Decoded fields dict:", decoded_fields)

# Decode to JSON-friendly format
decoded_json = decoder.decode_json(hex_data)
print("Decoded JSON:", decoded_json)

# Example of encoding
fields_to_encode = {
    0: {"wire": 0, "field": 1, "value": 150}
}
encoded_data_hex = decoder.encode(fields_to_encode, output_hex=True)
print("Re-encoded data (hex):", encoded_data_hex)

encoded_data_bytes = decoder.encode(fields_to_encode, output_hex=False)
print("Re-encoded data (bytes):", encoded_data_bytes)
```

This will output:
```
Decoded fields dict: {0: {'wire': 0, 'field': 1, 'value': 150}}
Decoded JSON: {1: 150}
Re-encoded data (hex): 089601
Re-encoded data (bytes): b'\x08\x96\x01'
```

