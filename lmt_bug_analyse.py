import pandas, re
from sqlalchemy import create_engine

input_file = 'D:\安恒信息\LMT\现网问题\LMT.xlsx'
output_file = 'D:\安恒信息\LMT\现网问题\LMT_BUG_CURRENT_STATUS.xlsx'
input_file2 = 'D:\安恒信息\LMT\现网问题\LMT_BUG_LAST_WEEK_STATUS.xlsx'

bug_sheets = [
    ("2023 Q2现网问题闭环","问题链接"), 
    ("2023 Q3现网问题闭环","问题链接"),
    ("2023 Q4现网问题闭环","问题链接"),
    ("2024 Q1现网问题闭环","问题链接"),
    ("2024 Q2现网问题闭环","禅道链接"),
    ("2024 Q3现网问题闭环","禅道链接"),
    ("2024 Q4现网问题闭环","禅道链接")
    ]

# 自动化平台数据库信息
username = 'root'
password = 'ngfw123!%40%23'
port = '3306'
host = '10.113.53.29'
database = 'true_zentao_copy'

def get_bugs(file, bug_sheets):
    '''
    输入文件、及sheet页的列表
    返回值是一个DataFramem，列名是BUG_ID和是否紧急
    返回值已进行去重和排序
    '''

    data = []
    for i in bug_sheets:
        bug_sheet = pandas.read_excel(file, sheet_name=i[0])
        if "是否紧急" in bug_sheet.columns:  # 存在是否紧急的列
            temp_df = bug_sheet[[i[1], "是否紧急"]]
            for j in temp_df.values:  # j是一个list，是每行数据
                if isinstance(j[0], str):  # 如果没有问题单号，跳过
                    bug_ids = re.findall(r'(?:bugID|id)=(\d+)', j[0])
                    for k in bug_ids:
                        data.append([k, j[1]])                               
        else:
            temp_df = bug_sheet[[i[1]]]
            temp_df["是否紧急"] = float('nan') # 需要优化，pandas不建议这样操作
            for j in temp_df.values:  
                if isinstance(j[0], str): 
                    bug_ids = re.findall(r'(?:bugID|id)=(\d+)', j[0])
                    for k in bug_ids:  
                        data.append([k, j[1]])
    # 构造df并去重排序
    return pandas.DataFrame(data, columns=["BUG_ID", "是否紧急"]).drop_duplicates(subset=["BUG_ID"]).sort_values(by="BUG_ID", key=lambda x : x.astype(int))

def get_bug_status(bug_ids):
    '''
    从自动化平台数据库获取bug状态
    输入DF，包含BUG_ID列和是否紧急列
    输出一个DF，列名是：BUG_ID，BUG标题，责任人，是否紧急，状态
    '''

    rst_df = pandas.DataFrame(columns=["Bug编号", "Bug标题", "责任人", "是否紧急", "Bug状态"])
    try:
        engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}') # 创建数据库连接
    except:
        print("数据库连接失败")
        return
    for bug in bug_ids.values: # bug是一个list，包含bug id和是否紧急
        mysql_bug_df = pandas.read_sql_query(f'SELECT id,title,assignedto,status,substatus FROM zt_bug WHERE id={bug[0]}', engine)  # 根据bug id查询bug状态，返回一个df
        # 需要根据BUG的status和substatus公共判断BUG是否关闭
        print(bug[0],end="\n")
        print(mysql_bug_df.iloc[0,4])
        if mysql_bug_df.iloc[0,4]:

            if mysql_bug_df.iloc[0,4] == '10':
                rst_df.loc[len(rst_df)] = [bug[0], mysql_bug_df.iloc[0,1], mysql_bug_df.iloc[0,2], bug[1], "closed"]
            else:
                rst_df.loc[len(rst_df)] = [bug[0], mysql_bug_df.iloc[0,1], mysql_bug_df.iloc[0,2], bug[1], mysql_bug_df.iloc[0,3]]
    return rst_df

def compare_df(df1, df2):
    '''
    对比1周期间LMTbug的新增和关闭情况
    返回状态有变化的BUG清单和新增的BUG清单
    '''
    diff = df1.compare(df2)
    diff.to_excel('D:\安恒信息\LMT\现网问题\LMT_DI.xlsx')
    return 

if __name__ == '__main__':
    bug_ids = get_bugs(file=input_file, bug_sheets=bug_sheets)

    last_week_bug_status_df = pandas.read_excel(input_file2).set_index('Bug编号') # 读取上一周BUG状态数据，Bug编号是索引
    current_bug_status_df = get_bug_status(bug_ids).set_index('Bug编号') # 获取当前bug状态数据，Bug编号是索引

    # 对比BUG编号，检查是否有新增，若有新增，将新增的BUG保存到一个DataFrame
    # 需要修改为根据Bug ID判断，因为Bug标题可以修改
    mask = current_bug_status_df['Bug标题'].isin(last_week_bug_status_df['Bug标题'])
    increase_bug_df = current_bug_status_df[~mask]

    # 对边BUG状态，将有变化的BUG保存到一个DataFrame
    change_bug_df = pandas.DataFrame(columns=["Bug编号", "Bug标题", "责任人", "是否紧急", "Bug状态"], index=['Bug编号'])
    for bug_id in last_week_bug_status_df.index:
        # 根据Bug编号判断上周和当前的Bug状态是否一致，若一致则跳过，若不一致则保存到DataFrame
        if str(bug_id) in current_bug_status_df.index:
            if last_week_bug_status_df.loc[bug_id, 'Bug状态'] != current_bug_status_df.loc[str(bug_id), 'Bug状态']:
                change_bug_df.loc[len(change_bug_df)] = current_bug_status_df.loc[str(bug_id)]
    
    # 最新的BUG状态数据写入文件之前将原来的文件备份到上周数据中（LAST WEEK STATUS)
    pandas.read_excel(output_file).to_excel(input_file2, index=False)
    
    # 将最新数据写入文件
    with pandas.ExcelWriter(output_file) as writer:
        current_bug_status_df.to_excel(writer, sheet_name="当前所有问题", index_label='Bug编号', index=True)
        increase_bug_df.to_excel(writer, sheet_name="新增问题", index_label='Bug编号', index=True)
        change_bug_df.to_excel(writer, sheet_name="状态变更问题", index_label='Bug编号', index=True)