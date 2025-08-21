from enum import Enum


class APIType(str, Enum):
    CONFIG = "config"
    CONNECTION = "connection"
    DAG = "dag"
    DAGRUN = "dagrun"
    DAGSTATS = "dagstats"
    DATASET = "dataset"
    EVENTLOG = "eventlog"
    IMPORTERROR = "importerror"
    MONITORING = "monitoring"
    PLUGIN = "plugin"
    POOL = "pool"
    PROVIDER = "provider"
    TASKINSTANCE = "taskinstance"
    VARIABLE = "variable"
    XCOM = "xcom"
