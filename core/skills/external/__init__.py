"""External-system skills — read-only lookups against Graylog, ParkIS,
SKIDATA, Bmove backend, Datatrans.

Importing this package side-effects: each skill module registers itself
into ``core.skills.REGISTRY`` at import time via the ``@register``
decorator. The mock data lives in ``mock_data.py``; when Ivan wires real
API credentials, each skill's ``execute`` method swaps the mock helper
call for an HTTP client call. The shape of ``SkillResult.data`` stays
the same so the planner / Claude prompt doesn't change.
"""
from core.skills.external import (  # noqa: F401  — side-effect: register skills
    bmove_user_lookup,
    datatrans_lookup,
    graylog_search,
    parkis_lookup,
    search_playbooks,
    skidata_lookup,
)

__all__ = [
    "bmove_user_lookup",
    "datatrans_lookup",
    "graylog_search",
    "parkis_lookup",
    "search_playbooks",
    "skidata_lookup",
]
