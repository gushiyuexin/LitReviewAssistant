

def LLM_API_process(PaperInfo, Prompt_file, output_address, TitleList, step_num=5, mode="manual"):
    f = open(output_address, 'w', encoding="UTF-8")
    f1 = open(Prompt_file, "r", encoding="UTF-8")
    BasePrompt = f1.read()
    cnt = 0
    for Paper in PaperInfo:
        #手动操作部分
        if mode == "manual":
            Prompt = "[编号]：" + str(Paper.num) + "\n" + BasePrompt
            f.write(Prompt)
            title = "[标题]" + Paper.title + "\n"
            abstract = "[摘要]" + Paper.abstract + "\n"
            f.write(title)
            f.write(abstract)
            f.write("请按照{json}格式并以{中文}输出结果，同时，在json格式的最外层，加入{编号}\n")
            #for name in TitleList:
            #    f.write(name + "：\n")
            #f.write("}}\"\n")
            cnt += 1
        if cnt == step_num:
            cnt = 0
            f.write("请输出多个 JSON 格式的内容，每个内容以单独的 {} 形式呈现，而不是使用最外层的 [ ] 括号。" +
                    "同时，每个内容内部条目均换行显示，且每个内容之间不要有空行\n")
            f.write("请输出所有内容为一个整体，并确保每个条目都用正常的JSON格式换行，并且可以一次性复制。\n")
    f.close()
    f1.close()
