from dataclasses import dataclass
from datetime import datetime

from dbt.adapters.postgres.impl import PostgresIndexConfig
from dbt.utils import md5


@dataclass
class TimescaleDBIndexConfig(PostgresIndexConfig):
    transaction_per_chunk: bool = False

    def render(self, relation) -> str:  # noqa: ANN001
        # We append the current timestamp to the index name because otherwise
        # the index will only be created on every other run. See
        # https://github.com/dbt-labs/dbt-core/issues/1945#issuecomment-576714925
        # for an explanation.
        now = datetime.utcnow().isoformat()
        inputs = self.columns + [
            relation.render(),
            str(self.unique),
            str(self.type),
            str(self.transaction_per_chunk),
            now,
        ]
        string = "_".join(inputs)
        return md5(string)
