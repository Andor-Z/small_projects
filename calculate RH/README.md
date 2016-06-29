
今天在看招聘网站时，看到一家公司的数据分析岗位的面试前题，便下载下来做一下试试。  
代码和数据文件在这里[Andor-Z/small_projects/calculate RH](https://github.com/Andor-Z/small_projects/tree/master/calculate%20RH)。

## 1. 题目  
  
19991001-20000930”文件夹下包含 1999-10-01 至 2000-09-30 期间沪深两市全部 A 股的代码  、简称、日期、开盘价(元)、最高价(元)、最低价(元)、收盘价(元)、成交量(股)、成交金额(元)，以代码为文件名保存成的 xls 文件。请你计算 2000 年 3 月 9 日这一天的所有股票的市场情绪指标(RH)的排名, 降序排列，输出成 excel 文件或者 txt 文件，文件内容逐列依次为“代码”、“简称”、“市场情绪指标”、“排名”。可以使用任意编程语言或工具。市场情绪指标 RH 的计算公式如下：   
  
$$RH = \frac{max(最近5日收盘价(包括今日)) - 今日收盘价}{max(最近5日收盘价(包括今日)) - min(最近5日收盘价(包括今日))}$$  
  
最近 5 日收盘价相同，定义 RH=0 ; 上市不足 5 天的，不纳入计算。  

## 2. 第一反应  
  
看完此题目，我的第一反应是：  
    1. 是否会出现由于某些特殊原因，导致3月9日这天没有数据的？（个人最终理解如果3月9日无数据的，不纳入计算）  
    2. 最近5天，是指最近有数据的5天，还是时间上的最近5天？（个人最终理解为有数据的最近5天）
    3. 上市不足5天，指到3月9日时不足5天
    4. 对于上市不足5天、3月9日当天没有数据的，虽然不纳入计算，最好有数据统计一下？  
      
好吧，不管我这样空想了多少，不能光想不做，让我来着手处理它吧。  
  

## 3. 解题  
  
首先查看一下数据：


```python
import os
import pandas as pd
df = pd.read_excel('19991001-20000930/000001.SZ.xls')
df.head()
#df.tail(5)
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>代码</th>
      <th>简称</th>
      <th>日期</th>
      <th>开盘价(元)</th>
      <th>最高价(元)</th>
      <th>最低价(元)</th>
      <th>收盘价(元)</th>
      <th>成交量(股)</th>
      <th>成交金额(元)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>000001.SZ</td>
      <td>平安银行</td>
      <td>1999-10-08</td>
      <td>23.01</td>
      <td>23.25</td>
      <td>22.51</td>
      <td>22.63</td>
      <td>5341900.0</td>
      <td>121685913.1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>000001.SZ</td>
      <td>平安银行</td>
      <td>1999-10-11</td>
      <td>22.65</td>
      <td>23.00</td>
      <td>22.13</td>
      <td>22.21</td>
      <td>2945400.0</td>
      <td>66079127.7</td>
    </tr>
    <tr>
      <th>2</th>
      <td>000001.SZ</td>
      <td>平安银行</td>
      <td>1999-10-12</td>
      <td>22.21</td>
      <td>22.59</td>
      <td>22.13</td>
      <td>22.47</td>
      <td>2914400.0</td>
      <td>65088320.2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>000001.SZ</td>
      <td>平安银行</td>
      <td>1999-10-13</td>
      <td>22.58</td>
      <td>22.70</td>
      <td>21.83</td>
      <td>21.92</td>
      <td>3987900.0</td>
      <td>88021013.4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>000001.SZ</td>
      <td>平安银行</td>
      <td>1999-10-14</td>
      <td>21.78</td>
      <td>22.36</td>
      <td>21.55</td>
      <td>21.79</td>
      <td>3996200.0</td>
      <td>87281751.4</td>
    </tr>
  </tbody>
</table>
</div>



又多打开几个文件，发现每个文件包含一支股票的数据。对于异常的数据暂时先不主动去寻找。  
  
### 3.1 思路-分解  
  
    1. 先求出单独一支股票的RH值  
    2. 求出所有股票的RH值并根据题目要求排序  
    3. 将结果输入到指定文件  
    
  
 
### 3.2 完整代码  
因为写代码在先，写文章在后，就不把我遇到的问题一一写出来了，直接把代码放出来。代码上也有较为详细的注解。


```python
import os
import pandas as pd

def get_RH(filedir, date):
   '''
   根据文件路径和日期获取单支股票的市场情绪指标，返回
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

def get_stocks_RH(dir='19991001-20000930', date = '2000-03-09'):
    '''传入参数dir为包含数据的文件夹或者路径， date为所求RH值的日期
    状态码：  
    1：正常数据
    2：当天数据不存在
    3：截止到当天为止，上市不足5天
    '''
    stock_RHs = []
    stock_RHs_2 = []
    stock_RHs_3 = []
    data_list = os.listdir(dir)
    for i in data_list:
        data_file = i
        data_file_dir = os.path.join(dir, data_file)
        stock_RH = get_RH(data_file_dir, date)
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
    RH_file = date+'的RH.xls' 
    # 将最终的RH数据写入文件
    stock_df.to_excel(RH_file, index=False, columns = ['代码', '简称', '市场情绪指标', '排名'])
    
    print('本次一共获取{}支股票的数据。'.format(len(data_list)))
    print('其中可计算出{}的RH值一共{}支，已经写入当前文件夹下的“{}”文件。'.format(date, len(stock_RHs), RH_file))
    print('其中{}当天股票数据不存在的{}支。'.format(date, len(stock_RHs_2)))
    print('其中截止到{}为止，上市不足5天的{}支。'.format(date, len(stock_RHs_3)))

# if __name__ == '__main__':
#     get_stocks_RH()
```

## 4. 优化-利用多线程  
由于涉及到了很多IO操作，故欲用多线程优化。  
对于原获取单支股票的 `get_RH()` 不做变动。  
首先声明几个全局变量，以及继承至 `threading.Thread` 的类。


```python
from threading import Thread

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
```

### 4.1 测试优化效果  
- 未使用多线程的代码


```python
%run -t calculate_RH.py
```

    本次一共获取940支股票的数据。
    其中可计算出2000-03-09的RH值一共858支，已经写入当前文件夹下的“2000-03-09的RH.xls”文件。
    其中2000-03-09当天股票数据不存在的80支。
    其中截止到2000-03-09为止，上市不足5天的2支。
    
    IPython CPU timings (estimated):
      User   :      50.18 s.
      System :       0.00 s.
    Wall time:      50.18 s.
    

- 进行多线程优化过的代码


```python
%run -t calculate_RH_thread优化.py
```

    本次一共获取940支股票的数据。
    其中可计算出2000-03-09的RH值一共858支，已经写入当前文件夹下的“2000-03-09的RH_多线程.xls”文件。
    其中2000-03-09当天股票数据不存在的80支。
    其中截止到2000-03-09为止，上市不足5天的2支。
    
    IPython CPU timings (estimated):
      User   :      34.66 s.
      System :       0.00 s.
    Wall time:      34.66 s.
    
