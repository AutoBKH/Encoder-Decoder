import sys
from io import BytesIO
import xml.etree.cElementTree as ET

CHUNK_SIZE = 90
BLOCK_SIZE = 5
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
    condition = ET.SubElement(event, "condition")

    for decimal_block in decimal_blocks:
        field = ET.SubElement(event, "Field")
        ET.SubElement(field, "Type").text = TYPE_FORMAT.format("%.1f" % float(type_counter_1),
                                                               type_counter_2)
        ET.SubElement(field, "Value").text = decimal_block

        type_counter_1 += TYPE_COUNTER_1_INCREASE
        type_counter_2 += TYPE_COUNTER_2_INCREASE

    tree = ET.ElementTree(root)
    tree.write("filename.xml")
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

        start_index += end_index
        end_index += end_index


def split_message_by_chunks(message):
    with message as message_handler:
        while True:
            chunk = message_handler.read(CHUNK_SIZE)
            if not chunk:
                break
            yield chunk


def convert_bytes_to_decimal(bytes_message):
    return int.from_bytes(bytes_message, byteorder=sys.byteorder)


class Encoder:
    def encode_message(self, message: BytesIO) -> str:
        message_in_decimal = convert_bytes_to_decimal(message.read())
        decimal_blocks = split_message_by_blocks(message_in_decimal)
        create_xml(decimal_blocks)

    def decode_message(self, encoded_message: BytesIO):
        pass


Encoder().encode_message(BytesIO(b"llll"))
# import xml.etree.cElementTree as ET
#
# root = ET.Element("root")
# doc = ET.SubElement(root, "doc")
#
# ET.SubElement(doc, "field1", name="blah").text = "some value1"
# ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"
#
# tree = ET.ElementTree(root)
# tree.write("filename.xml")
#
# from xml.etree.ElementTree import Element, SubElement, Comment, tostring
#
# top = Element('top')
#
# comment = Comment('Generated for PyMOTW')
# top.append(comment)
#
# child = SubElement(top, 'child')
# child.text = 'This child contains text.'
#
# child_with_tail = SubElement(top, 'child_with_tail')
# child_with_tail.text = 'This child has regular text.'
# child_with_tail.tail = 'And "tail" text.'
#
# child_with_entity_ref = SubElement(top, 'child_with_entity_ref')
# child_with_entity_ref.text = 'This & that'
#
# print(tostring(top))
