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

    def insert_pandas_df(self, table: str, df):
        client = self.get_clickhouse.get_conn()
        columns = ", ".join(df.columns)
        # clickhouse-driver 0.2.x expects lists/tuples, not raw numpy columns
        payload = [
            tuple(
                v.to_pydatetime() if hasattr(v, "to_pydatetime") else v
                for v in row
            )
            for row in df.itertuples(index=False, name=None)
        ]
        client.execute(f"INSERT INTO {table} ({columns}) VALUES", payload)
