import PreProcess as PP
def CSV_File_Classify(input_csv_file, prompt, file_dir, TitleList, KeyWordList, step_num=100):
    csv_data = PP.csv_load(input_csv_file)
    prompt_file = open(prompt, "r", encoding="UTF-8")
    prompt_line1 = prompt_file.readline()
    prompt_line2 = prompt_file.readline()

    for num in range(len(TitleList)):
        title = TitleList[num]
        f = open(file_dir + "LLM_template4" + title + ".txt", "w", encoding="UTF-8")
        cnt = 0
        count = 0
        for text in csv_data[title]:
            if cnt == 0:
                f.write(str(count) + ":\n")
                count += 1
                line = prompt_line1.replace("[]", "[" + title + "]")
                f.write(line)
                f.write(prompt_line2)
                f.write(KeyWordList[num][:-1])
                f.write("，二级分类请在一级分类的基础上给出细化分类：\n")
            f.write("{" + str(text) + "}")
            cnt += 1
            if cnt == step_num:
                f.write("\n")
                f.write("请按照我的输入顺序将结果以表格形式输出，格式为" + title + "|一级分类|二级分类\n如果有多重分类可能，那么请用'/'分隔\n")
                cnt = 0
        if cnt != 0:
            f.write("\n")
            f.write(
                "请按照我的输入顺序将结果以表格形式输出，格式为" + title + "|一级分类|二级分类\n如果有多重分类可能，那么请用'/'分隔\n")

