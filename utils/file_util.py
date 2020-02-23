import os
import re
import uuid
from pathlib import Path


def get_all_cch_files(repo_path: str) -> [Path]:
    repo_p = Path(repo_path)
    cch_file_list = list(repo_p.glob('**/*.cc')) + list(repo_p.glob('**/*.h'))
    return cch_file_list


def generate_random_file_name_with_extension(file_extension: str) -> str:
    return "{}.{}".format(generate_hex_uuid_4(), file_extension)


def generate_hex_uuid_4() -> str:
    """Generate UUID (version 4) in hexadecimal representation.
    :return: hexadecimal representation of version 4 UUID.
    """
    return str(uuid.uuid4().hex)


def is_cch_file(file_path: str):
    if str(file_path).endswith('.cc') or str(file_path).endswith('.h'):
        return True
    else:
        return False


def is_test_file(file_path: str):
    result = False
    if is_cch_file(file_path):
        file_name = os.path.basename(file_path)
        pattern = '.*[Tt]est.*'
        match = re.search(pattern, file_name)
        if match is not None:
            result = True

    return result

