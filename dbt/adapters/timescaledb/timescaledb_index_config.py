from dataclasses import dataclass

from dbt_common.utils.encoding import md5

from dbt.adapters.postgres.impl import PostgresIndexConfig


@dataclass
class TimescaleDBIndexConfig(PostgresIndexConfig):
    transaction_per_chunk: bool = False

    def render(self, relation) -> str:  # noqa: ANN001
        # We append the current timestamp to the index name because otherwise
        # the index will only be created on every other run. See
        # https://github.com/dbt-labs/dbt-core/issues/1945#issuecomment-576714925
        # for an explanation.
        inputs = self.columns + [
            relation.render(),
            str(self.unique),
            str(self.type),
            str(self.transaction_per_chunk),
        ]
        string = "_".join(inputs)
        return md5(string)
