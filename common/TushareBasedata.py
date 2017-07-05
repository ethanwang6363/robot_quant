#!/usr/bin/python
#coding=utf-8

import BaseTools as bt
from  Basedata import Basedata
import tushare as ts
from datetime import datetime
import os
import pandas as pd

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

'''
基础数据接口---Tushare数据

'''
class TushareBasedata(Basedata):

    '''
        通过时间段行情数据接口
    '''
    def get_history_data_by_date(self, code, start_date_str, end_date_str, frequency, fq):
        print 'tushare get_history_data_by_date start'
        if len(code) != 9:
            return None
        code = code[0:6]
        df1 = ts.get_hist_data(code,start=start_date_str,end=end_date_str, ktype=frequency)
        df1['tradedate']= df1.index
        df1 = df1.reset_index(drop=True)
        df1['date']=df1['tradedate'].map(lambda x:datetime.strptime(x, '%Y-%m-%d'))
        dfNew = df1.set_index('date')
        df = None
        if fq == 'N':
            df = ts.get_h_data(code, start=start_date_str, end=end_date_str, autype=None)
        elif fq == 'B':
            df = ts.get_h_data(code, start=start_date_str, end=end_date_str, autype='hfq')
        elif fq == 'F':
            df = ts.get_h_data(code, start=start_date_str, end=end_date_str)
        #df = df2.copy()
        df['pct_chg'] = dfNew['p_change']
        # del df['amount']
        #print df

        return df

    '''
        通过股票列表查询行情数据接口
    '''
    def get_history_data_by_stocklist(self, trade_date_str, codelist, frequency, fq):
        df = None
        dfChg = None

        for code in codelist:
            if len(code) != 9:
                continue
            code = code[0:6]
            df1 = None
            if fq == 'N':
                df1 = ts.get_k_data(code, start=trade_date_str, end=trade_date_str, autype=None)
            elif fq == 'B':
                df1 = ts.get_k_data(code, start=trade_date_str, end=trade_date_str, autype='hfq')
            elif fq == 'F':
                df1 = ts.get_k_data(code, start=trade_date_str, end=trade_date_str)
            df = pd.concat([df, df1])
            df2 = ts.get_hist_data(code, start=trade_date_str, end=trade_date_str, ktype=frequency)
            dfChg = pd.concat([dfChg, df2])
        #print df
        #print dfChg
        df = df.reset_index(drop=True)
        dfChg = dfChg.reset_index(drop=True)
        df['pct_chg'] = dfChg['p_change']
        del df['date']
        return df

    '''
        通过时间段指数行情数据接口
    '''
    def get_history_index_data_by_date(self, code, start_date_str, end_date_str, frequency):
        if len(code) != 9:
            return None
        code = code[0:6]
        df1 = ts.get_hist_data(code, start=start_date_str, end=end_date_str, ktype=frequency)
        df1['tradedate'] = df1.index
        df1 = df1.reset_index(drop=True)
        df1['date'] = df1['tradedate'].map(lambda x: datetime.strptime(x, '%Y-%m-%d'))
        dfNew = df1.set_index('date')
        df = ts.get_h_data(code, start=start_date_str, end=end_date_str, index=True)
        # df = df2.copy()
        df['pct_chg'] = dfNew['p_change']
        # del df['amount']
        # print df

        return df

    '''
        通过指数代码列表查询指数行情数据接口
    '''
    def get_history_index_data_by_stocklist(self, trade_date_str, codelist, frequency):
        df = None
        dfChg = None

        for code in codelist:
            if len(code) != 9:
                continue
            code = code[0:6]
            df1 = ts.get_k_data(code, start=trade_date_str, end=trade_date_str)
            df = pd.concat([df, df1])
            df2 = ts.get_hist_data(code, start=trade_date_str, end=trade_date_str, ktype=frequency)
            dfChg = pd.concat([dfChg, df2])
        # print df
        # print dfChg
        df = df.reset_index(drop=True)
        dfChg = dfChg.reset_index(drop=True)
        df['pct_chg'] = dfChg['p_change']
        del df['date']
        return df

    '''
        通过股票列表查询因子值数据 todo 待完成

        roe,净资产收益率(%)
    '''
    def get_factor_data_by_stocklist(self, trade_date_str, codelist, factorenname, tracetype):
        factorDf = None
        # 通过时间得到查询的年份、季度，往前顺延两个季度
        # 通过因子名称找出调用的api---业绩报告（主表）、如：偿债能力
        # 分别查询获取财务因子，年份、季度、接口

        # 通过trade_date与ann_date比较，小于trade_date，返回因子值
        trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d')
        quarterlist = bt.getLastestQuarterlistByDate(trade_date)

        for q in quarterlist:
            try:
                # 业绩报告（主表）
                df1 = ts.get_report_data(q[0], q[1])
                # 盈利能力--因子值数据
                df2 = ts.get_profit_data(q[0], q[1])

                df1 = df1.sort(["code", "report_date"], ascending=False)
                #print df1
                df1 = df1.drop_duplicates(['code'])
                #print df1
                df1 = df1.reset_index(drop=True)
                df2 = df2.drop_duplicates(['code'])
                df2 = df2.reset_index(drop=True)
                df1New = df1.set_index('code')
                df2New = df2.set_index('code')
                # print df1New
                # print df2New
                #print df1New.index
                #print df2New.index
                df2New['ann_date'] = df1New['report_date']
                print df2New
                #break
            except Exception, e:
                # traceback.print_exc()
                pass
                continue



    '''
        通过时间段因子值接口
    '''
    def get_factor_data_by_date(self, code, start_date_str, end_date_str, factorenname, tracetype):
        pass

    '''
        通过行业名称查询股票代码数据
    '''
    def get_stock_data_by_industryname(self, trade_date, industryname):
        industryname = industryname.decode("utf-8")
        df = ts.get_industry_classified()
        df = df[df.c_name==industryname]
        del df['c_name']
        return df

    '''
        通过概念名称查询股票代码数据
    '''
    def get_stock_data_by_conceptname(self, trade_date, conceptname):
        conceptname = conceptname.decode("utf-8")
        df = ts.get_concept_classified()
        df = df[df.c_name==conceptname]
        del df['c_name']
        return df

    '''
        通过地域名称查询股票代码数据
    '''
    def get_stock_data_by_areaname(self, trade_date, areaname):
        areaname = areaname.decode("utf-8")
        df = ts.get_area_classified()
        df = df[df.c_name==areaname]
        del df['area']
        return df

'''
t = TushareBasedata()
df = t.get_history_data_by_date('000001.SZ', '2016-01-01', '2017-01-01', 'D', 'N')
print df

#df2 = t.get_stock_data_by_industryname('2016-01-01', '综合行业'.decode("utf-8"))
#print df2

df3 = t.get_history_data_by_stocklist('2017-06-26', ['000001.SZ', '000002.SZ', '000003.SZ'], 'D', 'N')
print df3'''

'''
df1 = ts.get_report_data(2014,3)
df2 = ts.get_profit_data(2014,3)

df1 = df1.sort(["code","report_date"], ascending=False)
print df1
df1 = df1.drop_duplicates(['code'])
print df1
df1 = df1.reset_index(drop=True)
df2 = df2.drop_duplicates(['code'])
df2 = df2.reset_index(drop=True)
df1New = df1.set_index('code')
df2New = df2.set_index('code')
#print df1New
#print df2New
print df1New.index
print df2New.index
df2New['ann_date'] = df1New['report_date']
print df2New
'''
t = TushareBasedata()
# 净资产收益率(%)
#print t.get_factor_data_by_stocklist('2017-5-8', ['000001.SZ','000002.SZ','000004.SZ','000005.SZ'], 'roe', 1)

print t.get_history_index_data_by_date('000001.SZ', '2017-01-05', '2017-02-08', 'D')