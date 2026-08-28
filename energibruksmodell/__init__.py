from ebm.__version__ import version

__all__ = [
    'calculate_area_forecast',
    'calculate_energy_need',
    'calculate_energy_use',
    'calculate_heating_systems',
    'calculate_holiday_homes',
    'calculate_s_curves',
    'calculate_s_curves_by_condition',
    'run_model',
]


def __getattr__(name: str):
    if name in __all__:
        from . import controllers  # noqa: PLC0415 (lazy import to break circular dependency)
        return getattr(controllers, name)
    raise AttributeError(f"module 'energibruksmodell' has no attribute {name!r}")
