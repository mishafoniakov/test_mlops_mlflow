import redis
from airflow.hooks.base import BaseHook
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook

class MLFlowEngines:

    @property
    def get_redis(self):
        conn = BaseHook.get_connection("redis_default")
        return redis.from_url(conn.get_uri())

    @property
    def get_clickhouse(self):
        return ClickHouseHook(clickhouse_conn_id="clickhouse_default")

    def get_pandas_df(self, sql: str):
        return self.get_clickhouse.get_conn().query_dataframe(sql)