import sqlite3
from collections import defaultdict


class Store:
    def __init__(self, database_filename):
        self.database_connection = sqlite3.connect(database_filename)
        self.database_connection.row_factory = sqlite3.Row
        cur = self.database_connection.cursor()
        cur.execute(
            "CREATE TABLE metric(id TEXT, title TEXT, description TEXT, PRIMARY KEY(id))"
        )
        cur.execute(
            "CREATE TABLE observation(metric_id TEXT, id TEXT, value_amount TEXT, value_currency TEXT, PRIMARY KEY(metric_id, id))"
        )
        cur.execute(
            "CREATE TABLE dimension(metric_id TEXT, observation_id TEXT, key TEXT, value TEXT, PRIMARY KEY(metric_id, observation_id, key))"
        )
        self.database_connection.commit()

    def add_metric_json(self, data: dict):
        # TODO check for id clash
        cur = self.database_connection.cursor()
        cur.execute(
            "INSERT INTO metric (id, title, description) VALUES (?, ?, ?)",
            (
                data.get("id"),
                data.get("title"),
                data.get("description"),
            ),
        )
        for observation in data["observations"]:
            cur.execute(
                "INSERT INTO observation (metric_id, id, value_amount, value_currency) VALUES (?, ?, ?, ?)",
                (
                    data.get("id"),
                    observation.get("id"),
                    observation.get("value", {}).get("amount"),
                    observation.get("value", {}).get("currency"),
                ),
            )
            for dimension_key, dimension_value in observation.get(
                "dimensions", {}
            ).items():
                cur.execute(
                    "INSERT INTO dimension (metric_id, observation_id, key, value) VALUES (?, ?, ?, ?)",
                    (
                        data.get("id"),
                        observation.get("id"),
                        dimension_key,
                        dimension_value,
                    ),
                )
        self.database_connection.commit()

    def get_metric(self, metric_id):
        return Metric(self, metric_id)


class Metric:
    def __init__(self, store: Store, metric_id: str):
        self.store = store
        self.metric_id = metric_id
        # TODO error if metric does not exist

    def get_observation_list(self):
        return ObservationList(self)


class ObservationList:
    def __init__(self, metric: Metric):
        self.metric: Metric = metric
        self.store: Store = metric.store
        self.filter_by_dimensions: dict = {}

    def filter_by_dimension(self, dimension_key: str, dimension_value: str):
        self.filter_by_dimensions[dimension_key] = {"value": dimension_value}

    def get_data(self):
        cur = self.store.database_connection.cursor()

        params: dict = {"metric_id": self.metric.metric_id}

        where: list = ["o.metric_id = :metric_id"]

        joins: list = []

        dimension_join_count = 0

        for dimension_key, dimension_filter in self.filter_by_dimensions.items():
            dimension_join_count += 1
            table_alias = "dimension_filter_" + str(dimension_join_count)
            joins.append(
                " JOIN dimension AS {table_alias} ON {table_alias}.metric_id=o.metric_id AND {table_alias}.observation_id=o.id".format(
                    table_alias=table_alias
                )
            )
            where.append(
                " {table_alias}.key=:{table_alias}key".format(table_alias=table_alias)
            )
            params[table_alias + "key"] = dimension_key
            where.append(
                " {table_alias}.value=:{table_alias}value".format(
                    table_alias=table_alias
                )
            )
            params[table_alias + "value"] = dimension_filter["value"]

        sql: str = (
            "SELECT o.* FROM observation AS o "
            + " ".join(joins)
            + " WHERE "
            + " AND ".join(where)
            + " ORDER BY o.id ASC"
        )

        cur.execute(sql, params)

        out = []
        for result in cur.fetchall():
            out.append(Observation(self.metric, result))
        return out

    def get_data_by_dimension(self, dimension_key: str):
        out = defaultdict(list)
        for observation in self.get_data():
            dimensions: dict = observation.get_dimensions()
            if dimensions.get(dimension_key):
                out[dimensions.get(dimension_key)].append(observation)
        return out


class Observation:
    def __init__(self, metric: Metric, observation_row_data):
        self.metric: Metric = metric
        self.store: Store = metric.store
        self.observation_row_data = observation_row_data

    def get_dimensions(self):
        cur = self.store.database_connection.cursor()

        cur.execute(
            "SELECT dimension.key, dimension.value FROM dimension WHERE metric_id=? AND observation_id=?",
            (self.metric.metric_id, self.observation_row_data["id"]),
        )

        out = {}
        for result in cur.fetchall():
            out[result["key"]] = result["value"]
        return out

    def get_value_amount(self):
        return self.observation_row_data["value_amount"]
