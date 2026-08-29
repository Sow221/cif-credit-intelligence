"""Feature engineering: construction des 25 features officielles."""

from cifci.features.build import (
    aggregate_loans,
    build_features,
    prepare_feature_matrix,
)
from cifci.features.validate import (
    LeakageError,
    assert_no_leakage,
    forbidden_features,
    load_and_validate,
)

__all__ = [
    "LeakageError",
    "aggregate_loans",
    "assert_no_leakage",
    "build_features",
    "forbidden_features",
    "load_and_validate",
    "prepare_feature_matrix",
]
