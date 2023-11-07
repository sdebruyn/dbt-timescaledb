from dbt.tests.adapter.basic.test_adapter_methods import BaseAdapterMethod
from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_empty import BaseEmpty
from dbt.tests.adapter.basic.test_ephemeral import BaseEphemeral
from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.test_incremental import BaseIncremental
from dbt.tests.adapter.basic.test_singular_tests import BaseSingularTests
from dbt.tests.adapter.basic.test_singular_tests_ephemeral import BaseSingularTestsEphemeral
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp


class TestSimpleMaterializationsTimescaleDB(BaseSimpleMaterializations):
    pass


class TestSingularTestsTimescaleDB(BaseSingularTests):
    pass


class TestSingularTestsEphemeralTimescaleDB(BaseSingularTestsEphemeral):
    pass


class TestEmptyTimescaleDB(BaseEmpty):
    pass


class TestEphemeralTimescaleDB(BaseEphemeral):
    pass


class TestIncrementalTimescaleDB(BaseIncremental):
    pass


class TestGenericTestsTimescaleDB(BaseGenericTests):
    pass


class TestSnapshotCheckColsTimescaleDB(BaseSnapshotCheckCols):
    pass


class TestSnapshotTimestampTimescaleDB(BaseSnapshotTimestamp):
    pass


class TestBaseAdapterMethodTimescaleDB(BaseAdapterMethod):
    pass
