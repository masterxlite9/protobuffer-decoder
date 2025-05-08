import struct
import json
from typing import Union, Dict, Any

class ProtobufDecoder:
    def __init__(self):
        pass

    def _hex_to_bytes(self, hex_string: str) -> bytes:
        """Converts a hex string to bytes."""
        try:
            if hex_string.startswith(("0x", "0X")):
                hex_string = hex_string[2:]
            if not hex_string:
                return b''
            if len(hex_string) % 2 != 0:
                raise ValueError("Hex string must have an even number of digits.")
            return bytes.fromhex(hex_string)
        except ValueError as e:
            raise ValueError(f"Invalid hex string: '{hex_string}'. Error: {e}")

    def _decode_varint(self, data: bytes, index: int) -> tuple[int, int]:
        value = 0
        shift = 0
        start_index = index
        while True:
            if index >= len(data):
                raise ValueError(f"Buffer underflow at offset {start_index}")
            byte = data[index]
            index += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                return value, index
            shift += 7
            if shift >= 64:
                raise ValueError(f"Varint too long at offset {start_index}")

    def _encode_varint(self, value: int) -> bytes:
        if not isinstance(value, int):
            raise TypeError(f"Varint must be int, got {type(value)}")
        if value < 0:
            raise ValueError("Varint cannot be negative")
        parts = []
        if value == 0:
            return b'\x00'
        while value > 0:
            byte = value & 0x7F
            value >>= 7
            if value > 0:
                byte |= 0x80
            parts.append(byte)
        return bytes(parts)

    def decode(self, data: Union[bytes, str]) -> Dict[int, Dict[str, Any]]:
        if isinstance(data, str):
            actual_data = self._hex_to_bytes(data)
        elif isinstance(data, bytes):
            actual_data = data
        else:
            raise TypeError("Data must be bytes or hex string")

        decoded_fields: Dict[int, Dict[str, Any]] = {}
        index = 0
        counter = 0

        while index < len(actual_data):
            tag_start = index
            tag, index = self._decode_varint(actual_data, index)
            wire_type = tag & 0x07
            field_num = tag >> 3

            if field_num == 0:
                raise ValueError(f"Invalid field 0 at offset {tag_start}")

            field: Dict[str, Any] = {"wire": wire_type, "field": field_num}

            if wire_type == 0:  # VARINT
                val, index = self._decode_varint(actual_data, index)
                field["value"] = val
            elif wire_type == 1:  # I64
                if index + 8 > len(actual_data):
                    raise ValueError(f"I64 overflow at {index}")
                val = struct.unpack('<Q', actual_data[index:index+8])[0]
                index += 8
                field["value"] = val
            elif wire_type == 2:  # LEN
                len_val, index = self._decode_varint(actual_data, index)
                if index + len_val > len(actual_data):
                    raise ValueError(f"LEN overflow at {index}")
                try:
                    field["value"] = actual_data[index:index+len_val].decode("UTF-8")
                except Exception:
                    field["value"] = actual_data[index:index+len_val].hex()
                index += len_val
            elif wire_type == 5:  # I32
                if index + 4 > len(actual_data):
                    raise ValueError(f"I32 overflow at {index}")
                val = struct.unpack('<I', actual_data[index:index+4])[0]
                index += 4
                field["value"] = val
            else:
                raise ValueError(f"Unsupported wire type {wire_type} at {tag_start}")

            decoded_fields[counter] = field
            counter += 1

        return decoded_fields

    def _convert_value_for_json(self, value: Any, wire_type: int) -> Any:
        if wire_type == 2:  # LEN
            if isinstance(value, bytes):
                try:
                    return value.decode('utf-8')
                except UnicodeDecodeError:
                    return value.hex()
            return str(value)
        elif wire_type in [0, 1, 5]:
            return value
        return value

    def decode_json(self, data: Union[bytes, str]) -> Dict[int, Any]:
        raw_fields = self.decode(data)
        result: Dict[int, Any] = {}

        for field in raw_fields.values():
            field_num = field["field"]
            wire_type = field["wire"]
            value = field["value"]

            processed_value = self._convert_value_for_json(value, wire_type)

            if field_num in result:
                if not isinstance(result[field_num], list):
                    result[field_num] = [result[field_num]]
                result[field_num].append(processed_value)
            else:
                result[field_num] = processed_value

        return result

    def encode(self, decoded_fields: Dict[int, Dict[str, Any]], output_hex: bool = False) -> Union[bytes, str]:
        encoded: list[bytes] = []
        for _, field in decoded_fields.items():
            wire_type = field["wire"]
            field_num = field["field"]
            value = field["value"]

            # Encode tag
            tag = (field_num << 3) | wire_type
            encoded.append(self._encode_varint(tag))

            # Encode value
            if wire_type == 0:  # VARINT
                encoded.append(self._encode_varint(value))
            elif wire_type == 1:  # I64
                encoded.append(struct.pack('<Q', value))
            elif wire_type == 2:  # LEN
                if isinstance(value, str):
                    if all(c in "0123456789abcdefABCDEF" for c in value) and len(value) % 2 == 0:
                        value_bytes = bytes.fromhex(value)
                    else:
                        value_bytes = value.encode('utf-8')
                elif isinstance(value, bytes):
                    value_bytes = value
                else:
                    raise TypeError(f"Invalid LEN type: {type(value)}")
                encoded.append(self._encode_varint(len(value_bytes)))
                encoded.append(value_bytes)
            elif wire_type == 5:  # I32
                encoded.append(struct.pack('<I', value))

        final_data = b''.join(encoded)
        return final_data.hex() if output_hex else final_data

