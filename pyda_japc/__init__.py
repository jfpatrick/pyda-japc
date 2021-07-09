"""
Documentation for the pyda_japc package

"""

__version__ = "0.0.1.dev0"


__cmmnbuild_deps__ = [
    {"product": "japc", "groupId": "cern.japc"},
    {"product": "japc-ext-cmwrda3", "groupId": "cern.japc"},  # (indirect use) For RDA communication
    {"product": "japc-ext-inca", "groupId": "cern.japc"},
    {"product": "japc-ext-mockito2", "groupId": "cern.japc"},
    {"product": "japc-ext-remote", "groupId": "cern.japc"},  # (indirect use)
    {"product": "japc-ext-tgm", "groupId": "cern.japc"},
    {"product": "japc-svc-ccs", "groupId": "cern.japc"},  # (indirect use) To fetch descriptors without INCA
    {"product": "japc-value", "groupId": "cern.japc"},
    # {"product": "log4j", "groupId": "log4j"},
    # {"product": "slf4j-api", "groupId": "org.slf4j"},
    # {"product": "slf4j-log4j12", "groupId": "org.slf4j"},
]
