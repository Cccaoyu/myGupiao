#  股票信息以及监控程序
import traceback

import requests
import time
import os
import pymysql
import stocktools.mylogs


# 判断字符串中是否含有中文
def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


# 获取url网页
def get_target_url(target_url):
    f"""
    获取指定url网页信息
    :param target_url:  目标url
    :return: 网页信息
    """
    if target_url == '':
        print("url 不能为空")
        return None
    else:
        return requests.get(target_url).text


# 获取股票信息
def get_stock_information(stock_code):
    """
    获取股票信息登记到数据库中
    :param stock_code: 股票代码
    :return: 返回成功笔数
    """
    info_add = 'http://hq.sinajs.cn/list='

    res = get_target_url(info_add + stock_code)

    result = res.split('=')[1]  # 截取等号之后的数据部分

    stock_name = result.split(',')[0].replace('"', '')  # 股票名称
    start_price = float(result.split(',')[1])  # 今日开盘价格
    end_price = float(result.split(',')[2])  # 昨日收盘价格
    cur_price = float(result.split(',')[3])  # 当前价格
    max_price = float(result.split(',')[4])  # 今日最高价格
    min_price = float(result.split(',')[5])  # 今日最低价格

    if start_price > float(0):
        rate = (cur_price - start_price) / start_price * 100  # 涨跌幅度
    else:
        rate = float(0)

    # print("股票名称:", stock_name)
    # print("今日开盘价格:", start_price)
    # print("昨日收盘价格:", end_price)
    # print("当前价格:   ", cur_price)
    # print("今日最高价格:", max_price)
    # print("今日最低价格:", min_price)

    # if rate < 0:
    #     content = "今日跌幅 {0:.2f}%".format(rate)
    #     print(content)
    # else:
    #     content = "今日涨幅 {0:.2f}%".format(rate)
    #     print(content)

    #  先查询 没有结果再登记 否则 更新
    sql1 = "select * from stock where txn_dt='%s' and stock_code='%s'"
    data1 = (time.strftime("%Y%m%d"), stock_code)
    ret = sqlr(sql1 % data1)
    Logger.info("返回记录数：%s" % ret)
    if ret > 0:
        up_sql = "update stock set start_price='%.2f',end_price='%.2f',cur_price='%.2f'" \
                 ",max_price='%.2f',min_price='%.2f',rate='%.2f'" \
                 "where" \
                 " txn_dt='%s' and stock_code='%s'"
        up_data = (start_price, end_price, cur_price, max_price, min_price, rate, time.strftime("%Y%m%d"), stock_code)

        return sqlr(up_sql % up_data)

    elif ret == 0:
        insert_sql = "INSERT INTO stock (txn_dt,stock_code,stock_name,start_price,end_price,cur_price,max_price," \
                     "min_price,rate) " \
                     "VALUES" \
                     "('%s','%s','%s',%.2f,%.2f,%.2f,%.2f,%.2f,%.2f)"
        insert_data = (
            time.strftime("%Y%m%d"), stock_code, stock_name, start_price, end_price, cur_price, max_price, min_price,
            rate)

        return sqlr(insert_sql % insert_data)
    else:
        return ret


#  清理屏幕 用于终端
def screen_clear():
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


# 连接数据库
def connect_db():
    """
    连接数据库
    :return: 数据库对象
    """
    connect = pymysql.Connect(
        host='121.40.117.70',
        port=3306,
        user='centos',
        passwd="123456",
        db='mysql',
        charset='utf8'
    )
    Logger.info(connect)
    return connect


# 执行sql
def sqlr(sel, args=None):
    """
    执行sql语句
    :param sel: sql语句
    :param args: sql语句条件
    :return: 失败返回 -1 ; 成功返回笔数
    """
    Logger.info("执行sql %s" % sel)

    conn = connect_db()  # 连接数据库
    cursor = conn.cursor()  # 获取游标

    try:
        cursor.execute(sel, args)  # 执行sql
    except Exception as e:
        conn.rollback()  # 抛出异常 回滚事物
        Logger.error("事务处理失败%s" % e)
        Logger.error(traceback.format_exc())
        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接
        return -1
    else:
        conn.commit()  # 提交事务
        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接
        return cursor.rowcount  # 返回笔数


if __name__ == '__main__':
    Logger = stocktools.mylogs.logger #  创建日志对象
    st_code = 'sz300348'
    Logger.info("股票监控启动中....")

    #exit(1)
    while True:

        ret = get_stock_information(st_code)
        if ret < 0:
            Logger.error("监控出错!返回值=" % ret)
            exit(ret)
        time.sleep(10)
