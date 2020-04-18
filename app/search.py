from flask import current_app
from typing import TypeVar, Generic, Tuple, List

T = TypeVar('T')

def add_to_index(index: str, obj: Generic[T]) -> None:
    if not current_app.elasticsearch:
        return

    payload = {}
    for field in obj.__searchable__:
        payload[field] = getattr(obj, field)
    current_app.elasticsearch.index(index=index, id=obj.id, body=payload)


def remove_from_index(index: str, obj: Generic[T]) -> None:
    if not current_app.elasticsearch:
        return

    current_app.elasticsearch.delete(index=index, id=obj.id)


def query_index(index: str, query_str: str, page: int, per_page: int) -> Tuple[List[int], int]:
    if not current_app.elasticsearch:
        return [], 0

    search = current_app.elasticsearch.search(
        index=index,
        body={'query': {'multi_match': {'query': query_str, 'fields': ['*']}},
              'from': (page-1)*per_page, 'size': per_page})
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
