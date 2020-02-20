import os
import subprocess
from pathlib import Path

from lxml import etree

from utils import file_util, shell_util

NS_MAP = {"src": "http://www.srcML.org/srcML/src"}


def get_logging_calls_xml_of_repo(repo_path: str):
    cch_file_list = file_util.get_all_cch_files(repo_path)
    total_result = []
    for cch_path in cch_file_list:
        logging_stmts = get_logging_stmts_xml_of_file(str(cch_path))
        for call in logging_stmts:
            total_result.append(call)

    return total_result


def get_logging_stmts_xml_of_file(file_path: str):
    print("processing: " + file_path)
    file_expr = get_expr_of_file(file_path)
    result = []
    for expr in file_expr:
        expr_str = b'<root>' + etree.tostring(expr) + b'</root>'
        expr = etree.fromstring(expr_str, etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
        # print(expr)

        if check_logging_existence(expr):
            logging_stmt = etree.tostring(expr)
            result.append(logging_stmt)

    return result


def get_expr_of_file(file_path: str):
    xml_name = file_util.generate_random_file_name_with_extension('xml')
    expr_list = []
    xml_p = None
    try:
        shell_util.run("srcml '{}' -o {}".format(file_path, xml_name))
        xml_p = Path(xml_name)
        xml_bytes = xml_p.read_bytes()
        expr_list = get_expr_of_xml_bytes(xml_bytes)
    finally:
        xml_p.unlink()
        return expr_list


def get_expr_of_xml_bytes(xml_bytes):
    if xml_bytes is not None:
        parser = etree.XMLParser(huge_tree=True)
        xml_object = etree.fromstring(xml_bytes, parser=parser)
        expr_stmt_list = xml_object.xpath('//src:expr_stmt/src:expr', namespaces=NS_MAP)
        return expr_stmt_list
    else:
        return []


def check_logging_existence(expr_xml_obj):
    # print(expr_xml_obj)
    call_xpath_str = '//src:*[1]'
    expr_call_xml = expr_xml_obj.xpath(call_xpath_str, namespaces=NS_MAP)
    operator_xpath_str = '//src:*[2]'
    expr_operator_xml = expr_xml_obj.xpath(operator_xpath_str, namespaces=NS_MAP)
    if_direct_log_call = False
    if_second_operator = True
    for call_item in expr_call_xml:
        # print(etree.tostring(call_item).decode('utf-8'))
        if etree.tostring(call_item).decode('utf-8').startswith('<call'):
            call_xml_obj = etree.fromstring(b'<root>' + etree.tostring(call_item) + b'</root>', etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            name_xpath_str = '//src:*[1]'
            call_name_xml = call_xml_obj.xpath(name_xpath_str, namespaces=NS_MAP)
            for name_item in call_name_xml:
                if "VLOG" in etree.tostring(name_item).decode('utf-8') or "LOG" in etree.tostring(name_item).decode('utf-8'):
                    print(etree.tostring(name_item).decode('utf-8'))
                    if_direct_log_call = True



            # print(etree.tostring(call_item).decode('utf-8'))
            # for operator_item in expr_operator_xml:
            #     # print(etree.tostring(operator_item).decode('utf-8'))
            #     if "&lt;&lt;</operator>" in etree.tostring(operator_item).decode('utf-8'):
            #         return True
    # for item in expr_xml_list:
    # if b"<operator>&lt;&lt;</operator>" in expr_xml_obj:
    #     return True

    return if_direct_log_call and if_second_operator


def transform_xml_str_to_code(xml_str):
    pre_str = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><unit xmlns="http://www.srcML.org/srcML/src" xmlns:cpp="http://www.srcML.org/srcML/cpp" revision="1.0.0" language="C++" filename="code_temp.cc">'
    xml_str = pre_str + xml_str + '</unit>'
    fifo_name = file_util.generate_random_file_name_with_extension('xml')
    os.mkfifo(fifo_name)
    try:
        process = subprocess.Popen(['srcml', fifo_name], stdout=subprocess.PIPE)
        with open(fifo_name, 'w') as f:
            f.write(xml_str)
        output = process.stdout.read()
    finally:
        os.remove(fifo_name)
    return str(output)



print(get_logging_calls_xml_of_repo("/Users/holen/DegreeProject/VCS/log4mlf/tensorflow"))


