import os
import subprocess
from pathlib import Path

from lxml import etree

from utils import file_util, shell_util

NS_MAP = {"src": "http://www.srcML.org/srcML/src"}


def get_logging_stmts_xml_of_repo(repo_path: str):
    cch_file_list = file_util.get_all_cch_files(repo_path)
    total_result = []
    for cch_path in cch_file_list:
        logging_stmts = get_logging_stmts_xml_of_file(str(cch_path))
        for call in logging_stmts:
            total_result.append(call)

    return total_result


def get_logging_stmts_xml_of_file(file_path: str):
    print("processing: " + file_path)
    file_expr_list = get_expr_of_file(file_path)
    result = []
    with open('/Users/holen/DegreeProject/logdetector4tf/data/file_with_loop_vlog.txt', 'w') as f:
        tmp_file = ""
        for expr in file_expr_list:
            expr_str = etree.tostring(expr)
            bin_expr_str = b'<root>' + etree.tostring(expr) + b'</root>'
            expr = etree.fromstring(bin_expr_str, etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            # print(expr)

            if is_logging_expr(expr):
                # logging_stmt = etree.tostring(expr)
                tmp_file = file_path
                result.append(expr_str)

            if tmp_file != "":
                f.write("%s\n" % tmp_file)

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
        parser = etree.XMLParser(huge_tree=True, encoding='utf-8', ns_clean=True, recover=True)
        xml_object = etree.fromstring(xml_bytes, parser=parser)
        do_while_expr_list = xml_object.xpath('//src:do//src:expr', namespaces=NS_MAP)
        for_expr_list = xml_object.xpath('//src:for//src:expr', namespaces=NS_MAP)
        while_expr_list = xml_object.xpath('//src:while//src:expr', namespaces=NS_MAP)
        return do_while_expr_list + for_expr_list + while_expr_list
    else:
        return []


def is_logging_expr(expr_xml_obj):
    # select the current node and take it as the root, and only fetch the immediate child.
    call_xpath_str = './src:expr/*[1]'
    expr_call_xml = expr_xml_obj.xpath(call_xpath_str, namespaces=NS_MAP)
    operator_xpath_str = './src:expr/*[2]'
    expr_operator_xml = expr_xml_obj.xpath(operator_xpath_str, namespaces=NS_MAP)
    if_direct_log_call = False
    if_second_operator = True
    for call_item in expr_call_xml:
        # print(etree.tostring(call_item).decode('utf-8'))
        call_item_str = etree.tostring(call_item).decode('utf-8')
        if call_item_str.startswith('<call'):
            # print(etree.tostring(call_item).decode('utf-8'))
            call_xml_obj = etree.fromstring(b'<root>' + etree.tostring(call_item) + b'</root>', etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            name_xpath_str = './src:call/*[1]'
            immediate_following_sibling_xpath_str = './src:call/following-sibling:*[1]'
            call_name_xml = call_xml_obj.xpath(name_xpath_str, namespaces=NS_MAP)
            immediate_sibling_xml = call_xml_obj.xpath(name_xpath_str, namespaces=NS_MAP)
            for name_item in call_name_xml:
                name_item_str = etree.tostring(name_item).decode('utf-8')
                if "VLOG".upper() in name_item_str and name_item_str.startswith('<name'):
                    print(etree.tostring(name_item).decode('utf-8'))
                    if_direct_log_call = True

    # for operator_item in expr_operator_xml:
    #     if etree.tostring(operator_item).decode('utf-8').startswith('<operator'):
    #         operator_xml_obj = etree.fromstring(b'<root>' + etree.tostring(operator_item) + b'</root>',
    #                                         etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
    #         operator_value_xpath_str = './src:operator/text()'
    #         operator_value = operator_xml_obj.xpath(operator_value_xpath_str, namespaces=NS_MAP)
    #         print(operator_value)



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



# print(get_logging_stmts_xml_of_repo("/Users/holen/DegreeProject/VCS/log4mlf/tensorflow"))
# print(get_logging_stmts_xml_of_repo("/Users/holen/Desktop/tf-test/xla_kernel_cache"))

xml_logging_item_list = get_logging_stmts_xml_of_repo("/Users/holen/DegreeProject/VCS/log4mlf/tensorflow")
str_logging_item_list = []
for item in xml_logging_item_list:
    # print(type(item))
    # print(item.decode('utf-8'))
    str_logging_item = transform_xml_str_to_code(item.decode('utf-8'))
    # print(str_logging_item)
    str_logging_item_list.append(str_logging_item)

with open('/Users/holen/DegreeProject/logdetector4tf/data/tf_loop_log_data.txt', 'w') as f:
    for item in str_logging_item_list:
        # byte_str = str.encode(item)
        # print_logging_str = (item[2:-1])
        item = item[2:-1].replace('\\n', '').replace('\\t', '').replace('\\r', '')
        print_logging_str = " ".join(item.split())

        f.write("%s\n" % print_logging_str)


