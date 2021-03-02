##############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
##############################################################################

import numpy as np
from numba import njit, float64, int64
from ..utils.Math import cholesky

###############################################################################

@njit(float64[:, :](int64, int64, float64, float64, float64, float64, int64),
      cache=True, fastmath=True)
def getPaths(num_paths,
             numTimeSteps,
             t,
             mu,
             stock_price,
             volatility,
             seed):
    """ Get the simulated GBM process for a single asset with many paths and
    time steps. Inputs include the number of time steps, paths, the drift mu,
    stock price, volatility and a seed. """

    np.random.seed(seed)
    dt = t / numTimeSteps
    vsqrt_dt = volatility * np.sqrt(dt)
    m = np.exp((mu - volatility * volatility / 2.0) * dt)
    Sall = np.empty((2 * num_paths, numTimeSteps + 1))

    # This should be less memory intensive as we only generate randoms per step
    Sall[:, 0] = stock_price
    for it in range(1, numTimeSteps + 1):
        g1D = np.random.standard_normal((num_paths))
        for ip in range(0, num_paths):
            w = np.exp(g1D[ip] * vsqrt_dt)
            Sall[ip, it] = Sall[ip, it - 1] * m * w
            Sall[ip + num_paths, it] = Sall[ip + num_paths, it - 1] * m / w

    return Sall

###############################################################################


@njit(float64[:, :, :](int64, int64, int64, float64, float64[:], float64[:],
                       float64[:], float64[:, :], int64),
      cache=True, fastmath=True)
def getPathsAssets(numAssets,
                   num_paths,
                   numTimeSteps,
                   t,
                   mus,
                   stock_prices,
                   volatilities,
                   corrMatrix,
                   seed):
    """ Get the simulated GBM process for a number of assets and paths and num
    time steps. Inputs include the number of assets, paths, the vector of mus,
    stock prices, volatilities, a correlation matrix and a seed. """

    np.random.seed(seed)
    dt = t / numTimeSteps
    vsqrt_dts = volatilities * np.sqrt(dt)
    m = np.exp((mus - volatilities * volatilities / 2.0) * dt)

    Sall = np.empty((2 * num_paths, numTimeSteps + 1, numAssets))

    g = np.random.standard_normal((num_paths, numTimeSteps + 1, numAssets))
    c = cholesky(corrMatrix)
    gCorr = np.empty((num_paths, numTimeSteps + 1, numAssets))

    # Calculate the dot product
    for ip in range(0, num_paths):
        for it in range(0, numTimeSteps+1):
            for ia in range(0, numAssets):
                gCorr[ip][it][ia] = 0.0
                for ib in range(0, numAssets):
                    gCorr[ip][it][ia] += g[ip][it][ib] * c[ia][ib]

    for ip in range(0, num_paths):
        for ia in range(0, numAssets):
            Sall[ip, 0, ia] = stock_prices[ia]
            Sall[ip + num_paths, 0, ia] = stock_prices[ia]

    for ip in range(0, num_paths):
        for it in range(1, numTimeSteps + 1):
            for ia in range(0, numAssets):
                z = gCorr[ip, it, ia]
                w = np.exp(z * vsqrt_dts[ia])
                v = m[ia]
                Sall[ip, it, ia] = Sall[ip, it - 1, ia] * v*w
                Sall[ip + num_paths, it, ia] = Sall[ip + num_paths,
                                                   it - 1, ia] * v/w

    return Sall

###############################################################################


#@njit(float64[:, :](int64, int64, float64, float64[:], float64[:], float64[:],
#                   float64[:, :], int64),
#                   cache=True, fastmath=True)
@njit
def getAssets(numAssets,
              num_paths,
              t,
              mus,
              stock_prices,
              volatilities,
              corrMatrix,
              seed):
    
    """ Get the simulated GBM process for a number of assets and paths for one
    time step. Inputs include the number of assets, paths, the vector of mus,
    stock prices, volatilities, a correlation matrix and a seed. """

    np.random.seed(seed)
    vsqrt_dts = volatilities * np.sqrt(t)
    m = np.exp((mus - volatilities * volatilities / 2.0) * t)
    Sall = np.empty((2 * num_paths, numAssets))
    g = np.random.standard_normal((num_paths, numAssets))
    c = cholesky(corrMatrix)
    gCorr = np.empty((num_paths, numAssets))

    # Calculate the dot product
    for ip in range(0, num_paths):
        for ia in range(0, numAssets):
            gCorr[ip][ia] = 0.0
            for ib in range(0, numAssets):
                gCorr[ip][ia] += g[ip][ib] * c[ia][ib]

    for ip in range(0, num_paths):
        for ia in range(0, numAssets):
            z = gCorr[ip, ia]
            w = np.exp(z * vsqrt_dts[ia])
            Sall[ip, ia] = stock_prices[ia] * m[ia] * w
            Sall[ip + num_paths, ia] = stock_prices[ia] * m[ia] / w

    return Sall

###############################################################################


class FinGBMProcess():

    def getPaths(self,
                 num_paths: int,
                 numTimeSteps: int,
                 t: float,
                 mu: float,
                 stock_price: float,
                 volatility: float,
                 seed: int):
        """ Get a matrix of simulated GBM asset values by path and time step.
        Inputs are the number of paths and time steps, the time horizon and
        the initial asset value, volatility and random number seed. """

        paths = getPaths(num_paths, numTimeSteps,
                         t, mu, stock_price, volatility, seed)

        return paths

###############################################################################

    def getPathsAssets(self,
                       numAssets,
                       num_paths,
                       numTimeSteps,
                       t,
                       mus,
                       stock_prices,
                       volatilities,
                       corrMatrix,
                       seed):
        """ Get a matrix of simulated GBM asset values by asset, path and time
        step. Inputs are the number of assets, paths and time steps, the time-
        horizon and the initial asset values, volatilities and betas. """

        if numTimeSteps == 2:
            paths = getAssets(numAssets, num_paths,
                              t, mus, stock_prices,
                              volatilities, corrMatrix, seed)
        else:
            paths = getPathsAssets(numAssets, num_paths, numTimeSteps,
                                   t, mus, stock_prices,
                                   volatilities, corrMatrix, seed)
        return paths

###############################################################################