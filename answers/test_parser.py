import json
import typing
import dataclasses
import enum


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


class TraverseDirection(enum.Enum):
    UP = enum.auto()
    DOWN = enum.auto()

def traverse_find_downwards_str_node(
    node: JsonNodeParentType,
    predicate: typing.Callable[[JsonNodeStr], bool]
) -> typing.Optional[JsonNodeStr]:
    iterator = iter(node.data.values() if isinstance(node, JsonNodeDict) else node.data)
    for child_node in iterator:
        if isinstance(child_node, JsonNodeParentType):
            found_node = traverse_find_downwards_str_node(child_node, predicate)
            if found_node is not None:
                return found_node
        elif isinstance(child_node, JsonNodeStr):
            if predicate(child_node):
                return child_node
    return None


def traverse_find_all_downwards_str_node(
    node: JsonNodeParentType,
    predicate: typing.Callable[[JsonNodeStr], bool],
    found_nodes: list[JsonNodeStr]
):
    iterator = iter(node.data.values() if isinstance(node, JsonNodeDict) else node.data)
    for child_node in iterator:
        if isinstance(child_node, JsonNodeParentType):
            found_node = traverse_find_all_downwards_str_node(child_node, predicate, found_nodes)
            if found_node is not None:
                found_nodes.append(found_node)
        elif isinstance(child_node, JsonNodeStr):
            if predicate(child_node):
                found_nodes.append(child_node)

# @dataclasses.dataclass(slots=True, frozen=True)
# class JsonNodeChildIndexDict:
#     value: str

# @dataclasses.dataclass(slots=True, frozen=True)
# class JsonNodeChildIndexArray:
#     value: int

# JsonNodeChildIndex = typing.Union[JsonNodeChildIndexDict, JsonNodeChildIndexArray]

# def get_child_index(parent: JsonNodeParentType, child: JsonNodeType) -> JsonNodeChildIndex:
#     if isinstance(parent, JsonNodeDict):
#         for k, v in parent.data.items():
#             if v is child:
#                 return JsonNodeChildIndexDict(k)
#         assert False
#     else:
#         for i, v in enumerate(parent.data):
#             if v is child:
#                 return JsonNodeChildIndexArray(i)
#         assert False

# def path_to_root(child: JsonNodeStr):
#     child_index_parent_pairs: list[tuple[JsonNodeChildIndex, JsonNodeParentType]] = []

#     current_child: JsonNodeType = child
#     current_parent = child.parent
#     while current_parent is not None:
#         child_index_parent_pairs.append((get_child_index(current_parent, current_child), current_parent))
#         current_child = current_parent
#         current_parent = current_parent.parent
#     return child_index_parent_pairs

# @dataclasses.dataclass(slots=True, frozen=True)
# class CommonParentAndPaths:
#     first_child_indexes: tuple[JsonNodeChildIndex, ...]
#     second_child_indexes: tuple[JsonNodeChildIndex, ...]
#     common_parent: JsonNodeParentType


# def find_common_parent_and_paths_to_parent(first: JsonNodeStr, second: JsonNodeStr):
#     first_path = path_to_root(first)
#     second_path = path_to_root(second)
#     for first_index, (_, first_parent) in enumerate(first_path):
#         for second_index, (_, second_parent) in enumerate(second_path):
#             if first_parent is second_parent:
#                 first_child_indexes = tuple(child_index for child_index, _ in first_path[:first_index + 1])
#                 second_child_indexes = tuple(child_index for child_index, _ in second_path[:second_index + 1])
#                 return CommonParentAndPaths(first_child_indexes, second_child_indexes, first_parent)
#     assert False

STATUS_CORRECT = 'status correct'
STATUS_INCORRECT = 'status incorrect'
CHECK = 'Check'
UNCHECK = 'Uncheck'

def main():
    with open('answers.txt', 'w') as output_file:
        for test_index in range(1, 14):
            output_file.write(f'📝Тест {test_index}\n')
            with open(f'test_{test_index}.json') as file:
                root_element = typing.cast(JsonElementDict, json.load(file))
            
            root_node = JsonNodeDict(None)
            build_tree(JsonNodeElementPairDict(root_node, root_element))

            for question_index in range(1, 11):
                question_name = f'Question {question_index}'
                question_node = traverse_find_downwards_str_node(root_node, lambda x: x.data == question_name)
                assert question_node is not None
                assert question_node.parent is not None
                status = traverse_find_downwards_str_node(
                    question_node.parent,
                    lambda x: x.data == STATUS_CORRECT or x.data == STATUS_INCORRECT
                )
                assert status is not None


                output_file.write('✅' if status.data == STATUS_CORRECT else '❌')
                output_file.write(' ')
                output_file.write(question_name)
                output_file.write('\n')


                answers_checkboxes: list[JsonNodeStr] = []
                traverse_find_all_downwards_str_node(
                    question_node.parent,
                    lambda x: x.data == CHECK or x.data == UNCHECK,
                    answers_checkboxes
                )
                # assert len(answers_checkboxes) == 5
                for answer_checkbox in answers_checkboxes:
                    output_file.write('\t')
                    output_file.write('📌' if answer_checkbox.data == UNCHECK else '')
                    
                    assert answer_checkbox.parent is not None
                    assert answer_checkbox.parent.parent is not None
                    assert isinstance(answer_checkbox.parent.parent, JsonNodeDict)
                    answer_node = answer_checkbox.parent.parent.data['name']
                    assert isinstance(answer_node, JsonNodeStr)

                    output_file.write(answer_node.data)
                    output_file.write('\n')
                output_file.write('\n')

if __name__ == '__main__':
    main()