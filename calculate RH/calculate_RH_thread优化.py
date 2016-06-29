import os
import pandas as pd
from threading import Thread



def get_RH(filedir, date):
    '''根据文件路径和日期获取单支股票的市场情绪指标，返回
    stock_RH = {'代码': stock_code, '简称': stock_name, '市场情绪指标': RH, '状态码': status_code}
    状态码：   
    1：正常数据
    2：当天数据不存在
    3：截止到当天为止，上市不足5天
    '''
    # 因为后续取值需要日期，将日期定位索引值方便取值
    stock_df = pd.read_excel(filedir, index_col='日期')
    # 获得这支股票的代码和简称
    stock_code = stock_df['代码'][0]
    stock_name = stock_df['简称'][0]
    # 获得这支股票的所有的日期，并转换类型，以检查当天的数据是否存在
    date_list = stock_df.index.tolist()
    date_pd = pd.to_datetime(date)
    if date_pd not in date_list:
        # 当天数据不存在，状态码为2
        status_code = 2
        RH = None
    else:
        # 取出最近5天的数据
        df5 = stock_df[:date].tail(5)
        # 如果截止到当天为止，数据量小于5，表示到当天上市不足5天
        if len(df5) < 5:
            # 截止到当天为止，上市不足5天，状态码为3
            status_code = 3
            RH = None
        else:
            # 正常数据，状态码为1
            status_code = 1
            max_closing_price = df5['收盘价(元)'].max()
            min_closing_price = df5['收盘价(元)'].min()
            if max_closing_price == min_closing_price:
                # 若最近5日收盘价相同，RH = 0
                RH = 0
            else:
                RH = (max_closing_price - df5.ix[date]['收盘价(元)'])/(max_closing_price - min_closing_price)            
        
    stock_RH = {'代码': stock_code, '简称': stock_name, '市场情绪指标': RH, '状态码': status_code}
    return stock_RH

# 声明全局变量
stock_RHs_all = []


class GetRHThread(Thread):
    def __init__(self, filedir, date):
        self.filedir = filedir
        self.date = date
        self.stock_RH = {}
        super(GetRHThread, self).__init__()

    def run(self):
        '''
        调用get_RH函数获取单支股票的市场情绪指标
        并将数据添加到全局变量列表中
        '''
        self.stock_RH = get_RH(self.filedir, self.date)
        stock_RHs_all.append(self.stock_RH)
        


def get_stocks_RH(dir='19991001-20000930', date = '2000-03-09'):
    '''传入参数dir为包含数据的文件夹或者路径， date为所求RH值的日期
    状态码：  
    1：正常数据
    2：当天数据不存在
    3：截止到当天为止，上市不足5天
    '''
    data_list = os.listdir(dir)
    threads = []
    for i in data_list:
        data_file = i
        data_file_dir = os.path.join(dir, data_file)
        t = GetRHThread(data_file_dir, date)
        threads.append(t)
        t.start()
    for t in threads:
        # 暂停主程序，待所有线程都结束后再继续执行后面的语句
        t.join()
    stock_RHs = []
    # 2、3列表为可能的需求准备
    stock_RHs_2 = []
    stock_RHs_3 = []
    for stock_RH in stock_RHs_all:
        # 根据状态码进行分类，添加到不同的列表中
        if stock_RH['状态码'] == 1:
            stock_RHs.append(stock_RH)
        elif stock_RH['状态码'] == 2:
            stock_RHs_2.append(stock_RH)
        elif stock_RH['状态码'] == 3:
            stock_RHs_3.append(stock_RH)
        
    # 根据RH值排序
    stock_RHs = sorted(stock_RHs, key=lambda s:s['市场情绪指标'], reverse=True)
    for i in range(len(stock_RHs)):
        stock_RHs[i]['排名'] = i + 1
    stock_df = pd.DataFrame(stock_RHs)
    # 删除状态码
    stock_df = stock_df.drop('状态码', axis=1)
    RH_file = date+'的RH_多线程.xls' 
    # 将最终的RH数据写入文件
    stock_df.to_excel(RH_file, index=False, columns = ['代码', '简称', '市场情绪指标', '排名'])
    print('本次一共获取{}支股票的数据。'.format(len(data_list)))
    print('其中可计算出{}的RH值一共{}支，已经写入当前文件夹下的“{}”文件。'.format(date, len(stock_RHs), RH_file))
    print('其中{}当天股票数据不存在的{}支。'.format(date, len(stock_RHs_2)))
    print('其中截止到{}为止，上市不足5天的{}支。'.format(date, len(stock_RHs_3)))

if __name__ == '__main__':
    get_stocks_RH()