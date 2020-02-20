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