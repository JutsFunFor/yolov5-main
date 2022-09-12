import json
import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class SQLogger:
    """
        Dbname - testdb
        usr - postgres
        pwd - 3vn4ssps
        host - localhost
    """

    def __init__(self, dbname, usr, pwd, host, autocommit_flag=False):
        self.dbname = dbname
        self.usr = usr
        self.pwd = pwd
        self.host = host
        self.__conn = psycopg2.connect(dbname='postgres', user=self.usr, password=self.pwd, host=self.host)
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.__cursor = self.__conn.cursor()
        # self.autocommit_flag = autocommit_flag


    def set_conn_dbase(self, dbase_name):
        self.__conn = psycopg2.connect(dbname=dbase_name, user=self.usr, password=self.pwd, host=self.host)
        self.__conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.__cursor = self.__conn.cursor()

    def set_autocommit(self, flag):
        self.__conn.autocommit = flag

    def set_dict_cursor(self) -> None:
        self.__cursor = self.__conn.cursor(cursor_factory=DictCursor)

    def __close(self):
        self.__cursor.close()
        self.__conn.close()

    def get_tables(self):
        self.__cursor.execute(f"""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public';""")
        return [items[0] for items in self.__cursor.fetchall()]

    def get_columns(self, table_name):
        assert isinstance(table_name, str)
        assert table_name in self.get_tables()

        self.__cursor.execute(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = '{table_name}';""")
        return [items[0] for items in self.__cursor.fetchall()]

    def get_table_id(self, table_name):
        table_name_id = str(table_name + '_id')
        self.__cursor.execute(
            f"""
            SELECT max({table_name_id}) FROM {table_name};
            """)
        return self.__cursor.fetchall()[0][0]

    def __write_stats_from_json(self, json_file, table, old=False):

        with open(json_file, 'r') as file:
            for id, string in enumerate(file):
                item = f'{string[1:-2]}'
                item = item.replace("'", r'"')

                record = json.loads(item)
                assert type(record) == dict

                #### FOR OLD VERSION
                if old:
                    if record["Detection"]:
                        if len(record['Detection']) == 2:
                            self.__cursor.execute(
                                f"""
                            INSERT INTO {table}
                            VALUES 
                            ({id},
                             '{record["Detection"]["Coffee"]["DateTime"]}',
                             '{record["Detection"]["Coffee"]["OrderID"]}',
                             '{record["Detection"]["Coffee"]["MenuItemId"]}',
                             {record["Detection"]["Coffee"]["OrderNumber"]},
                             {record["Detection"]["Coffee"]["NozzleID"]},
                             {record["Detection"]["Coffee"]["Ymax"]},
                             {record["Detection"]["CupTop"]["Ymax"]},
                             {record["Detection"]["Coffee"]["Score"]},
                             {record["Detection"]["CupTop"]["Score"]},
                             {record["RealDistance"]}
                             );""")
                        elif "Coffee" in record["Detection"].keys():
                            self.__cursor.execute(
                                f"""
                            INSERT INTO {table}
                            VALUES 
                            ({id},
                             '{record["Detection"]["Coffee"]["DateTime"]}',
                             '{record["Detection"]["Coffee"]["OrderID"]}',
                             '{record["Detection"]["Coffee"]["MenuItemId"]}',
                             {record["Detection"]["Coffee"]["OrderNumber"]},
                             {record["Detection"]["Coffee"]["NozzleID"]},
                             {record["Detection"]["Coffee"]["Ymax"]},
                             NULL,
                             {record["Detection"]["Coffee"]["Score"]},
                             NULL,
                             {record["RealDistance"]}
                             );""")
                        elif "CupTop" in record["Detection"].keys():
                            self.__cursor.execute(
                                f"""
                            INSERT INTO {table}
                            VALUES 
                            ({id},
                             '{record["Detection"]["CupTop"]["DateTime"]}',
                             '{record["Detection"]["CupTop"]["OrderID"]}',
                             '{record["Detection"]["CupTop"]["MenuItemId"]}',
                             {record["Detection"]["CupTop"]["OrderNumber"]},
                             {record["Detection"]["CupTop"]["NozzleID"]},
                             NULL,
                             {record["Detection"]["CupTop"]["Ymax"]},
                             NULL,
                             {record["Detection"]["CupTop"]["Score"]},
                             {record["RealDistance"]}
                             );""")
                    else:
                        self.__cursor.execute(
                            f"""
                        INSERT INTO {table}
                        VALUES 
                        ({id},
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         NULL,
                         {record["RealDistance"]}
                         );""")
                else:
                    #### FOR NEW VERSION
                    if record["Detection"]["Coffee"] and record["Detection"]["CupTop"]:
                        self.__cursor.execute(f"""
                        INSERT INTO {table}
                        VALUES 
                        ({id},
                         '{record["DateTime"]}',
                         '{record["OrderID"]}',
                         '{record["MenuItemId"]}',
                         {record["OrderNumber"]},
                         {record["NozzleID"]},
                         {record["Detection"]["Coffee"]["Ymax"]},
                         {record["Detection"]["CupTop"]["Ymax"]},
                         {record["Detection"]["Coffee"]["Score"]},
                         {record["Detection"]["CupTop"]["Score"]},
                         {record["RealDistance"]}
                         );""")
                    elif record["Detection"]["Coffee"]:
                        self.__cursor.execute(
                        f"""
                        INSERT INTO {table}
                        VALUES 
                        ({id},
                        '{record["DateTime"]}',
                        '{record["OrderID"]}',
                        '{record["MenuItemId"]}',
                        {record["OrderNumber"]},
                        {record["NozzleID"]},
                        {record["Detection"]["Coffee"]["Ymax"]},
                        NULL,
                        {record["Detection"]["Coffee"]["Score"]},
                        NULL,
                        {record["RealDistance"]}
                        );
                        """)
                    elif record["Detection"]["CupTop"]:
                        self.__cursor.execute(
                            f"""
                        INSERT INTO {table}
                        VALUES 
                        ({id},
                        '{record["DateTime"]}',
                        '{record["OrderID"]}',
                        '{record["MenuItemId"]}',
                        {record["OrderNumber"]},
                        {record["NozzleID"]},
                        NULL,
                        {record["Detection"]["CupTop"]["Ymax"]},
                        NULL,
                        {record["Detection"]["CupTop"]["Score"]},
                        {record["RealDistance"]}
                        );
                        """)
                    else:
                        self.__cursor.execute(
                            f"""
                        INSERT INTO {table}
                        VALUES 
                        ({id},
                        '{record["DateTime"]}',
                        '{record["OrderID"]}',
                        '{record["MenuItemId"]}',
                        {record["OrderNumber"]},
                        {record["NozzleID"]},
                        NULL,
                        NULL,
                        NULL,
                        NULL,
                        {record["RealDistance"]}
                        );
                        """)

    def write_dur_stats(self, dbase_name, packet) -> None:

        self.set_conn_dbase(dbase_name)
        table_name = dbase_name + '_dur'

        if isinstance(packet, str):
            packet = json.loads(packet)

        assert isinstance(table_name, str)
        assert isinstance(packet, dict)
        assert table_name in self.get_tables()

        table_last_id = self.get_table_id(table_name)

        ### Check next item_id to write query
        if isinstance(table_last_id, int) and table_last_id != 0:
            table_id = table_last_id + 1
        elif isinstance(table_last_id, int) and table_last_id == 0:
            table_id = 1
        elif table_last_id is None:
            table_id = 0
        else:
            raise AssertionError


        self.__cursor.execute(f"""
                    INSERT INTO {table_name}
                    VALUES 
                    ({table_id},
                     '{packet["DateTime"]}',
                     '{packet["OrderId"]}',
                     '{packet["MenuItemId"]}',
                     {packet["OrderNumber"]},
                     {packet["NozzleId"]},
                     {packet["Capture_duration"]},
                     {packet["Inference_duration"]},
                     {packet["Save_img_duration"]},
                     {packet["Total_time"]},
                     {packet["RealDistance"]});""")


    def write_stats(self, dbase_name, packet) -> None:

        self.set_conn_dbase(dbase_name)
        table_name = dbase_name + '_stats'
        if isinstance(packet, str):
            packet = json.loads(packet)

        assert isinstance(table_name, str)
        assert isinstance(packet, dict)
        assert table_name in self.get_tables()

        table_last_id = self.get_table_id(table_name)

        ### Check next item_id to write query
        if isinstance(table_last_id, int) and table_last_id != 0:
            table_id = table_last_id + 1
        elif isinstance(table_last_id, int) and table_last_id == 0:
            table_id = 1
        elif table_last_id is None:
            table_id = 0
        else:
            raise AssertionError

        if packet["Detection"]["Coffee"] and packet["Detection"]["CupTop"]:
            self.__cursor.execute(f"""
            INSERT INTO {table_name}
            VALUES 
            ({table_id},
             '{packet["DateTime"]}',
             '{packet["OrderId"]}',
             '{packet["MenuItemId"]}',
             {packet["OrderNumber"]},
             {packet["NozzleId"]},
             {packet["Detection"]["Coffee"]["Ymax"]},
             {packet["Detection"]["CupTop"]["Ymax"]},
             {packet["Detection"]["Coffee"]["Score"]},
             {packet["Detection"]["CupTop"]["Score"]},
             {packet["RealDistance"]});""")
        elif packet["Detection"]["Coffee"]:
            self.__cursor.execute(f"""
            INSERT INTO {table_name}
            VALUES 
            ({table_id},
             '{packet["DateTime"]}',
             '{packet["OrderId"]}',
             '{packet["MenuItemId"]}',
             {packet["OrderNumber"]},
             {packet["NozzleId"]},
             {packet["Detection"]["Coffee"]["Ymax"]},
             NULL,
             {packet["Detection"]["Coffee"]["Score"]},
             NULL,
             {packet["RealDistance"]});""")
        elif packet["Detection"]["CupTop"]:
            self.__cursor.execute(f"""
            INSERT INTO {table_name}
            VALUES 
            ({table_id},
             '{packet["DateTime"]}',
             '{packet["OrderId"]}',
             '{packet["MenuItemId"]}',
             {packet["OrderNumber"]},
             {packet["NozzleId"]},
             NULL,
             {packet["Detection"]["CupTop"]["Ymax"]},
             NULL,
             {packet["Detection"]["CupTop"]["Score"]},
             {packet["RealDistance"]});""")
        else:
            self.__cursor.execute(f"""
            INSERT INTO {table_name}
            VALUES 
            ({table_id},
             '{packet["DateTime"]}',
             '{packet["OrderId"]}',
             '{packet["MenuItemId"]}',
             {packet["OrderNumber"]},
             {packet["NozzleId"]},
             NULL,
             NULL,
             NULL,
             NULL,
             {packet["RealDistance"]});""")


    def create_database(self, dbase_name):
        try:
            ### Check if exists
            self.__cursor.execute(f"""
            SELECT * FROM pg_database
            WHERE datname = '{dbase_name}'
            """)
            if not self.__cursor.fetchall():
                ### Create dbase
                self.__cursor.execute(f"""
                CREATE DATABASE {dbase_name}
                    WITH
                    OWNER = postgres
                    ENCODING = 'UTF-8'
                    CONNECTION LIMIT = -1;""")
        except Exception as err:
            print(err)


    def get_dbase_list(self):
        self.__cursor.execute(f"""
        SELECT datname
        FROM pg_database;
        """)
        return [x[0] for x in self.__cursor.fetchall()]


    def drop_database(self, dbase_name):
        try:
            ### Connect to different database
            dbase_list = self.get_dbase_list()
            if dbase_name in dbase_list:
                dbase_list.remove(dbase_name)
                self.set_conn_dbase(dbase_list[0])
            else:
                self.set_conn_dbase(dbase_list[0])

            ### Terminate connection
            self.__cursor.execute(f"""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname='{dbase_name}'""")
            ### Drop database
            self.__cursor.execute(f"""
            DROP DATABASE {dbase_name}
            """)
            print(f"Database '{dbase_name}' successfully dropped ")
        except Exception as err:
            print(err)


    def create_dur_table(self, dbase_name):

        table_name = dbase_name + '_dur'

        ### Set connection to current dbase
        self.set_conn_dbase(dbase_name=dbase_name)

        self.__cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            (
            {table_name}_id integer NOT NULL PRIMARY KEY,
            datetime timestamp,
            order_id varchar(128),
            menu_item_id varchar(128),
            order_number smallint,
            nozzle_id smallint,
            capture_duration real,
            inference_duration real,
            save_img_duration real,
            total_time real,
            real_distance_mm real
            );""")

    def create_stats_table(self, dbase_name):

        table_name = dbase_name + '_stats'
        self.set_conn_dbase(dbase_name=dbase_name)
        self.__cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            (
            {table_name}_id int NOT NULL PRIMARY KEY,
            datetime timestamp, 
            order_id varchar(128),
            menu_item_id varchar(128),
            order_number smallint,
            nozzle_id smallint,
            coffee_y_max real,
            cup_top_y_max real,
            coffee_score real,
            cup_top_score real,
            real_distance_mm real
            );""")


    def delete_table(self, table_name, restrict_flag=False):
        if restrict_flag:
            self.__cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name} RESTRICT;
            """)
        else:
            self.__cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name};
            """)

    def get_data(self, stats=True):
        table_name = self.dbname + '_stats' if stats else self.dbname + '_dur'
        columns = self.get_columns(table_name)
        self.__cursor.execute(f"""SELECT * FROM {table_name};""")
        data = pd.DataFrame(self.__cursor.fetchall(), columns=columns)
        return data


if __name__ == '__main__':

    #packet = {'Detection': {'CupTop': {'OrderID': '01G1KDA7PEV4ENSXFFHGQGK229', 'OrderNumber': '510', 'NozzleID': '1', 'MenuItemId': '01ESM7PEWGABK0YFX74JCXP1KF', 'Xmax': '457.0', 'Ymax': '57.0', 'Ymin': '339.0', 'ElapsedTime': '4.97', 'DateTime': '2022-04-26 20:06:26.453562', 'Score': '0.61'}, 'Coffee': {'OrderID': '01G1KDA7PEV4ENSXFFHGQGK229', 'OrderNumber': '510', 'NozzleID': '1', 'MenuItemId': '01ESM7PEWGABK0YFX74JCXP1KF', 'Xmax': '411.0', 'Ymax': '97.0', 'Ymin': '321.0', 'ElapsedTime': '4.97', 'DateTime': '2022-04-26 20:06:26.454660', 'Score': '0.67'}}, 'RealDistance': '9.47'}
    # print(packet['Detection'].keys())
    packet = {'Detection': {'Coffee': {}, 'CupTop': {'Xmax': '600.0', 'Ymax': '78.0', 'Ymin': '561.0', 'Score': '0.78'}}, 'OrderId': '01G36EZ4ZXE8HEXFP54NSJG9XF', 'OrderNumber': '901', 'NozzleId': '1', 'MenuItemId': '4RV06W3796RSWX1TW2C6CU', 'DateTime': '2022-05-16 15:56:13', 'Capture_duration': '3.19', 'Inference_duration': '2.78', 'Save_img_duration': '0.10', 'Total_time': '6.07', 'RealDistance': -1}
    dbname = 'complex1_18'
    usr = 'pi'
    pwd = '3vn4ssps'
    host = 'localhost'

    logger = SQLogger(dbname, usr, pwd, host, True)

    # logger.drop_database('abc')
    #logger.create_database(dbname)
    logger.set_conn_dbase(dbname)
    #logger.create_dur_table(dbname)
    #logger.create_stats_table(dbname)
    #
    #logger.write_dur_stats('abc', packet)
    #logger.write_stats('abc', packet)

    # logger.drop_database('abc')
    # logger.get_dbase_list()
    # logger.drop_database('abc')
    # logger.drop_database('abc')
    # logger.create_stats_table('abc_stats')
    table_list = logger.get_tables()
    data = logger.get_data(stats=False)
    print(data)
    print(table_list)

    #columns = logger.get_columns(table_list[-1])
    #print(columns)



    #logger.drop_database('abc')
    # table_id = logger.get_table_id(table_list[1])
    # print(type(table_id), table_id)

    # logger.write_stats(table_list[1], packet)

    # tlen = logger.get_table_len(table_list[-1])
    # print(type(tlen))
