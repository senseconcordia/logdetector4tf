from utils import file_util

cch_file_list = file_util.get_all_cch_files("/Users/holen/DegreeProject/VCS/log4mlf/tensorflow")
i = 0
for cch_path in cch_file_list:
    if not file_util.is_test_file(cch_path):
        i = i + 1

print(i)