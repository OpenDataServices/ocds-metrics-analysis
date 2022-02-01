import copy
import sqlite3
from collections import defaultdict
from typing import Optional, Union

from ocdsmetricsanalysis.exceptions import MetricNotFoundException


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

    def add_metric(self, id: str, title: str, description: str):
        # TODO check for id clash
        cur = self.database_connection.cursor()
        cur.execute(
            "INSERT INTO metric (id, title, description) VALUES (?, ?, ?)",
            (
                id,
                title,
                description,
            ),
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

        cur = self.store.database_connection.cursor()
        cur.execute(
            "SELECT metric.* FROM metric WHERE id=?",
            [metric_id],
        )
        row = cur.fetchone()
        if row is None:
            raise MetricNotFoundException("No such metric found")

    def get_observation_list(self):
        return ObservationList(self)

    def add_observation(
        self,
        id: str,
        value_amount: Optional[str] = None,
        value_currency: Optional[str] = None,
        dimensions: dict = {},
    ):
        # TODO check for id clash
        cur = self.store.database_connection.cursor()
        cur.execute(
            "INSERT INTO observation (metric_id, id, value_amount, value_currency) VALUES (?, ?, ?, ?)",
            (
                self.metric_id,
                id,
                value_amount,
                value_currency,
            ),
        )
        for dimension_key, dimension_value in dimensions.items():
            cur.execute(
                "INSERT INTO dimension (metric_id, observation_id, key, value) VALUES (?, ?, ?, ?)",
                (
                    self.metric_id,
                    id,
                    dimension_key,
                    dimension_value,
                ),
            )
        self.store.database_connection.commit()

    def add_aggregate_observations(
        self,
        data_rows: list,
        idx_to_aggregate: Union[str, int],
        answer_dimension_key: str,
        idx_to_dimensions: dict = {},
    ):

        # ------------------------------- Get list of Observations
        # First, just the observations for possible answers
        possible_answers = sorted(
            list(set([d[idx_to_aggregate] for d in data_rows if d[idx_to_aggregate]]))
        )

        observations = [
            {
                "answer_value": a,
                "count": 0,
                "extra_dimension_definitions": {},
                "dimensions": {answer_dimension_key: a},
            }
            for a in possible_answers
        ]

        # Second, for every extra dimension add more observations
        for idx, dimension in idx_to_dimensions.items():
            possible_answers = sorted(list(set([d[idx] for d in data_rows if d[idx]])))
            new_observations = []
            for observation in observations:
                for a in possible_answers:
                    new_observation = copy.deepcopy(observation)
                    new_observation["dimensions"][dimension["dimension_name"]] = a
                    new_observation["extra_dimension_definitions"][idx] = dimension
                    new_observations.append(new_observation)
            observations.extend(new_observations)

        # ------------------------------- Process Data
        for data_row in data_rows:
            for observation in observations:
                # For every data row and every observation see if it matches - if so, increase count
                if observation["answer_value"] == data_row[idx_to_aggregate]:
                    increase_count = True
                    for d_idx, dimension in observation[
                        "extra_dimension_definitions"
                    ].items():
                        if (
                            data_row[d_idx]
                            != observation["dimensions"][dimension["dimension_name"]]
                        ):
                            increase_count = False
                    if increase_count:
                        observation["count"] += 1

        # ------------------------------- Save data to disk
        id = 0
        for observation in observations:
            id += 1
            self.add_observation(
                "%09d" % (id),
                value_amount=observation["count"],
                dimensions=observation["dimensions"],
            )


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
