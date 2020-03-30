import sys
from io import BytesIO
from lxml import objectify
import xml.etree.ElementTree as ET

BLOCK_SIZE = 90
START_TYPE_COUNTER_1 = 3.0
START_TYPE_COUNTER_2 = 0
TYPE_COUNTER_1_INCREASE = 0.1
TYPE_COUNTER_2_INCREASE = 1
TYPE_FORMAT = "a.{}_key{}"


def create_xml(decimal_blocks):
    type_counter_1 = START_TYPE_COUNTER_1
    type_counter_2 = START_TYPE_COUNTER_2
    root = ET.Element("root")
    data = ET.SubElement(root, "Data")
    event = ET.SubElement(data, "Event")
    conditions = ET.SubElement(event, "Conditions")
    condition = ET.SubElement(conditions, "Condition")

    for decimal_block in decimal_blocks:
        field = ET.SubElement(condition, "Field")
        ET.SubElement(field, "Type").text = TYPE_FORMAT.format("%.1f" % float(type_counter_1),
                                                               type_counter_2)
        ET.SubElement(field, "Value").text = decimal_block

        type_counter_1 += TYPE_COUNTER_1_INCREASE
        type_counter_2 += TYPE_COUNTER_2_INCREASE

    # tree = ET.ElementTree(root)
    # tree.write("filename.xml")
    return ET.tostring(root, encoding='unicode')


def split_message_by_blocks(decimal_message):
    decimal_message = str(decimal_message)
    start_index = 0
    end_index = BLOCK_SIZE
    while True:
        splitted_message = decimal_message[start_index:end_index]

        if not splitted_message:
            break

        yield splitted_message

        start_index = end_index
        end_index += BLOCK_SIZE


def convert_bytes_to_decimal(bytes_message: bytes) -> int:
    return int.from_bytes(bytes_message, byteorder=sys.byteorder)


def convert_decimal_to_bytes(decimal_message: int) -> bytes:
    return decimal_message.to_bytes((decimal_message.bit_length() + 7) // 8, byteorder=sys.byteorder)


class Encoder:
    def encode_message(self, message: BytesIO) -> str:
        message_in_decimal = convert_bytes_to_decimal(message.read())
        decimal_blocks = split_message_by_blocks(message_in_decimal)
        return create_xml(decimal_blocks)

    def decode_message(self, encoded_message: str) -> BytesIO:
        root = objectify.fromstring(encoded_message)
        total_text = ""
        for field in root.Data.Event.Conditions.Condition.Field:
            total_text += field.Value.text
        return BytesIO(convert_decimal_to_bytes(int(total_text)))


after_encode = Encoder().encode_message(BytesIO(b'hello world'))
after_decode = Encoder().decode_message(after_encode)
print(after_decode.read())

