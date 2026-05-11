import numpy as np
import pandas as pd
from scipy.special import expit, logit

from ebm.model.scurve import SCurve


def logistic(x, L=1.0, x_0=0, k=1.0):
    #print(x)
    return L / (1.0 + np.exp(-k * (np.longdouble(x) - x_0), dtype=np.longdouble))

def make_sigmoid(sc: SCurve, precision=6.0):
    curve_length = sc._last_age - sc._earliest_age
    curve_center = sc._average_age - sc._earliest_age
    curve_max = 1.0 - (sc._never_share/100)
    rate =  (precision*2) / (curve_length-1)
    x=pd.Series(np.longdouble(np.arange(-precision, precision + rate, rate)))

    x_0_relative = curve_center / curve_length
    x_0_relative =  (precision * 2 * (curve_center / curve_length)) - precision
    y = logistic(x=x, L=curve_max, x_0=x_0_relative, k=1)

    return y


def make_alt_sigmoid(sc: SCurve, precision=6.0):
    curve_length = sc._last_age - sc._earliest_age
    curve_center = sc._average_age - sc._earliest_age
    curve_max = 1.0 - (sc._never_share / 100)
    rate = (precision * 2) / (curve_length - 1)
    x = pd.Series(np.longdouble(np.arange(-precision, precision + rate, rate)))

    M = curve_max  # max value
    k = 1.0  # steepness
    x0 = 0 # (precision * 2 * (curve_center / curve_length)) - precision  # midpoint
    #x = np.linspace(-6, 6, 200)

    return M * expit(k * (x - x0))  # in (0, M)


def logistic_scaled(x, a, b, ya, yb, m=0.0, M=1.0):
    """
    Build a scaled logistic y(x) that satisfies y(a)=ya and y(b)=yb (with m<ya,yb<M).
    Returns y(x) and the underlying parameters (k, x0).
    """
    if not (m < ya < M and m < yb < M):
        raise ValueError("ya and yb must be strictly between m and M.")

    pa = (ya - m) / (M - m)
    pb = (yb - m) / (M - m)

    k  = (logit(pb) - logit(pa)) / (b - a)
    x0 = a - logit(pa) / k

    y = m + (M - m) * expit(k * (x - x0))
    return y, k, x0



def main():

    scurve = SCurve(earliest_age=50,
                    average_age=100,
                    rush_years=30,
                    rush_share=0.7,
                    last_age=130,
                    never_share=0.05,
                    building_lifetime=130)
    y = make_sigmoid(scurve)

    curve_array = scurve.calc_scurve().array
    dy = np.concatenate(([np.nan], np.diff(y)))

    exp = make_alt_sigmoid(scurve)
    dexp = np.concatenate(([np.nan], np.diff(exp)))

    x = np.linspace(0, 10.0, 80)

    sy, ky, sx0 = logistic_scaled(x, 0, 10, 0.0005251397050774195, 0.95, m=0.0, M=1.0)

    print('  i (age): yyyyyyyyyyyyyyyyyyyyy  diffyyyyyyyyyyyyyyyyy  scurveeeeeeeeeeeeeeee  expittttttttttttttttt diffexpppppppppppp')
    for i, (a, b, c, p, dx) in enumerate(zip(y, dy, curve_array[49:], exp, sy), start=0):
        print(f'{i:>3} ({i+50:>3}): {a:<22} {b:<22} {c:<22} {p:<22} {dx:<22}')

    print('y=>', max(y), min(y))
    print('dy=>', max(dy), min(dy))


if __name__ == '__main__':
    main()
