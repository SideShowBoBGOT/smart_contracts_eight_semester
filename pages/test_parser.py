import json
import typing
import dataclasses


JsonElementDict = dict[str, 'JsonElementType']

JsonElementType: typing.TypeAlias = typing.Union[
    JsonElementDict,
    list['JsonElementType'],
    str,
    int,
    float,
    bool,
    None
]

JsonElementParantType = typing.Union[
    dict[str, 'JsonElementType'],
    list['JsonElementType'],
]

JsonNodeParentType = typing.Union[
    'JsonNodeDict',
    'JsonNodeList'
]

JsonNodeType = typing.Union[
    'JsonNodeDict',
    'JsonNodeList',
    'JsonNodeStr',
    'JsonNodeInt',
    'JsonNodeFloat',
    'JsonNodeBool',
    'JsonNodeNone',
]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeDict:
    parent: typing.Optional[JsonNodeParentType]
    data: dict[str, JsonNodeType] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeList:
    parent: typing.Optional[JsonNodeParentType]
    data: list[JsonNodeType] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeStr:
    data: str
    parent: typing.Optional[JsonNodeParentType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeInt:
    data: int
    parent: typing.Optional[JsonNodeParentType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeFloat:
    data: float
    parent: typing.Optional[JsonNodeParentType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeBool:
    data: bool
    parent: typing.Optional[JsonNodeParentType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeNone:
    parent: typing.Optional[JsonNodeParentType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeElementPairDict:
    node: JsonNodeDict
    element: dict[str, JsonElementType]

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeElementPairList:
    node: JsonNodeList
    element: list[JsonElementType]

JsonNodeElementPair = typing.Union[
    JsonNodeElementPairDict,
    JsonNodeElementPairList
]

def match_build_tree(parent: JsonNodeParentType, el: JsonElementType) -> JsonNodeType:
    if el is None:
        node = JsonNodeNone(parent)
    elif isinstance(el, dict):
        node = JsonNodeDict(parent)
        build_tree(JsonNodeElementPairDict(node, el))
    elif isinstance(el, list):
        node = JsonNodeList(parent)
        build_tree(JsonNodeElementPairList(node, el))
    elif isinstance(el, str):
        node = JsonNodeStr(el, parent)
    elif isinstance(el, int):
        if isinstance(el, bool):
            node = JsonNodeBool(el, parent)
        else:
            node = JsonNodeInt(el, parent)
    else:
        node = JsonNodeFloat(el, parent)
    return node

def build_tree(json_node_element_pair: JsonNodeElementPair):
    if isinstance(json_node_element_pair, JsonNodeElementPairDict):
        for k, el in json_node_element_pair.element.items():
            json_node_element_pair.node.data.setdefault(k, match_build_tree(json_node_element_pair.node, el))
    else:
        for el in json_node_element_pair.element:
            json_node_element_pair.node.data.append(match_build_tree(json_node_element_pair.node, el))

# def traverse_recurse(data: JsonElementType):
#     if data is None:
#         pass
#     elif isinstance(data, dict):
#         for k, el in data.items():
#             # print(k)
#             traverse_recurse(el)
#     elif isinstance(data, list):
#         for el in data:
#             traverse_recurse(el)
#     elif isinstance(data, str):
#         pass
#     elif isinstance(data, int):
#         if isinstance(data, bool):
#             pass
#         pass
#     else:
#         pass

def main():
    with open('test_1.json') as file:
        root_element = typing.cast(JsonElementDict, json.load(file))
    root_node = JsonNodeDict(None)
    build_tree(JsonNodeElementPairDict(root_node, root_element))

    print(root_node)

if __name__ == '__main__':
    main()