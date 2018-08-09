# coding: utf-8

""" Test cases for GroupBy.plot """


from pandas import Series, DataFrame
import pandas.util.testing as tm
import pandas.util._test_decorators as td

import numpy as np

from pandas.tests.plotting.common import TestPlotBase
import pytest


@td.skip_if_no_mpl
@pytest.mark.parametrize('bins', [5, None, np.linspace(-3, 3, 10)])
def test_hist_bins_match(bins):
    # GH-22222
    N = 100
    np.random.seed(0)
    df = DataFrame(np.append(np.random.randn(N), np.random.randn(N) / 10),
                   columns=['rand'])
    df['group'] = [0] * N + [1] * N
    g = df.groupby('group')['rand']
    ax = g.hist(bins=bins, alpha=0.7, equal_bins=True)[0]

    if bins is None:
        num_bins = 10  # default value used in `hist_series`
    elif type(bins) == np.ndarray:
        num_bins = len(bins) - 1
    else:
        num_bins = bins

    bin_width_group0 = ax.patches[0].get_width()
    bin_width_group1 = ax.patches[num_bins].get_width()
    assert np.isclose(bin_width_group0, bin_width_group1)

    bars_x_pos_group0 = [patch.get_bbox().get_points()[0, 0]
                         for patch in ax.patches[:num_bins]]
    bars_x_pos_group1 = [patch.get_bbox().get_points()[0, 0]
                         for patch in ax.patches[num_bins:]]
    assert np.isclose(bars_x_pos_group0, bars_x_pos_group1).all()
    tm.close()


@td.skip_if_no_mpl
class TestDataFrameGroupByPlots(TestPlotBase):

    def test_series_groupby_plotting_nominally_works(self):
        n = 10
        weight = Series(np.random.normal(166, 20, size=n))
        height = Series(np.random.normal(60, 10, size=n))
        with tm.RNGContext(42):
            gender = np.random.choice(['male', 'female'], size=n)

        weight.groupby(gender).plot()
        tm.close()
        height.groupby(gender).hist()
        tm.close()
        # Regression test for GH8733
        height.groupby(gender).plot(alpha=0.5)
        tm.close()

    def test_plotting_with_float_index_works(self):
        # GH 7025
        df = DataFrame({'def': [1, 1, 1, 2, 2, 2, 3, 3, 3],
                        'val': np.random.randn(9)},
                       index=[1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 1.0, 2.0, 3.0])

        df.groupby('def')['val'].plot()
        tm.close()
        df.groupby('def')['val'].apply(lambda x: x.plot())
        tm.close()

    def test_hist_single_row(self):
        # GH10214
        bins = np.arange(80, 100 + 2, 1)
        df = DataFrame({"Name": ["AAA", "BBB"],
                        "ByCol": [1, 2],
                        "Mark": [85, 89]})
        df["Mark"].hist(by=df["ByCol"], bins=bins)
        df = DataFrame({"Name": ["AAA"], "ByCol": [1], "Mark": [85]})
        df["Mark"].hist(by=df["ByCol"], bins=bins)

    def test_plot_submethod_works(self):
        df = DataFrame({'x': [1, 2, 3, 4, 5],
                        'y': [1, 2, 3, 2, 1],
                        'z': list('ababa')})
        df.groupby('z').plot.scatter('x', 'y')
        tm.close()
        df.groupby('z')['x'].plot.line()
        tm.close()

    def test_plot_kwargs(self):

        df = DataFrame({'x': [1, 2, 3, 4, 5],
                        'y': [1, 2, 3, 2, 1],
                        'z': list('ababa')})

        res = df.groupby('z').plot(kind='scatter', x='x', y='y')
        # check that a scatter plot is effectively plotted: the axes should
        # contain a PathCollection from the scatter plot (GH11805)
        assert len(res['a'].collections) == 1

        res = df.groupby('z').plot.scatter(x='x', y='y')
        assert len(res['a'].collections) == 1
