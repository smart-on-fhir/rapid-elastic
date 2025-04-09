def _query(expression) -> dict:
    return {'query': expression}

def _bool(expression) -> dict:
    return {'bool': expression}

def _must(expression) -> dict:
    return {'must': expression}

def _must_not(expression) -> dict:
    return {'must_not': expression}

def _match_phrase(phrase, index='note') -> dict:
    return {"match_phrase": {index: _quote(phrase)}}

def _quote(expression: str) -> str:
    return '"' + expression + '"'

def match_phrase_any(keyword_list) -> str:
    if not isinstance(keyword_list, list):
        keyword_list = [keyword_list]
    out = [f'note:{_quote(keyword)}' for keyword in keyword_list]
    return ' OR '.join(out)

def query_string(expression) -> dict:
    return {"query": {"query_string": {"query": expression}}}

def sort_by(sortable='@timestamp') -> dict:
    return {"sort": [{sortable: {"order": "desc"}}]}

def return_these() -> dict:
    return {'_source': {'includes': INCLUDE_COLS, 'excludes': EXCLUDE_COLS}}
