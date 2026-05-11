import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_array_equal

from ebm import saving


def _make_energy_need_dataframe(kwh_m2, m2, reduction_condition, reduction_policy, reduction_yearly, behaviour_factor=1.0) -> pd.DataFrame:
    df = pd.DataFrame(
        data=[
            [1.0, 1.0, 1.0, 1.0, 10, 100],
            [reduction_condition, reduction_policy, reduction_yearly, behaviour_factor, 42.42, kwh_m2,m2],
        ],
        columns=['reduction_condition', 'reduction_policy', 'reduction_yearly', 'behaviour_factor', 'original_kwh_m2', 'calibrated_kwh_m2', 'm2'])
    return df


@pytest.mark.parametrize(('reduction_policy', 'reduction_condition','reduction_yearly', 'reduction_policy_kwh_m2', 'm2', 'original_condition_kwh_m2'),
                         [pytest.param(0.8, 0.8, 1.0, 1.6, 100, 10, id='policy+condition-reduction'),
                          pytest.param(0.5, 1.0, 1.0, 5.0, 100, 10, id='policy-reduction'),
                          pytest.param(1.0, 0.5, 1.0, 0.0, 100, 10, id='condition-reduction'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 100, 10, id='no-reduction'),
                          pytest.param(0.8, 1.0, 0.8, 1.6, 100, 10, id='policy+yearly-reduction'),
                          pytest.param(0.9, 0.9, 0.9, 1.62, 100, 20, id='reduce-all'),
                          pytest.param(0.5, 0.5, 0.5, 1.25, 100, 10, id='apartment_heating_rv'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 1_300_935.4375, 154.531037, id='reduce-all-50'),
                          pytest.param(0.75, 1.0, 1.0,  38.5, 1_300_935, 154, id='culture-pt49-r_a_s-2020-hrv'),
                          ])
def test_reduction_policy_kwh(
        reduction_policy: float,
        reduction_condition: float,
        reduction_yearly: float,
        reduction_policy_kwh_m2: float,
        m2: float,
        original_condition_kwh_m2: float):
    df: pd.DataFrame = _make_energy_need_dataframe(kwh_m2=original_condition_kwh_m2,
                                     m2=m2,
                                     reduction_policy=reduction_policy,
                                     reduction_yearly=reduction_yearly,
                                     reduction_condition=reduction_condition)

    res = saving.reduction_policy_kwh(df)

    expected_reduction_policy_kwh_m2 = np.array([0.0, reduction_policy_kwh_m2])
    assert res['reduction_policy_kwh_m2'].tolist() == pytest.approx(expected_reduction_policy_kwh_m2.tolist(), rel=1e-4)

    expected_reduction_condition_kwh = np.array(expected_reduction_policy_kwh_m2)*m2
    assert res['reduction_policy_kwh'].tolist() == pytest.approx(expected_reduction_condition_kwh.tolist(), rel=1e-4)


@pytest.mark.parametrize(('reduction_yearly', 'reduction_condition','reduction_policy', 'reduction_yearly_kwh_m2', 'm2', 'original_condition_kwh_m2'),
                         [pytest.param(0.8, 0.8, 1.0, 1.6, 100, 10, id='policy+condition-reduction'),
                          pytest.param(0.5, 1.0, 1.0, 5.0, 100, 10, id='policy-reduction'),
                          pytest.param(1.0, 0.5, 1.0, 0.0, 100, 10, id='condition-reduction'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 100, 10, id='no-reduction'),
                          pytest.param(0.8, 1.0, 0.8, 1.6, 100, 10, id='policy+yearly-reduction'),
                          pytest.param(0.9, 0.9, 0.9, 1.62, 100, 20, id='reduce-all'),
                          pytest.param(0.5, 0.5, 0.5, 1.25, 100, 10, id='apartment_heating_rv'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 1_300_935.4375, 154.531037, id='reduce-all-50'),
                          pytest.param(0.75, 1.0, 1.0,  38.5, 1_300_935, 154, id='culture-pt49-r_a_s-2020-hrv'),
                          ])
def test_reduction_yearly_kwh(
        reduction_yearly: float,
        reduction_condition: float,
        reduction_policy: float,
        reduction_yearly_kwh_m2: float,
        m2: float,
        original_condition_kwh_m2: float):
    df: pd.DataFrame = _make_energy_need_dataframe(kwh_m2=original_condition_kwh_m2,
                                     m2=m2,
                                     reduction_yearly=reduction_yearly,
                                     reduction_policy=reduction_policy,
                                     reduction_condition=reduction_condition)

    res = saving.reduction_yearly_kwh(df)

    expected_reduction_yearly_kwh_m2 = np.array([0.0, reduction_yearly_kwh_m2])
    assert res['reduction_yearly_kwh_m2'].tolist() == pytest.approx(expected_reduction_yearly_kwh_m2.tolist(), rel=1e-4)

    expected_reduction_yearly_kwh = np.array(expected_reduction_yearly_kwh_m2)*m2
    assert res['reduction_yearly_kwh'].tolist() == pytest.approx(expected_reduction_yearly_kwh.tolist(), rel=1e-4)


@pytest.mark.parametrize(('reduction_condition','reduction_policy','reduction_yearly', 'reduction_condition_kwh_m2', 'm2', 'original_condition_kwh_m2'),
                         [pytest.param(0.8, 0.8, 1.0, 1.6, 100, 10, id='condition+policy-reduction'),
                          pytest.param(0.9, 1.0, 1.0, 5.0, 100, 50, id='condition-reduction'),
                          pytest.param(1.0, 0.5, 1.0, 0.0, 100, 10, id='policy-reduction'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 100, 10, id='no-reduction'),
                          pytest.param(0.8, 1.0, 0.8, 1.6, 100, 10, id='condition+yearly-reduction'),
                          pytest.param(0.9, 0.9, 0.9, 1.62, 100, 20, id='reduce-all'),
                          pytest.param(0.5, 0.5, 0.5, 1.25, 100, 10, id='apartment_heating_rv'),
                          pytest.param(1.0, 1.0, 1.0, 0.0, 1_300_935.4375, 154.531037, id='reduce-all-50'),
                          pytest.param(0.75, 1.0, 1.0,  38.5, 1_300_935, 154, id='culture-pt49-r_a_s-2020-hrv'),
                          ])
def test_reduction_condition_kwh(reduction_condition: float,
                               reduction_policy: float,
                               reduction_yearly: float,
                               reduction_condition_kwh_m2: float,
                               m2: float,
                               original_condition_kwh_m2: float):

    df: pd.DataFrame = _make_energy_need_dataframe(kwh_m2=original_condition_kwh_m2,
                                     m2=m2,
                                     reduction_condition=reduction_condition,
                                     reduction_policy=reduction_policy,
                                     reduction_yearly=reduction_yearly)

    res = saving.reduction_condition_kwh(df)

    expected_reduction_condition_kwh_m2 = np.array([0.0, reduction_condition_kwh_m2])
    assert res['reduction_condition_kwh_m2'].tolist() == pytest.approx(expected_reduction_condition_kwh_m2.tolist(), rel=1e-4)

    expected_reduction_condition_kwh = np.array(expected_reduction_condition_kwh_m2)*m2
    assert res['reduction_condition_kwh'].tolist() == pytest.approx(expected_reduction_condition_kwh.tolist(), rel=1e-4)


def missing_column_parameters():
    return [
        (['calibrated_kwh_m2'], 'Required column calibrated_kwh_m2 missing from energy need dataframe'),
        (['reduction_condition'], 'Required column reduction_condition missing from energy need dataframe'),
        (['reduction_policy',
          'reduction_yearly',
          'm2'], 'Required columns m2, reduction_policy, reduction_yearly missing from energy need dataframe'),
    ]


@pytest.mark.parametrize(('missing', 'msg'), missing_column_parameters())
def test_reduction_condition_kwh_raise_value_error_on_missing_columns(missing, msg):
    df = _make_energy_need_dataframe(kwh_m2=10, m2=100, reduction_condition=1.0, reduction_policy=1.0, reduction_yearly=1.0)
    with pytest.raises(ValueError, match=msg):
        saving.reduction_condition_kwh(df.drop(columns=missing))

@pytest.mark.parametrize(('missing', 'msg'), missing_column_parameters())
def test_reduction_policy_kwh_raise_value_error_on_missing_columns(missing, msg):
    df = _make_energy_need_dataframe(kwh_m2=10, m2=100, reduction_condition=1.0, reduction_policy=1.0, reduction_yearly=1.0)
    with pytest.raises(ValueError, match=msg):
        saving.reduction_policy_kwh(df.drop(columns=missing))


@pytest.mark.parametrize(('missing', 'msg'), missing_column_parameters())
def test_reduction_yearly_kwh_raise_value_error_on_missing_columns(missing, msg):
    df = _make_energy_need_dataframe(kwh_m2=10, m2=100, reduction_condition=1.0, reduction_policy=1.0, reduction_yearly=1.0)
    with pytest.raises(ValueError, match=msg):
        saving.reduction_yearly_kwh(df.drop(columns=missing))


def test_reduction_condition_handle_zero_division():
    df = pd.DataFrame(
        data=[
            [1.0, 1.0, 1.0, 1.0, 10, 100, 1000],
            [0.0, 1.0, 1.0, 1.0, 42, 100, 4200],
            [1.0, 0.0, 1.0, 1.0, 10, 100, 1000],
            [1.0, 1.0, 1.0, 1.0, 10, 100, 1000],
        ],
        columns=['reduction_condition', 'reduction_policy', 'reduction_yearly', 'behaviour_factor', 'calibrated_kwh_m2', 'm2', 'kwh'])

    res = saving.reduction_condition_kwh(df)

    expected_reduction_condition_kwh_m2 = np.round(np.array([0.0, 42.0, 0.0, 0.0]), 4)
    assert_array_equal(res['reduction_condition_kwh_m2'], expected_reduction_condition_kwh_m2)


def test_reduction_condition_handle_zero_division_like_cases():
    """
    The function does not divide, but this test mirrors original intent:
    when reduction factors are 0 or 1, results should remain finite and correct.
    """
    df = pd.DataFrame(
        data=[
            # (rc, rp, ry, bf, kwh/m2, m2, kwh)
            [1.0, 1.0, 1.0, 1.0, 10.0, 100.0, 1000.0],  # baseline: no difference expected
            [0.0, 1.0, 1.0, 1.0, 42.0, 100.0, 4200.0],  # condition = 0 -> full diff = kwh/m2 * rp * ry
            [1.0, 0.0, 1.0, 1.0, 10.0, 100.0, 1000.0],  # policy = 0 -> diff = 0
            [1.0, 1.0, 1.0, 1.0, 10.0, 100.0, 1000.0],  # all ones -> diff = 0
        ],
        columns=[
            "reduction_condition",
            "reduction_policy",
            "reduction_yearly",
            "behaviour_factor",
            "calibrated_kwh_m2",
            "m2",
            "kwh",
        ],
    )

    res = saving.reduction_condition_kwh(df)

    expected = np.array([0.0, 42.0, 0.0, 0.0])
    # Use approx for clarity instead of pre-rounding
    assert res["reduction_condition_kwh_m2"].tolist() == pytest.approx(expected.tolist(), abs=1e-4)


def test_reduction_condition_handles_nan_as_one():
    """
    If any of the multiplicative factors are NaN, the implementation fills NaN with no reduction (1.0)
    for the per-m² difference. Validate that behavior explicitly.
    """
    df = pd.DataFrame(
        data=[
            [np.nan, 1.0, 1.0, 1.0, 20.0, 100.0],  # NaN in condition -> treated as 0 by .fillna(0) on diff
            [0.5, np.nan, 1.0, 1.0, 20.0, 100.0],  # NaN in policy
            [0.9, 1.0, np.nan, 1.0, 2.0, 100.0],  # NaN in yearly
        ],
        columns=[
            "reduction_condition",
            "reduction_policy",
            "reduction_yearly",
            "behaviour_factor",
            "calibrated_kwh_m2",
            "m2",
        ],
    )

    res = saving.reduction_condition_kwh(df)

    expected = pd.Series([0.0, 10.0, 0.2], name="reduction_condition_kwh_m2", dtype=float)

    pd.testing.assert_series_equal(
        res['reduction_condition_kwh_m2'],
        expected,
        check_names=True,
        check_dtype=False,  # dtype float OK; pandas may upcast
        atol=1e-12,
    )


def test_reduced_column_kwh_raise_value_error_on_duplicate_columns():
    with pytest.raises(ValueError, match='Operational column condition also present in other columns'):
        saving._reduced_column_kwh(df=_make_energy_need_dataframe(1,2,1.0, 1.0, 1.0),
                                   operational_column='condition',
                                   other_columns={'reduction_condition', 'reduction_yearly', 'reduction_policy'})


def test_reduced_construction_kwh():
    df = pd.DataFrame({
        'kwh_m2': [120.0, 42, 95.5, 50.0],
        'm2': [1000.0, 42, 2500.0, 100.0],
        'net_construction_m2': [200.0, 0.0, -100.0, 150.0],  # 2nd row adds area; 3rd row over-reduces area
    })
    result = saving.reduced_construction_kwh(df)

    # Row 0 (expected scenario)
    assert result.loc[0, 'original_construction_kwh'] == pytest.approx(120000.0)
    assert result.loc[0, 'reduced_construction_kwh'] == pytest.approx(96000.0)
    assert result.loc[0, 'net_construction_kwh'] == pytest.approx(24000.0)

    # Row 1 (zero scenario)
    assert result.loc[1, 'original_construction_kwh'] == 1764.0
    assert result.loc[1, 'reduced_construction_kwh'] == 1764.0
    assert result.loc[1, 'net_construction_kwh'] == 0.0

    # Row 1 (area increases): net_construction_m2 = -100 (Change to validation or raise error)
    assert result.loc[2, 'original_construction_kwh'] == pytest.approx(238750.0)
    assert result.loc[2, 'reduced_construction_kwh'] == pytest.approx(248300.0)
    assert result.loc[2, 'net_construction_kwh'] == pytest.approx(-9550.0)

    # Row 2 (over-reduction; no clamping in function): (Change to validation or raise error)
    assert result.loc[3, 'original_construction_kwh'] == pytest.approx(5000.0)
    assert result.loc[3, 'reduced_construction_kwh'] == pytest.approx(-2500.0)
    assert result.loc[3, 'net_construction_kwh'] == pytest.approx(7500.0)


def test_reduced_construction_kwh_return_a_copy():
    df = pd.DataFrame({
        'kwh_m2': [120.0, 42, 95.5, 50.0],
        'm2': [1000.0, 42, 2500.0, 100.0],
        'net_construction_m2': [200.0, 0.0, -100.0, 150.0],  # 2nd row adds area; 3rd row over-reduces area
    })
    df_copy = saving.reduced_construction_kwh(df)
    df_copy.loc[:] = -1

    assert df.loc[0, 'kwh_m2'] == pytest.approx(120.0)
    assert df.loc[1, 'm2'] == pytest.approx(42.0)
    assert df.loc[1, 'net_construction_m2'] == pytest.approx(0.0)


def test_reduced_construction_kwh_return_expected_columns():
    df = pd.DataFrame({
        'kwh_m2': [120.0, 42, 95.5, 50.0],
        'm2': [1000.0, 42, 2500.0, 100.0],
        'net_construction_m2': [200.0, 0.0, -100.0, 150.0],  # 2nd row adds area; 3rd row over-reduces area
    })
    result = saving.reduced_construction_kwh(df)

    for col in ['original_construction_kwh', 'reduced_construction_kwh', 'net_construction_kwh']:
        assert col in result.columns, f'Missing expected column: {col}'
