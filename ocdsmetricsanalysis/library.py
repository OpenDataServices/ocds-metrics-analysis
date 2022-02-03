import copy
import sqlite3
from collections import defaultdict
from typing import Optional, Union

from ocdsmetricsanalysis.exceptions import MetricNotFoundException


class Store:
    def __init__(self, database_filename):
        self._database_connection = sqlite3.connect(database_filename)
        self._database_connection.row_factory = sqlite3.Row
        cur = self._database_connection.cursor()
        cur.execute(
            "CREATE TABLE metric(id TEXT, title TEXT, description TEXT, PRIMARY KEY(id))"
        )
        cur.execute(
            "CREATE TABLE observation("
            + "metric_id TEXT, "
            + "id TEXT, "
            + "value_amount TEXT, "
            + "value_currency TEXT, "
            + "measure TEXT, "
            + "unit_name TEXT, "
            + "unit_scheme TEXT, "
            + "unit_id TEXT, "
            + "unit_uri TEXT, "
            + "PRIMARY KEY(metric_id, id)"
            + ")"
        )
        cur.execute(
            "CREATE TABLE dimension(metric_id TEXT, observation_id TEXT, key TEXT, value TEXT, PRIMARY KEY(metric_id, observation_id, key))"
        )
        self._database_connection.commit()

    def add_metric(self, id: str, title: str, description: str):
        # TODO check for id clash
        cur = self._database_connection.cursor()
        cur.execute(
            "INSERT INTO metric (id, title, description) VALUES (?, ?, ?)",
            (
                id,
                title,
                description,
            ),
        )
        self._database_connection.commit()

    def add_metric_json(self, data: dict):
        # TODO check for id clash
        cur = self._database_connection.cursor()
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
                "INSERT INTO observation "
                + "(metric_id, id, value_amount, value_currency, measure, unit_name, unit_scheme, unit_id, unit_uri) "
                + "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    data.get("id"),
                    observation.get("id"),
                    observation.get("value", {}).get("amount"),
                    observation.get("value", {}).get("currency"),
                    observation.get("measure"),
                    observation.get("unit", {}).get("name"),
                    observation.get("unit", {}).get("scheme"),
                    observation.get("unit", {}).get("id"),
                    observation.get("unit", {}).get("uri"),
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
        self._database_connection.commit()

    def get_metric(self, metric_id):
        return Metric(self, metric_id)

    def get_metrics(self):
        cur = self._database_connection.cursor()
        cur.execute(
            "SELECT id FROM metric ORDER BY id ASC",
            [],
        )
        return [Metric(self, m["id"]) for m in cur.fetchall()]


class Metric:
    def __init__(self, store: Store, metric_id: str):
        self._store = store
        self._metric_id = metric_id

        cur = self._store._database_connection.cursor()
        cur.execute(
            "SELECT metric.* FROM metric WHERE id=?",
            [metric_id],
        )
        self._metric_row = cur.fetchone()
        if self._metric_row is None:
            raise MetricNotFoundException("No such metric found")

    def get_observation_list(self):
        return ObservationList(self)

    def get_id(self) -> str:
        return self._metric_row["id"]

    def add_observation(
        self,
        id: str,
        value_amount: Optional[str] = None,
        value_currency: Optional[str] = None,
        measure: Optional[str] = None,
        dimensions: dict = {},
        unit_name: Optional[str] = None,
        unit_scheme: Optional[str] = None,
        unit_id: Optional[str] = None,
        unit_uri: Optional[str] = None,
    ):
        # TODO check for id clash
        cur = self._store._database_connection.cursor()
        cur.execute(
            "INSERT INTO observation (metric_id, id, value_amount, value_currency, measure, unit_name, unit_scheme, unit_id, unit_uri) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self._metric_id,
                id,
                value_amount,
                value_currency,
                measure,
                unit_name,
                unit_scheme,
                unit_id,
                unit_uri,
            ),
        )
        for dimension_key, dimension_value in dimensions.items():
            cur.execute(
                "INSERT INTO dimension (metric_id, observation_id, key, value) VALUES (?, ?, ?, ?)",
                (
                    self._metric_id,
                    id,
                    dimension_key,
                    dimension_value,
                ),
            )
        self._store._database_connection.commit()

    def add_aggregate_observations(
        self,
        data_rows: list,
        idx_to_aggregate: Union[str, int],
        answer_dimension_key: str,
        idx_to_dimensions: dict = {},
        unit_name: Optional[str] = None,
        unit_scheme: Optional[str] = None,
        unit_id: Optional[str] = None,
        unit_uri: Optional[str] = None,
        create_observations_from_dimensions_exponentially: bool = False,
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
        if create_observations_from_dimensions_exponentially:
            for idx, dimension in idx_to_dimensions.items():
                possible_answers = sorted(
                    list(set([d[idx] for d in data_rows if d[idx]]))
                )
                new_observations = []
                for observation in observations:
                    for a in possible_answers:
                        new_observation = copy.deepcopy(observation)
                        new_observation["dimensions"][dimension["dimension_name"]] = a
                        new_observation["extra_dimension_definitions"][idx] = dimension
                        new_observations.append(new_observation)
                observations.extend(new_observations)
        else:
            new_observations = []
            for idx, dimension in idx_to_dimensions.items():
                possible_answers = sorted(
                    list(set([d[idx] for d in data_rows if d[idx]]))
                )
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
                measure=observation["count"],
                dimensions=observation["dimensions"],
                unit_name=unit_name,
                unit_scheme=unit_scheme,
                unit_id=unit_id,
                unit_uri=unit_uri,
            )

    def get_json(self):
        out = {
            "id": self._metric_row["id"],
            "title": self._metric_row["title"],
            "description": self._metric_row["description"],
            "observations": [],
        }

        observation_list = self.get_observation_list()
        for observation in observation_list.get_data():
            observation_data = {
                "id": observation.get_id(),
                "dimensions": observation.get_dimensions(),
            }
            if observation.has_value():
                observation_data["value"] = {
                    "amount": observation.get_value_amount(),
                    "currency": observation.get_value_currency(),
                }
            if observation.has_measure():
                observation_data["measure"] = observation.get_measure()
            if observation.has_unit():
                observation_data["unit"] = {
                    "name": observation.get_unit_name(),
                    "scheme": observation.get_unit_scheme(),
                    "id": observation.get_unit_id(),
                    "uri": observation.get_unit_uri(),
                }
            out["observations"].append(observation_data)

        return out

    def get_dimension_keys(self):
        cur = self._store._database_connection.cursor()
        cur.execute(
            "SELECT key FROM dimension WHERE metric_id=? GROUP BY key ORDER BY key ASC",
            [self._metric_id],
        )
        return [d["key"] for d in cur.fetchall()]


class ObservationList:
    def __init__(self, metric: Metric):
        self._metric: Metric = metric
        self._store: Store = metric._store
        self._filter_by_dimensions: dict = {}
        self._filter_by_dimensions_not_set: list = []

    def filter_by_dimension(self, dimension_key: str, dimension_value: str):
        self._filter_by_dimensions[dimension_key] = {"value": dimension_value}

    def filter_by_dimension_not_set(self, dimension_key: str):
        self._filter_by_dimensions_not_set.append(dimension_key)

    def get_data(self):
        cur = self._store._database_connection.cursor()

        params: dict = {"metric_id": self._metric._metric_id}

        where: list = ["o.metric_id = :metric_id"]

        joins: list = []

        dimension_join_count = 0

        for dimension_key, dimension_filter in self._filter_by_dimensions.items():
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

        for dimension_key in list(set(self._filter_by_dimensions_not_set)):
            dimension_join_count += 1
            table_alias = "dimension_filter_" + str(dimension_join_count)
            joins.append(
                " LEFT JOIN dimension AS {table_alias} ON {table_alias}.metric_id=o.metric_id AND {table_alias}.observation_id=o.id AND {table_alias}.key = :{table_alias}key".format(
                    table_alias=table_alias
                )
            )
            params[table_alias + "key"] = dimension_key
            where.append(" {table_alias}.key IS NULL".format(table_alias=table_alias))

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
            out.append(Observation(self._metric, result))
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
        self._metric: Metric = metric
        self._store: Store = metric._store
        self._observation_row_data = observation_row_data

    def get_dimensions(self):
        cur = self._store._database_connection.cursor()

        cur.execute(
            "SELECT dimension.key, dimension.value FROM dimension WHERE metric_id=? AND observation_id=?",
            (self._metric._metric_id, self._observation_row_data["id"]),
        )

        out = {}
        for result in cur.fetchall():
            out[result["key"]] = result["value"]
        return out

    def has_value(self) -> bool:
        return (
            self._observation_row_data["value_amount"]
            or self._observation_row_data["value_currency"]
        )

    def get_value_amount(self) -> str:
        return self._observation_row_data["value_amount"]

    def get_value_currency(self) -> str:
        return self._observation_row_data["value_currency"]

    def has_unit(self) -> bool:
        return (
            self._observation_row_data["unit_name"]
            or self._observation_row_data["unit_scheme"]
            or self._observation_row_data["unit_id"]
            or self._observation_row_data["unit_uri"]
        )

    def get_unit_name(self) -> str:
        return self._observation_row_data["unit_name"]

    def get_unit_scheme(self) -> str:
        return self._observation_row_data["unit_scheme"]

    def get_unit_id(self) -> str:
        return self._observation_row_data["unit_id"]

    def get_unit_uri(self) -> str:
        return self._observation_row_data["unit_uri"]

    def has_measure(self) -> bool:
        return bool(self._observation_row_data["measure"])

    def get_measure(self) -> str:
        return self._observation_row_data["measure"]

    def get_id(self) -> str:
        return self._observation_row_data["id"]
