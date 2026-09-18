import os
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
from rapid_elastic import config

QUERY_TOPICS_FILE = 'query_topics.json'

def read_query_topics(filename: Path | str) -> dict:
    path = path_query_topics(filename)
    if path.suffix == '.json':
        return read_query_topics_json(path)
    elif path.suffix == '.tsv':
        return read_query_topics_tsv(path)
    else:
        raise ValueError('Unsupported file type', filename)

def read_query_topics_json(filename: Path | str) -> dict:
    return read_json(path_query_topics(filename))

def read_query_topics_tsv(filename: Path | str, col_key='topic', col_value='query') -> dict:
    df = pd.read_csv(filename, sep="\t", on_bad_lines="error")
    return dict(zip(df[col_key], df[col_value]))

def path_query_topics(filename: Path | str = QUERY_TOPICS_FILE) -> Path:
    if isinstance(filename, Path):
        return filename
    else:
        return path_resource(filename)

def path_project() -> Path:
    return Path(Path(__file__).parent)

def path_resource(filename: Path | str) -> Path:
    return path_project() / 'resources' / filename

def path_output(base: str | None = None) -> Path:
    base = base or config.ELASTIC_OUTPUT or "output"
    base = path_project() / base / date_str()
    base.mkdir(parents=True, exist_ok=True)
    return base

def date_str(datetime_obj=None) -> str:
    if not datetime_obj:
        datetime_obj = datetime.now()
    return datetime_obj.strftime("%Y-%m-%d")

###############################################################################
#
# Read/Write Text
#
###############################################################################
def read_text(text_file: Path | str, encoding: str = 'UTF-8') -> str | None:
    """
    Read text from file
    :param text_file: absolute path to file
    :param encoding: provided file's encoding
    :return: file text contents
    """
    if file_exists(text_file):
        with m_open(file=text_file, encoding=encoding) as t_file:
            return t_file.read()


def write_text(contents: str, file_path: Path | str, encoding: str = 'UTF-8') -> Path:
    """
    Write file contents
    :param contents: string contents
    :param file_path: absolute path of target file
    :param encoding: provided file's encoding
    :return: text_file name
    """
    with m_open(file=file_path, mode='w', encoding=encoding) as file_path:
        file_path.write(contents)
        file_path.close()
        return Path(file_path.name)

def write_bytes(data: str, file_path: str) -> None:
    """
    Writes provided bytes to provided file path
    :param data: bytes contents
    :param file_path: absolute path to file
    :return:
    """
    with m_open(file=file_path, mode='wb') as bytes_file:
        bytes_file.write(data.encode('UTF-8'))

def read_bytes(binary_file: str) -> bytes | None:
    """
    Read bytes from binary file
    :param binary_file: absolute path to file
    :return: bytes file contents
    """
    if file_exists(binary_file):
        with m_open(file=binary_file, mode='rb') as bin_file:
            return bytes(bin_file.read())

def file_exists(filename: Path | str) -> bool:
    """
    FAIL FAST if not exists `filename`
    :param filename: check for existance
    :return: BOOL True or raise exception (fail fast)
    """
    target = Path(filename)
    if not target.exists():
        raise Exception('file not found: ' + str(target))
    return True

def m_open(**kwargs):
    """
    Wrapper for built in open with exception handling and logging
    :return: file like object
    """
    try:
        return open(**kwargs)
    except Exception:
        print('m_open raised an exception', exc_info=True)
        raise

###############################################################################
#
# Read/Write JSON
#
###############################################################################
def read_json(json_file: Path | str, encoding: str = 'UTF-8') -> dict:
    """
    Read json from file
    :param json_file: absolute path to file
    :param encoding: provided file's encoding
    :return: json file contents
    """
    if file_exists(json_file):
        with m_open(file=json_file, encoding=encoding) as j_file:
            return json.load(j_file)

def write_json(contents: dict, json_file_path: Path | str, encoding: str = 'UTF-8') -> Path:
    """
    Write JSON to file
    :param contents: json (dict) contents
    :param json_file_path: absolute destination file path
    :param encoding: provided file's encoding
    :return: file name
    """
    directory = os.path.dirname(json_file_path)
    os.makedirs(directory, exist_ok=True)
    with m_open(file=json_file_path, mode='w', encoding=encoding) as json_file_path:
        json.dump(contents, json_file_path, indent=4)
        return Path(json_file_path.name)

