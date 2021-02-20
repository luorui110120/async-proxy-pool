import sqlite3
from qqwry import QQwry
from .config import(SQLITE3_FILENAME,
                    INIT_SCORE,MAX_SCORE,QQWRY_FILENAME,
    MIN_SCORE,
    INIT_SCORE,)


g_conn = sqlite3.connect(SQLITE3_FILENAME, check_same_thread=False)
class SQLite3Client:
    """
    代理池依赖了 Redis 数据库，使用了其`有序集合`的数据结构
    （可按分数排序，key 值不能重复）
    """

    def __init__(self, FILENAME=SQLITE3_FILENAME):
        self.conn = g_conn #sqlite3.connect(FILENAME)
        self.cursor = self.conn.cursor()
        self.wry = QQwry()
        self.wry.load_file(QQWRY_FILENAME)

    def add_proxy(self, proxy, score=INIT_SCORE):
        """
        新增一个代理，初始化分数 INIT_SCORE < MAX_SCORE，确保在
        运行完收集器后还没运行校验器就获取代理，导致获取到分数虽为 MAX_SCORE,
        但实际上确是未经验证，不可用的代理

        :param proxy: 新增代理
        :param score: 初始化分数
        """
        country = self.get_country(proxy)
        type = self.get_proxy_type(proxy)
        sql = "INSERT INTO Proxy (PROXY, TYPE, COUNTRY, SPEED, SCORE) VALUES('%s', '%s', '%s', %f, %d)"\
            % (proxy, type, country, 100.0, score)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception:
            pass

    def reduce_proxy_score(self, proxy):
        """
        验证未通过，分数减一

        :param proxy: 验证代理
        """
        sql = "select SCORE from Proxy where PROXY=='%s'" % proxy
        cur = self.cursor.execute(sql)
        value = cur.fetchone()
        score = int(value[0])
        if score and score > MIN_SCORE:
            score -= 1
            sql = "UPDATE Proxy set SCORE=%d where PROXY=='%s'" %(score, proxy)
        else:
            sql = "DELETE from Proxy where PROXY=='%s'" % proxy
        self.cursor.execute(sql)
        self.conn.commit()

    def increase_proxy_score(self, proxy):
        """
        验证通过，分数加一

        :param proxy: 验证代理
        """
        sql = "select SCORE from Proxy where PROXY=='%s'" % proxy
        cur = self.cursor.execute(sql)
        value = cur.fetchone()
        score = int(value[0])
        if score and score < MAX_SCORE:
            score += 1
            sql = "UPDATE Proxy set SCORE=%d where PROXY=='%s'" % (score, proxy)
        self.cursor.execute(sql)
        self.conn.commit()
    def update_proxy_speed(self, proxy, speed):
        try:
            sql = "UPDATE Proxy set SPEED=%f, TIME = datetime('now','localtime') where PROXY=='%s'" % (speed, proxy)
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception:
            return False
    def pop_proxy(self):
        """
        返回一个代理
        """
        # 第一次尝试取分数最高，也就是最新可用的代理
        sql = "SELECT PROXY FROM Proxy ORDER BY SCORE DESC LIMIT 1"
        cur = self.cursor.execute(sql)
        value = cur.fetchone()
        if value:
            return value[0]
        return 0


    def get_proxies(self, count=1):
        """
        返回指定数量代理，分数由高到低排序

        :param count: 代理数量
        """
        #print("count:%d" %count)
        sql = "SELECT PROXY FROM Proxy ORDER BY SCORE DESC LIMIT %d" % count
        cur = self.cursor.execute(sql)
        #print(cur.fetchall())
        for row in cur.fetchall():
            yield row[0]

    def count_all_proxies(self):
        """
        返回所有代理总数
        """
        sql = "SELECT COUNT(*) FROM Proxy"
        cur = self.cursor.execute(sql)
        value = cur.fetchone()
        if value:
            return value[0]
        return 0

    def count_score_proxies(self, score):
        """
        返回指定分数代理总数

        :param score: 代理分数
        """
        if 0 <= score <= 10:
            sql = "SELECT COUNT(*) FROM Proxy WHERE SCORE==%d" % score
            cur = self.cursor.execute(sql)
            value = cur.fetchone()
            if value:
                return value[0]
        return -1
    def get_score_proxies(self, score):
        """
        返回数据库的中制定的score的所有数据

        :param score: 代理分数
        """
        list = []
        sql = "SELECT PROXY FROM Proxy WHERE SCORE== %d" % score
        values = self.cursor.execute(sql)
        for row in values:
            list.append(row[0])
        return list

    def clear_proxies(self, score):
        """
        删除分数小于等于 score 的代理
        """
        if 0 <= score <= 10:
            sql = "DELETE from Proxy WHERE SCORE <= %d" % score
            self.cursor.execute(sql)
            self.conn.commit()
            return True
        return False

    def get_country(self, proxy):
        pro_split_list = proxy.split(':')
        ip = pro_split_list[1].strip('/')
        ipcountry = self.wry.lookup(ip)
        if ipcountry:
            return ipcountry[0]
        return None
    def get_proxy_type(self, proxy):
        pro_split_list = proxy.split(':')
        if pro_split_list[0].find('http') >=0:
            return pro_split_list[0]
        return None
    def all_proxies(self):
        """
        返回全部代理
        """
        list=[]
        sql = "SELECT PROXY FROM Proxy"
        values = self.cursor.execute(sql)
        for row in values:
            list.append(row[0])
        return list
    def __del__(self):
        self.conn.close()
# if __name__=='__main__':
#     #test_main(proxyAddressArray)
#     gou = SQLite3Client()
#     proxy_all_list = gou.get_proxies(1)
#     for proxy in proxy_all_list:
#         print(proxy)
#     print("pop: %s" % gou.pop_proxy())
#     #gou.clear_proxies(9)
#     print("count_score_proxies:%d" %gou.count_score_proxies(9))
#     print("count_all_proxies:%d" % gou.count_all_proxies())
#     proxy_val = 'http://103.199.159.177:40049'
#     #gou.increase_proxy_score(proxy_val)
#     gou.reduce_proxy_score(proxy_val)
#     #gou.add_proxy()