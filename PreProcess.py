import Literature as L
import json
import pandas as pd
import numpy as np

###########################################################################
# txt提取模块
def parse_Txt(txt_dir, txt_num, txt_name, source):
    if source == "WOS":
        return parse_WosTxt(txt_dir, txt_num, txt_name)
    elif source == "CNKI":
        #return parse_CNKITxt(txt_dir, txt_num, txt_name)
        pass

def parse_WosTxt(txt_dir, txt_num, txt_name):
    PaperInfo = []
    start_mark_journal = "PT J\n"
    end_mark = "ER\n"
    fe = open(txt_dir + "error.txt", 'w', encoding="UTF-8")
    for i in range(1, txt_num+1):
        txt_file_name = txt_dir + txt_name + "-" + str(i) + ".txt"
        cnt = 0
        cnt_line = 0
        f = open(txt_file_name, encoding="UTF-8")
        flag = False
        f_lines = f.readlines()
        for line in f_lines:
            if line == start_mark_journal:
                title, journal, publication_year, abstract, citation_count = init()
                cnt += 1
                flag = True
            elif "PT " in line and flag is False:
                fe.write("编号-" +  str(cnt) + " 不是论文，非论文暂时无法识别\n")
                cnt += 1
            elif line.startswith('TI ') and flag:
                title = MultiLineGet(f_lines, "SO ", cnt_line).replace(",", " ")
            elif line.startswith('SO ') and flag:
                journal = line[3:-1].replace(",", " ")
            elif line.startswith("PY ") and flag:
                publication_year = line[3:-1]
            elif line.startswith("AB ") and flag:
                abstract = MultiLineGet(f_lines, "ZB ", cnt_line)
            elif line.startswith("TC ") and flag:
                citation_count = line[3:-1]
            elif line.startswith(end_mark) and flag:
                if title != "" and abstract != "":
                    PaperInfo.append(L.Literature(cnt, title, abstract, journal, publication_year, citation_count))
                else:
                    fe.write("编号-" + str(cnt) + " 标题或摘要缺失，跳过\n")
                flag = False
            cnt_line += 1
    return PaperInfo

"""
def parse_CNKITxt(txt_dir, txt_num, txt_name):
    PaperInfo = []
    start_mark = "SrcDatabase-来源库:"
    fe = open(txt_dir + "error.txt", 'w', encoding="UTF-8")
    for i in range(1, txt_num + 1):
        txt_file_name = txt_dir + txt_name + "-" + str(i) + ".txt"
        cnt = 0
        cnt_line = 0
        f = open(txt_file_name, encoding="UTF-8")
        flag = False
        f_lines = f.readlines()
        for line in f_lines:
            if start_mark + " 期刊" in line:
                title, journal, publication_year, abstract, citation_count = init()
                cnt += 1
                flag = True
            elif start_mark in line:
                fe.write("编号-" +  str(cnt) + " 不是论文，非论文暂时无法识别\n")
                cnt += 1
            elif line.strip().startswith('Title-题名:') and flag:
                title = MultiLineGet(f_lines, "Author-作者", cnt_line).replace(",", " ")
            elif line.startswith('Source-文献来源:') and flag:
                journal = line[13:-1].replace(",", " ")
            elif line.startswith("PY ") and flag:
                publication_year = line[3:-1]
            elif line.startswith("Summary-摘要:") and flag:
                abstract = MultiLineGet(f_lines, "SrcDatabase", cnt_line)
            elif line.startswith(end_mark) and flag:
                if title != "" and abstract != "":
                    PaperInfo.append(L.Literature(cnt, title, abstract, journal, publication_year, citation_count))
                else:
                    fe.write("编号-" + str(cnt) + " 标题或摘要缺失，跳过\n")
                flag = False
            cnt_line += 1
    return PaperInfo
"""

def MultiLineGet(file, end_mark, pos):
    txt = file[pos][3:].replace("\n", " ")
    for line in file[pos+1:]:
        if line.startswith(end_mark):
            return txt
        else:
            txt += line[3:].replace("\n", " ")
###########################################################################

###########################################################################
# excel 提取模块
def parse_Excel(file_dir, txt_num, txt_name, source, file_type, Non_IF_Paper_Delete, Non_DOI_Papaer_Delete, ImpactLimit):
    if source == "WOS":
        PaperInfo = parse_WOSExcel(file_dir, txt_num, txt_name, file_type, Non_IF_Paper_Delete, Non_DOI_Papaer_Delete, ImpactLimit)

    elif source == "CNKI":
        PaperInfo = parse_CNKIExcel(file_dir, txt_num, txt_name, file_type)

    return PaperInfo

def parse_WOSExcel(file_dir, file_total_num, file_name, file_type, Non_IF_Paper_Delete=True,
                   Non_DOI_Paper_Delete=True, ImpactLimit = 0):
    # 主要用于从WOS生成的excel中提取数据
    PaperInfo = []
    cnt = 0
    file_path = 'IF_database.xlsx'
    journal_lib = pd.read_excel(file_path)
    fe = open(file_dir + "error.txt", 'w', encoding="UTF-8")
    for i in range(1, file_total_num+1):
        excel_name = file_dir + file_name + "-" + str(i) + "." + file_type
        data = pd.read_excel(excel_name, usecols = ["Article Title", "Source Title", "DOI", "Publication Year",
                                                    "Abstract", "Times Cited, All Databases"])
        data_no_DOI = pd.read_excel(excel_name, usecols=["Article Title", "Source Title", "Publication Year",
                                                  "Abstract", "Times Cited, All Databases"])
        for j in range(0, len(data)):
            if j % 50 == 0:
                #进度条显示
                print(f"{int(j/len(data) * 100)}% , ({i}/{file_total_num})")
            if Non_DOI_Paper_Delete is True and True in pd.isnull(data.iloc[j]).values:
                fe.write("编号-" + str((i-1)*1000+j) + "存在内容缺失，不记录\n")
            elif Non_DOI_Paper_Delete is False and True in pd.isnull(data_no_DOI.iloc[j]).values:
                fe.write("编号-" + str((i - 1) * 1000 + j) + "存在内容缺失，不记录\n")
            else:
                IF = get_journal_if(data.iloc[j]["Source Title"], journal_lib, (i-1)*1000+j)
                if IF == 0 and Non_IF_Paper_Delete is True:
                    fe.write("编号-" + str((i-1)*1000+j) + "期刊影响因子未收录，不记录\n")
                    continue
                # 将title中的英文逗号替换，避免后面生成csv时候产生识别错误
                title = data.iloc[j]["Article Title"].replace(",", " ")
                TempPaper = L.Literature(cnt, title, data.iloc[j]["Abstract"], data.iloc[j]["Source Title"],
                                              data.iloc[j]["Publication Year"], data.iloc[j]["Times Cited, All Databases"], data.iloc[j]["DOI"])
                TempPaper.journal_IF = IF
                # 加入影响力阈值输出控制
                if TempPaper.PaperImpactCal(2024) > ImpactLimit:
                    PaperInfo.append(TempPaper)
                    cnt += 1
                else:
                    fe.write("编号-" + str((i - 1) * 1000 + j) + "期刊影响力不足，不记录\n")
    fe.close()
    return PaperInfo


def parse_CNKIExcel(file_dir, txt_num, txt_name, file_type):
    PaperInfo = []
    cnt = 0
    error_log = open(file_dir + "error.txt", 'w', encoding="UTF-8")

    for i in range(1, txt_num + 1):
        excel_name = file_dir + txt_name + "-" + str(i) + "." + file_type
        try:
            # 读取Excel文件，保留所有列
            data = pd.read_excel(excel_name)

            # 遍历每一行数据
            for j, row in data.iterrows():
                # 检查是否存在空值，如果有则记录错误并跳过
                if row.isnull().any():
                    error_log.write(f"编号-{cnt}存在内容缺失，不记录\n")
                    continue

                    # 提取所需信息
                title = row['Title-题名'].replace(",", " ")  # 替换逗号以避免CSV格式错误
                authors = row['Author-作者']  # 可以选择进一步处理作者信息，如分割多个作者
                organization = row['Organ-单位']  # 单位信息
                journal = row['Source-文献来源'].replace(",", " ")  # 替换逗号
                abstract = row['Summary-摘要']
                publication_year = row['PubTime-发表时间'][:4]  # 发表时间为YYYY-MM-DD格式
                citation_count = ""
                DOI = ""

                # 创建Literature实例并添加到列表中
                paper = L.Literature(cnt + 1, title, abstract, journal, publication_year, citation_count, DOI)
                PaperInfo.append(paper)
                cnt += 1

        except Exception as e:
            # 如果读取Excel文件时发生错误，记录错误信息并跳过当前文件
            error_log.write(f"读取文件{excel_name}时发生错误：{str(e)}\n")

    error_log.close()
    return PaperInfo

###########################################################################


###########################################################################
## Json 处理模块
def Json_Info_Read(Json_file_address, PaperInfo, file_dir, TitleList, ceilnum=-1):
    """
    用于对LLM处理后的json文件进行信息提取，生成csv文件；
    :param Json_file_address: 待读取的json文件地址
    :param PaperInfo:       文献的基础信息（可自动识别部分）
    :param file_dir:        全部文件的目录
    :param TitleList:       需要处理的关键信息
    :param ceilnum:         待处理总数
    :return:                无
    """
    full_result_address = file_dir + "full_result.csv"
    tar_result_address = file_dir + "tar_result.csv"
    f1 = open(full_result_address, 'w', encoding="UTF-8")
    f1.write(TitlePrint(TitleList))
    f2 = open(tar_result_address, 'w', encoding="UTF-8")
    f2.write(TitlePrint(TitleList))
    with open(Json_file_address, 'r', encoding="UTF-8") as f:
        data = json.load(f)
        cnt = 0
        for paper in PaperInfo:
            paper.LLM_extract_Info = data[str(cnt+1)]
            # 如果GPT成功识别，full和Tar两个文件均输出对应结果
            if Json_info_judge(paper, TitleList) is True:
                f1.write(paper.InfoPrint(2024, cnt, TitleList, cnt))
                f2.write(paper.InfoPrint(2024, cnt, TitleList, cnt))
            # 如果GPT没有有效识别，则只在full文件中输出结果
            else:
                f1.write(paper.InfoPrint(2024, cnt, TitleList, cnt))
            cnt += 1
            if ceilnum != -1 and cnt+1 > ceilnum:
                break
    f1.close()
    f2.close()

def Json_preprocess(Json_file_address, Json_file_processed):
    # 对LLM生成的json文件进行二次处理，使其可以用于后续的csv文件生成
    cnt = 1
    line_cnt = 0
    f1 = open(Json_file_address, 'r', encoding="UTF-8")
    f2 = open(Json_file_processed, 'w', encoding="UTF-8")
    f2.write("{\n")
    f1_lines = f1.readlines()
    for line in f1_lines:
        line_cnt += 1
        if cnt == 131:
            pass
        if "{" in line:
            line = '"' + str(cnt) + '"' + ":" + line
            cnt += 1
        if "，" in line or "," in line and "[" not in line:
            #替换除了最后的,为分号，避免csv的识别问题
            line = line.strip()
            line = line[:-2].replace("，", ";") + line[-2:]
            line = line[:-2].replace(",", ";") + line[-2:]
            line += "\n"
        if "}" in line and line_cnt != len(f1_lines) and line_cnt != len(f1_lines)-1:
            line = "},\n"
        f2.write(line)
    f2.write("}\n")
    f1.close()
    f2.close()

def Json_info_judge(paper, TitleList):
    # 用于判断GPT是否有效识别，写的比较简单，可以后期进一步补充
    if paper.LLM_extract_Info[TitleList[1]] != "" and paper.LLM_extract_Info[TitleList[0]] != "":
            #and "识别" not in paper.LLM_extract_Info[TitleList[2]]:
        return True
    else:
        return False

###########################################################################


###########################################################################
## csv表格输入输出模块
def TitlePrint(TitleList):
    # 用于输出csv结果中的标题行
    PrintStr = ""
    PrintStr += "编号,"
    PrintStr += "标题,"
    for name in TitleList:
        PrintStr += name + ","
    PrintStr += "期刊,"
    PrintStr += "年份,"
    PrintStr += "影响力,"
    PrintStr += "DOI,"
    PrintStr += "\n"
    return PrintStr

def TitleListRead(TitleFile):
    # 从title.txt中导入，标题行内容
    f = open(TitleFile, "r", encoding="UTF-8")
    f_lines = f.readlines()
    TitleList = []
    KeyWordList = []
    for line in f_lines:
        TitleList.append(line[:line.find(":")])
        KeyWordList.append(line[line.find("["):])
    return TitleList, KeyWordList

def init():
    return "", "", "", "", ""

def get_journal_if(journal_name, journal_lib, index):
    # 查询期刊的 2023 JIF
    # 使用 "Journal name" 列进行精确匹配

    result = journal_lib[journal_lib['Journal name'].str.lower() == journal_name.lower()]
    if not result.empty:
        # 返回精确匹配期刊的 2023 JIF 数值
        return result['2023 JIF'].values[0]
    else:
        #print(f"未找到第{index}篇论文，期刊 '{journal_name}' 的影响因子。")
        return 0

def csv_load(csv_file):
    data = pd.read_csv(csv_file)
    return data
###########################################################################
def file_parse(file_type, file_dir, file_total_num, file_name, source, Non_IF_Paper_Delete, Non_DOI_Papaer_Delete, ImpactLimit):
    if file_type == "txt":
        PaperInfo = parse_Txt(file_dir, file_total_num, file_name, source)
    elif file_type == "xls" or file_type == "xlsx":
        PaperInfo = parse_Excel(file_dir, file_total_num, file_name, source, file_type, Non_IF_Paper_Delete, Non_DOI_Papaer_Delete, ImpactLimit)
    return PaperInfo