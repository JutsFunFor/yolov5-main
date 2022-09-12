import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from postgreSQL import SQLogger
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from accessify import private, protected


class SQLBase:
    def __init__(self):
        assert os.path.exists("config.json")
        with open("config.json", 'r') as file:
            config = json.load(file)

        if os.name == 'nt':
            self.usr = 'postgres'
            self.pwd = '3vn4ssps'
            self.host = 'localhost'
            self.dbname = 'lamoda1_17'
        else:
            self.usr = config["yolov5_inference"]["usr"]
            self.pwd = config["yolov5_inference"]["pwd"]
            self.host = config["yolov5_inference"]["host"]
            self.dbname = config["yolov5_inference"]["dbname"]

        self.conn = psycopg2.connect(dbname='postgres', user=self.usr, password=self.pwd, host=self.host)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()


    def get_dbase_list(self):
        self.cursor.execute(f"""
        SELECT datname
        FROM pg_database;
        """)
        return [x[0] for x in self.cursor.fetchall()]

    def set_conn_dbase(self, dbname):
        self.conn = psycopg2.connect(dbname=dbname, user=self.usr, password=self.pwd, host=self.host)
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.conn.cursor()

    def get_tables(self):
        self.cursor.execute(f"""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public';""")
        return [items[0] for items in self.cursor.fetchall()]

    def get_columns(self, table_name):
        assert isinstance(table_name, str)
        assert table_name in self.get_tables()

        self.cursor.execute(f"""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = '{table_name}';""")
        return [items[0] for items in self.cursor.fetchall()]

    def get_data(self, stats=True):
        table_name = self.dbname + '_stats' if stats else self.dbname + '_dur'
        columns = self.get_columns(table_name)
        self.cursor.execute(f"""SELECT * FROM {table_name};""")
        data = pd.DataFrame(self.cursor.fetchall(), columns=columns)
        return data


class Analytics(SQLBase):

    parser = argparse.ArgumentParser()
    parser.add_argument('--dist_menu')
    parser.add_argument('--nozzle_miss')
    parser.add_argument('--all')
    args = parser.parse_args()


    def __int__(self):
        # self.set_conn_dbase(self.dbname)
        self.stats_filename = 'stats.json'
        super().__init__()

    def show_stats(self):
        self.set_conn_dbase(self.dbname)
        dur_data = self.get_data(False).iloc[:, 2:]
        stats_data = self.get_data(True).iloc[:, 2:]
        print(f"[INFO] Duration data stats: ")
        print(dur_data.describe())
        print(' ')
        print(f"[INFO] Data stats: ")
        print(stats_data.describe())


    def get_real_dist_menu_item(self):
        """Average real_distance grouped by menu_item_id"""
        self.set_conn_dbase(self.dbname)
        stats_data = self.get_data(True)

        real_distance = stats_data[stats_data['real_distance_mm'] != -1].groupby('menu_item_id')[["real_distance_mm", "coffee_score"]].mean()
        miss_item = stats_data[stats_data['real_distance_mm'] == -1].groupby('menu_item_id').real_distance_mm.count()

        miss_item.name = "miss_item"
        real_distance = real_distance.merge(miss_item, how='left', on='menu_item_id')

        print(f"Menu Item ID Stats: ")
        print(real_distance)
        print("------------------------------------------------------------------------------------")

    def get_nozzle_miss_percent(self):
        """Percent of miss classifications grouped by nozzle_id"""
        self.set_conn_dbase(self.dbname)
        stats_data = self.get_data(True)
        missclass_series = stats_data[stats_data['real_distance_mm'] == -1].groupby(
            'nozzle_id').real_distance_mm.count()


        missclass_series.rename('Miss %')
        missclass_series = missclass_series.apply(lambda x: x/stats_data.shape[0] * 100)

        if missclass_series.shape[0] == 0:
            print(f"No miss classifications yet. Total number of images processed: {stats_data.shape[0]}")

        print("Nozzle Miss Classification %")
        print(missclass_series)
        print("------------------------------------------------------------------------------------")

        # # print(missclass_series.index[0], missclass_series)
        # if missclass_series.shape[0] >= 2:
        #     print(f"Nozzle 0 miss classification: {missclass_series[0] / stats_data.shape[0] * 100:.2f} %")
        #     print(f'Nozzle 1 miss classification: {missclass_series[1] / stats_data.shape[0] * 100:.2f} %')
        #     print(f"Total miss classification: {missclass_series.sum() / stats_data.shape[0] * 100:.2f} %")
        # elif missclass_series.shape[0] == 1:
        #     print(f"Nozzle {missclass_series.index[0]} miss classification: {missclass_series[0] / stats_data.shape[0] * 100:.2f} %")
        # else:
        #     print(f"No miss classifications yet. Total number of images processed: {stats_data.shape[0]}")
        #     print("------------------------------------------------------------------------------------")

    def get_mean_time_stats(self):
        """Mean inference, save image and total time"""
        self.set_conn_dbase(self.dbname)
        dur_data = self.get_data(False)

        capture_mean = dur_data['capture_duration'].mean()
        inference_mean = dur_data['inference_duration'].mean()
        save_img_mean = dur_data['save_img_duration'].mean()
        total_time_mean = dur_data['total_time'].mean()

        index_col = ["Capture time, s", "Inference time, s:", "Save image  time, s:", "Total time, s:"]
        time_column = np.array([capture_mean, inference_mean, save_img_mean, total_time_mean])
        stats_series = pd.Series(time_column, index=index_col, name="Average Time Statistic")
        print(stats_series.name)
        print(stats_series)
        print("------------------------------------------------------------------------------------")

    def main(self):

        if self.args.dist_menu:
            self.get_real_dist_menu_item()
        if self.args.nozzle_miss:
            self.get_nozzle_miss_percent()
        if self.args.all:
            self.get_real_dist_menu_item()
            self.get_nozzle_miss_percent()
            self.get_mean_time_stats()


if __name__ == '__main__':

    a = Analytics()
    a.main()

