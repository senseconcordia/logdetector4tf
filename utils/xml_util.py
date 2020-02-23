import os
import subprocess
from pathlib import Path

from lxml import etree

from utils import file_util, shell_util

NS_MAP = {"src": "http://www.srcML.org/srcML/src"}


def get_logging_stmts_xml_of_repo(repo_path: str):
    cch_file_list = file_util.get_all_cch_files(repo_path)
    total_result = {}
    for cch_path in cch_file_list:
        file_log_list = []
        if not file_util.is_test_file(cch_path):
            logging_stmts = get_logging_stmts_xml_of_file(str(cch_path))
            for call in logging_stmts:
                file_log_list.append(call)
            if logging_stmts:
                total_result[str(cch_path)] = file_log_list

    return total_result


def get_logging_stmts_xml_of_file(file_path: str):
    print("processing: " + file_path)
    file_expr_list = get_expr_of_file(file_path)
    result = []
    for expr in file_expr_list:
        expr_str = etree.tostring(expr)
        bin_expr_str = b'<root>' + etree.tostring(expr) + b'</root>'
        expr_xml_obj = etree.fromstring(bin_expr_str, etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
        # print(expr)

        if is_logging_expr(expr_xml_obj):
            # logging_stmt = etree.tostring(expr)
            result.append(expr_str)

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
        expr_list = xml_object.xpath('//src:unit//src:expr', namespaces=NS_MAP)
        return expr_list
    else:
        return []


def is_logging_expr(expr_xml_obj):
    # select the current node and take it as the root, and only fetch the immediate child.
    call_xpath_str = './src:expr/*[1]'
    expr_call_xml = expr_xml_obj.xpath(call_xpath_str, namespaces=NS_MAP)
    # operator_xpath_str = './src:expr/*[2]'
    # expr_operator_xml = expr_xml_obj.xpath(operator_xpath_str, namespaces=NS_MAP)
    logging_call_name_list = ["LOG", "VLOG", "DVLOG", "LOG_EVERY_N_SEC", "TFLITE_LOG_PROD_ONCE", "TFLITE_LOG_ONCE",
                              "TFLITE_LOG_PROD", "TFLITE_LOG", "TF_LITE_KERNEL_LOG", "ESP_LOGE", "ESP_LOGW", "ESP_LOGI"
                              "ESP_LOGD", "ESP_LOGV", "NNAPI_LOG", "LOGI", "LOGE", "LOGW", "LOGV", "LOGD",
                              "XLA_VLOG_LINES", "XLA_LOG_LINES", "LOG_FIRST_N"]
    if_direct_log_call = False
    # if_second_operator = True
    for call_item in expr_call_xml:
        call_item_str = etree.tostring(call_item).decode('utf-8')
        if call_item_str.startswith('<call'):
            call_xml_obj = etree.fromstring(b'<root>' + etree.tostring(call_item) + b'</root>', etree.XMLParser(encoding='utf-8', ns_clean=True, recover=True))
            name_xpath_str = './src:call/*[1]'
            # immediate_following_sibling_xpath_str = './src:call/following-sibling:*[1]'
            call_name_xml = call_xml_obj.xpath(name_xpath_str, namespaces=NS_MAP)
            # immediate_sibling_xml = call_xml_obj.xpath(name_xpath_str, namespaces=NS_MAP)
            for name_item in call_name_xml:
                name_item_str = etree.tostring(name_item).decode('utf-8')
                if name_item_str.startswith('<name') and name_item_str.split('>')[1][:-6] in logging_call_name_list:
                    # print(name_item_str.split('>')[1][:-6])
                    if_direct_log_call = True

    return if_direct_log_call


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


def main():
    xml_logging_item_dict = get_logging_stmts_xml_of_repo("/Users/holen/DegreeProject/VCS/log4mlf/tensorflow")
    # print(len(xml_logging_item_dict.keys()))

    with open('/Users/holen/DegreeProject/logdetector4tf/data/tf_log_data.txt', 'w') as f:
        for key in xml_logging_item_dict.keys():
            f.write("\n%s\n" % key)
            for item in xml_logging_item_dict[key]:
                str_logging_item = transform_xml_str_to_code(item.decode('utf-8'))
                str_logging_item = str_logging_item[2:-1].replace('\\n', '').replace('\\t', '').replace('\\r', '').replace('\\', '')
                print_logging_str = " ".join(str_logging_item.split())
                f.write("%s\n" % print_logging_str)


if __name__ == "__main__":
    main()
