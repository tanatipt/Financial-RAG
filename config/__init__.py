from dynaconf import Dynaconf
settings = Dynaconf(
    environments = True,
    settings_files=["settings.yaml"]
)