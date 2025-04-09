import os
from typing import List, Dict, Any
from pathlib import Path
import json

######################################################################################
# CSV files curated by Ken Mandl assisted by ChatGPT. Each sheet is a CSV file.
#
# "ARPA-H Rare Disease Prioritization via ChatGPT with GIC counts"
# https://docs.google.com/spreadsheets/d/1lNgKOyt1cK_cTA72WbywsjjrvWCM0HUpv1nMFqKEngM
#
#####################################################################################
CSV_LIST = ["UNIQUE_LT10_PER_100K.csv",
            "UNIQUE_LT50_PER_100K.csv",
            "BROAD_LT10_PER_100K.csv",
            "BROAD_LT50_PER_100K.csv"]

def read_disease_json(filename='disease_names_expanded.json') -> dict:
    return read_json(resource(filename))

def write_disease_json(filename='disease_names.json') -> dict:
    return read_json(resource(filename))

def resource(filename) -> Path:
    return Path(os.path.join(os.path.dirname(__file__), 'resources', filename))

def output(filename) -> Path:
    return Path(os.path.join(os.path.dirname(__file__), 'output', filename))

def list_output(disease) -> List[Path]:
    return [output(f'{disease}.csv'),
            output(f'{disease}.json')]

def rsync_output() -> str:
    """
    :return: rsync command to "sync" uploading to a remote host the local output directory
    """
    return f"rsync -azvrh --progress {output('*.csv.gz')} "

###############################################################################
#
# Read/Write Text
#
###############################################################################
def read_text(text_file: Path | str, encoding: str = 'UTF-8') -> str:
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

def read_bytes(binary_file: str) -> bytes:
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
def read_json(json_file: Path | str, encoding: str = 'UTF-8') -> Dict[Any, Any]:
    """
    Read json from file
    :param json_file: absolute path to file
    :param encoding: provided file's encoding
    :return: json file contents
    """
    if file_exists(json_file):
        with m_open(file=json_file, encoding=encoding) as j_file:
            return json.load(j_file)

def write_json(contents: Dict[Any, Any], json_file_path: Path | str, encoding: str = 'UTF-8') -> Path:
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
