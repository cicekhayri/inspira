from enum import Enum


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PUT = "PUT"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"


SQLALCHEMY_TYPE_MAPPING = {
    "string": "String",
    "boolean": "Boolean",
    "enum": "Enum",
    "integer": "Integer",
    "numeric": "Numeric",
    "float": "Float",
    "date": "Date",
    "datetime": "DateTime",
    "time": "Time",
    "interval": "Interval",
    "text": "Text",
    "unicode": "Unicode",
    "unicodetext": "UnicodeText",
    "largebinary": "LargeBinary",
    "pickletype": "PickleType",
    "json": "JSON",
}
