"""
LLM辅助文摘信息提取工具
开发者： gsyx
#######################################################
软件功能：结合LLM对于大批量文件进行文摘分析
1. 对于下载的txt文件进行预处理，去除无效信息部分，提取关键数值信息，并将摘要和题目部分整理出来
2. 调用LLM API，对上述题目和摘要，按照Prompt提示词进行分析，整理得到json文件
3. 将整理好的json文件再次发给LLM，结合知识图谱等内容，对其进行二次分析与处理
4. 结合LLM对后续研究方向提供建议

########################################################
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import PreProcess as PP
import LLM_API
import LitClassification as Classify

UI = True

if UI is True:

    # 创建主窗口
    root = tk.Tk()
    root.title("LLM Paper Processing Interface")
    root.geometry("800x600")

    # 全局变量
    source_var = tk.StringVar(value="WOS")
    mode_var = tk.StringVar(value="manual")
    file_type_var = tk.StringVar(value="xls")
    Non_IF_var = tk.BooleanVar(value=True)
    Non_DOI_var = tk.BooleanVar(value=False)
    Non_Review_var = tk.BooleanVar(value=False)
    file_total_num = 1
    file_name = ""
    extract_step_num_var = tk.IntVar(value=5)  # 将 step_num 作为 IntVar 变量来绑定下拉菜单
    classify_step_num_var = tk.IntVar(value=50)
    file_dir = ""
    PaperInfo = None
    TitleList = []
    KeyWordList = []
    MaxPaperNum = -1        #补一个最大数量
    ImpactLimit = 0

    # 选择文件夹
    def select_directory():
        global file_dir
        file_dir = filedialog.askdirectory()

        # 确保路径末尾带有斜杠（适用于 Windows）
        if not file_dir.endswith("/") and not file_dir.endswith("\\"):
            file_dir += "/"

        dir_label.config(text=file_dir)


    # 获取输入参数
    def set_parameters():
        global file_total_num, file_name, MaxPaperNum, ImpactLimit, TitleList, KeyWordList
        Article_title_list_file = f"{file_dir}/Title4Article.txt"
        Review_title_list_file = f"{file_dir}/Title4Review.txt"

        file_total_num = int(num_files_entry.get())
        file_name = file_name_entry.get()
        ImpactLimit = int(impact_entry.get())
        MaxPaperNum = int(PaperNum_entry.get())

        if Non_Review_var is True:
            TitleList, KeyWordList = PP.TitleListRead(Article_title_list_file)
        else:
            TitleList, KeyWordList = PP.TitleListRead(Review_title_list_file)

        messagebox.showinfo("Info", "Parameters updated successfully.")

    # Step 1: 文献关键部分提取
    def extract_paper_info():
        global PaperInfo
        try:
            output_txt = f"{file_dir}/LLM_template.txt"

            # 文献解析
            PaperInfo = PP.file_parse(file_type_var.get(), file_dir, file_total_num, file_name,
                                      source_var.get(), Non_IF_var.get(), Non_DOI_var.get(), ImpactLimit)

            messagebox.showinfo("Success", "Paper info extraction completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error in paper extraction: {e}")

    # Step 2: 将 WOS 下载的 txt 文件转换为特定格式
    def convert_txt_format():
        if PaperInfo:
            output_txt = f"{file_dir}/LLM_template.txt"
            if Non_Review_var.get() is True:
                prompt_file = f"{file_dir}/Prompt4Review.txt"
            else:
                prompt_file = f"{file_dir}/Prompt4Article.txt"
            try:
                LLM_API.LLM_API_process(PaperInfo, prompt_file, output_txt, TitleList, step_num=extract_step_num_var.get())
                messagebox.showinfo("Success", "Text conversion for LLM completed.")
            except Exception as e:
                messagebox.showerror("Error", f"Error in text conversion: {e}")
        else:
            messagebox.showerror("Error", "Please run Step 1 first.")

    # Step 3: 对 JSON 文件格式进行微调
    def preprocess_json():
        json_file = f"{file_dir}/LLM_result.json"
        json_file_process = f"{file_dir}/LLM_result_processed.json"
        try:
            PP.Json_preprocess(json_file, json_file_process)
            messagebox.showinfo("Success", "JSON preprocessing completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error in JSON preprocessing: {e}")

    # Step 4: csv文件生成
    def generate_csv():
        json_file_process = f"{file_dir}/LLM_result_processed.json"
        try:
            PP.Json_Info_Read(json_file_process, PaperInfo, file_dir, TitleList, MaxPaperNum)
            messagebox.showinfo("Success", "JSON analysis and filtering completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error in JSON analysis: {e}")

    # Step 5: 根据生成的 CSV，对关键词进行分类
    def classify_keywords():
        tar_result = f"{file_dir}/tar_result.csv"
        prompt4classify = f"{file_dir}/Prompt4Classify.txt"
        try:
            Classify.CSV_File_Classify(tar_result, prompt4classify, file_dir, TitleList, KeyWordList, step_num=classify_step_num_var.get())
            messagebox.showinfo("Success", "Keyword classification completed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error in keyword classification: {e}")

    # 创建界面元素
    tk.Label(root, text="文献来源:").grid(row=0, column=0, sticky="w")
    tk.Radiobutton(root, text="WOS", variable=source_var, value="WOS").grid(row=0, column=1, sticky="w")
    tk.Radiobutton(root, text="CNKI", variable=source_var, value="CNKI").grid(row=0, column=2, sticky="w")

    tk.Label(root, text="LLM使用模式（目前仅可以使用手动）:").grid(row=1, column=0, sticky="w")
    tk.Radiobutton(root, text="手动", variable=mode_var, value="manual").grid(row=1, column=1, sticky="w")
    tk.Radiobutton(root, text="自动", variable=mode_var, value="auto").grid(row=1, column=2, sticky="w")

    tk.Label(root, text="文献集合类型:").grid(row=2, column=0, sticky="w")
    tk.Radiobutton(root, text="xls", variable=file_type_var, value="xls").grid(row=2, column=1, sticky="w")
    tk.Radiobutton(root, text="txt", variable=file_type_var, value="txt").grid(row=2, column=2, sticky="w")

    tk.Label(root, text="文件数量:").grid(row=3, column=0, sticky="w")
    num_files_entry = tk.Entry(root)
    num_files_entry.insert(0, str(file_total_num))
    num_files_entry.grid(row=3, column=1)

    tk.Label(root, text="文件名称:").grid(row=4, column=0, sticky="w")
    file_name_entry = tk.Entry(root)
    file_name_entry.insert(0, file_name)
    file_name_entry.grid(row=4, column=1)

    # Step Number 菜单
    tk.Label(root, text="文摘提取单次数量:").grid(row=5, column=0, sticky="w")
    extract_step_options = [5, 10, 15, 20, 25, 30]
    extract_step_num_menu = tk.OptionMenu(root, extract_step_num_var, *extract_step_options)
    extract_step_num_menu.grid(row=5, column=1, sticky="w")

    tk.Label(root, text="文摘分类单次数量:").grid(row=6, column=0, sticky="w")
    classify_step_options = [50, 75, 100, 125, 150]
    classify_step_num_menu = tk.OptionMenu(root, classify_step_num_var, *classify_step_options)
    classify_step_num_menu.grid(row=6, column=1, sticky="w")

    tk.Label(root, text="影响力阈值:").grid(row=7, column=0, sticky="w")
    impact_entry = tk.Entry(root)
    impact_entry.insert(0, str(ImpactLimit))
    impact_entry.grid(row=7, column=1)

    tk.Label(root, text="加载文献数量:").grid(row=7, column=2, sticky="w")
    PaperNum_entry = tk.Entry(root)
    PaperNum_entry.insert(0, str(MaxPaperNum))
    PaperNum_entry.grid(row=7, column=3)

    tk.Label(root, text="是否为综述整理:").grid(row=8, column=0, sticky="w")
    tk.Checkbutton(root, variable=Non_Review_var).grid(row=8, column=1)

    tk.Label(root, text="是否跳过无期刊影响因子文献:").grid(row=8, column=2, sticky="w")
    tk.Checkbutton(root, variable=Non_IF_var).grid(row=8, column=3)

    tk.Label(root, text="是否跳过无DOI号文献:").grid(row=9, column=0, sticky="w")
    tk.Checkbutton(root, variable=Non_DOI_var).grid(row=9, column=1)

    # 选择目录按钮
    tk.Button(root, text="选择文件目录", command=select_directory).grid(row=10, column=0, sticky="w")
    dir_label = tk.Label(root, text="")
    dir_label.grid(row=10, column=1, sticky="w")

    # 设置参数按钮
    tk.Button(root, text="设定参数", command=set_parameters).grid(row=11, column=0, columnspan=2)

    # 分步执行按钮
    tk.Button(root, text="Step 1: 文摘信息提取", command=extract_paper_info).grid(row=12, column=0, columnspan=2)
    tk.Button(root, text="Step 2: 文摘任务提示词生成", command=convert_txt_format).grid(row=13, column=0, columnspan=2)
    tk.Button(root, text="Step 3: JSON预处理", command=preprocess_json).grid(row=14, column=0, columnspan=2)
    tk.Button(root, text="Step 4: CSV文件生成", command=generate_csv).grid(row=15, column=0, columnspan=2)
    tk.Button(root, text="Step 5: 分类任务提示词生成", command=classify_keywords).grid(row=16, column=0, columnspan=2)

    root.mainloop()
else:
    # 文件参数设置
    source = "WOS"  # 用于选择文献来源，web of science - WOS, 中国知网 - CNKI
    mode = "manual"  # 用于选择时自动化接入[auto]或者手动接入[manual]

    ##用于存放所有的待处理文件目录
    # 需要有文献的文件，还有Prompt.txt和Title.txt
    file_dir = "D:\\工作\\成果\\论文\\进行中\\科研-Review-3DP Hydrogel For Drug\\文摘收集\\"

    # 提取任务
    file_type = "xls"  # 用于选择文献格式，包含xls/txt，强烈建议excel
    file_total_num = 1  # 连续编号文件的总数量
    file_name = "3DPHydrogel4Drug-Review"  # 带处理文件名称，最终生成结果为：[file_name]-1
    output_txt = file_dir + "LLM_template.txt"  # 生成的用于LLM的模板文件
    json_file = file_dir + "LLM_result.json"  # 经过LLM处理过的json文件
    json_file_process = file_dir + "LLM_result_processed.json"  # 对json文件进行二次处理后的文件
    Prompt_file = file_dir + "Prompt.txt"  # LLM_template.txt中的通用提示词
    Prompt_Review_file = file_dir + "Prompt4Review.txt"  # LLM_template.txt中的通用提示词
    TitleList_file = file_dir + "Title.txt"  # 需要读取的关键信息内容（注意换行输出）

    ##分类任务
    tar_result = file_dir + "tar_result.csv"  # 处理完毕后的csv文件
    Prompt4Classify = file_dir + "Prompt4Classify.txt"  # 用于分类任务的提示词模版

    ##参数控制
    # 提取任务
    Non_IF_Paper_Delete = True  # 是否删除没有期刊影响因子的论文
    Non_DOI_Papaer_Delete = False  # 是否删除没有DOI号的论文
    step_num = 5  # 多少个文章一组进行输出

    # 分类任务参数
    classify_step_num = 50  # 多少个文章一组进行输出

    ##程序运行
    # 文献关键部分提取（仅第一步、第五步需要运行，剩下不需要运行，当然，运行也不影响最后结果）
    #PaperInfo = PP.file_parse(file_type, file_dir, file_total_num, file_name, source, Non_IF_Paper_Delete, Non_DOI_Papaer_Delete)
    TitleList, KeyWordList = PP.TitleListRead(TitleList_file)

    # LLM API接入
    # 第一步： 将wos下载的txt文件转换为特定格式的txt
    # LLM_API.LLM_API_process(PaperInfo, Prompt_file, output_txt, TitleList, step_num=step_num)
    # 第二步 将txt手动/自动输入到LLM中，得到json文件
    # 第三步 对json文件格式进行微调
    # PP.Json_preprocess(json_file, json_file_process)
    # 第四步 对生成的json文件进行二次分析，将其中的非相关项去除（可省略）
    # 第五步 处理后的json文件进行提取，生成csv的文件
    # PaperInfoUpdate = PP.Json_Info_Read(json_file_process, PaperInfo, file_dir, TitleList)
    # 第六步 根据生成的csv，对关键字内容进行分类
    PaperInfoClassify = Classify.CSV_File_Classify(tar_result, Prompt4Classify, file_dir, TitleList, KeyWordList, classify_step_num)
