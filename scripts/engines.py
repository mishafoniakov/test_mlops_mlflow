import os

import redis
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook

class MLFlowEngines:

    @property
    def get_redis(self):
        return redis.from_url(os.environ["REDIS_URL"])

    @property
    def get_clickhouse(self):
        return ClickHouseHook(clickhouse_conn_id="clickhouse_default")

    def get_pandas_df(self, sql: str):
        return self.get_clickhouse.get_conn().query_dataframe(sql)