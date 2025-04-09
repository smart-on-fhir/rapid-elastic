###############################################################################
#
# KQL is "Kibana Query Language"
#
# Quick start:
#   https://www.elastic.co/guide/en/kibana/current/kuery-query.html
#   https://coralogix.com/blog/42-elasticsearch-query-examples-hands-on-tutorial/
#
###############################################################################
def query_string(expression) -> dict:
    return {"query": {"query_string": {"query": expression}}}

def match_phrase_any(keyword_list) -> str:
    if not isinstance(keyword_list, list):
        keyword_list = [keyword_list]
    out = [f'note:{_quote(keyword)}' for keyword in keyword_list]
    return ' OR '.join(out)

def return_these(include_list: list, exclude_list: list) -> dict:
    if include_list and exclude_list:
        return {'_source': {'includes': include_list, 'excludes': exclude_list}}
    if include_list:
        return {'_source': {'includes': include_list}}
    if exclude_list:
        return {'_source': {'excludes': include_list}}

###############################################################################
# Helper methods, future state (not curently used) for more complex queries
###############################################################################
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

def _sort_by(sortable_field: str) -> dict:
    return {"sort": [{sortable_field: {"order": "desc"}}]}
