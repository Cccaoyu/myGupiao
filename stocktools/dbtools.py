import pymysql


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
    return connect


# 执行sql
def sqlr(sel, args=None):
    """
    执行sql语句
    :param sel: sql语句
    :param args: sql语句条件
    :return: 失败返回 -1 ; 成功返回笔数
    """

    conn = connect_db()  # 连接数据库
    cursor = conn.cursor()  # 获取游标

    try:
        cursor.execute(sel, args)  # 执行sql
    except Exception as e:
        conn.rollback()  # 抛出异常 回滚事物
        print("事务处理失败：", e)
        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接
        return -1
    else:
        conn.commit()  # 提交事务
        cursor.close()  # 关闭游标
        conn.close()  # 关闭连接
        return cursor.rowcount  # 返回笔数
