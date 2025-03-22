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

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeDict:
    parent: typing.Optional['JsonNodeParentType']
    data: dict[str, 'JsonNodeType'] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeList:
    parent: typing.Optional['JsonNodeParentType']
    data: list['JsonNodeType'] = dataclasses.field(default_factory=list)

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeStr:
    data: str
    parent: typing.Optional['JsonNodeParentType']

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeInt:
    data: int
    parent: typing.Optional['JsonNodeParentType']

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeFloat:
    data: float
    parent: typing.Optional['JsonNodeParentType']

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeBool:
    data: bool
    parent: typing.Optional['JsonNodeParentType']

@dataclasses.dataclass(slots=True, frozen=True)
class JsonNodeNone:
    parent: typing.Optional['JsonNodeParentType']

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

JsonNodeParentType = typing.Union[
    JsonNodeDict,
    JsonNodeList
]

JsonNodeType = typing.Union[
    JsonNodeDict,
    JsonNodeList,
    JsonNodeStr,
    JsonNodeInt,
    JsonNodeFloat,
    JsonNodeBool,
    JsonNodeNone,
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

def traverse_find_downwards_str_node(node: JsonNodeParentType, value: str) -> typing.Optional[JsonNodeStr]:
    iterator = iter(node.data.values() if isinstance(node, JsonNodeDict) else node.data)
    for child_node in iterator:
        if isinstance(child_node, JsonNodeParentType):
            found_node = traverse_find_downwards_str_node(child_node, value)
            if found_node is not None:
                return found_node
        elif isinstance(child_node, JsonNodeStr):
            if child_node.data == value:
                return child_node
    return None

def main():
    with open('test_1.json') as file:
        root_element = typing.cast(JsonElementDict, json.load(file))
    root_node = JsonNodeDict(None)
    build_tree(JsonNodeElementPairDict(root_node, root_element))

    found_node = traverse_find_downwards_str_node(root_node, 'Question 1')

if __name__ == '__main__':
    main()