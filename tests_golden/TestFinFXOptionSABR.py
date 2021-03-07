###############################################################################
# Copyright (C) 2018, 2019, 2020 Dominic O'Kane
###############################################################################

import numpy as np

import sys
sys.path.append("..")

from financepy.utils.date import Date
from financepy.utils.global_types import FinOptionTypes
from financepy.products.fx.fx_vanilla_option import FXVanillaOption
from financepy.models.black_scholes import BlackScholes
from financepy.market.discount.curve_flat import DiscountCurveFlat

from FinTestCases import FinTestCases, globalTestCaseMode
testCases = FinTestCases(__file__, globalTestCaseMode)

##########################################################################


def test_FinFXOptionSABR():

    # UNFINISHED
    # There is no FXAmericanOption class. It is embedded in the FXVanillaOption
    # class. This test just compares it to the European

    valuation_date = Date(13, 2, 2018)
    expiry_date = Date(13, 2, 2019)

    # In BS the FX rate is the price in domestic of one unit of foreign
    # In case of EURUSD = 1.3 the domestic currency is USD and foreign is EUR
    # DOM = USD , FOR = EUR
    ccy1CCRate = 0.030  # EUR
    ccy2CCRate = 0.025  # USD

    spot_fx_rate = 1.20
    strike_fx_rate = 1.250
    volatility = 0.10

    notional = 1000000.0

    dom_discount_curve = DiscountCurveFlat(valuation_date, ccy2CCRate)
    for_discount_curve = DiscountCurveFlat(valuation_date, ccy1CCRate)

    model = BlackScholes(volatility)

    # Two examples to show that changing the notional currency and notional
    # keeps the value unchanged
    notional = 1000000.0

    spot_fx_rates = np.arange(50, 200, 10)/100.0

    testCases.header("OPTION", "FX_RATE", "VALUE_BS", "VOL_IN", "DIFF")

    for spot_fx_rate in spot_fx_rates:

        callOption = FXVanillaOption(expiry_date,
                                     strike_fx_rate,
                                        "EURUSD",
                                     FinOptionTypes.EUROPEAN_CALL,
                                     notional,
                                        "USD")

        valueEuropean = callOption.value(valuation_date,
                                         spot_fx_rate,
                                         dom_discount_curve,
                                         for_discount_curve,
                                         model)['v']

        callOption = FXVanillaOption(expiry_date,
                                     strike_fx_rate,
                                        "EURUSD",
                                     FinOptionTypes.AMERICAN_CALL,
                                     1000000,
                                        "USD")

        valueAmerican = callOption.value(valuation_date,
                                         spot_fx_rate,
                                         dom_discount_curve,
                                         for_discount_curve,
                                         model)['v']

        diff = (valueAmerican - valueEuropean)

        testCases.print("CALL:",
                        "%9.6f" % spot_fx_rate,
                        "%9.7f" % valueEuropean,
                        "%9.7f" % valueAmerican,
                        "%9.7f" % diff)

    testCases.header("OPTION", "FX_RATE", "VALUE_BS", "VOL_IN", "DIFF")

    for spot_fx_rate in spot_fx_rates:

        callOption = FXVanillaOption(expiry_date,
                                     strike_fx_rate,
                                        "EURUSD",
                                     FinOptionTypes.EUROPEAN_PUT,
                                     1000000,
                                        "USD")

        valueEuropean = callOption.value(valuation_date,
                                         spot_fx_rate,
                                         dom_discount_curve,
                                         for_discount_curve,
                                         model)['v']

        callOption = FXVanillaOption(expiry_date,
                                     strike_fx_rate,
                                        "EURUSD",
                                     FinOptionTypes.AMERICAN_PUT,
                                     1000000,
                                        "USD")

        valueAmerican = callOption.value(valuation_date,
                                         spot_fx_rate,
                                         dom_discount_curve,
                                         for_discount_curve,
                                         model)['v']

        diff = (valueAmerican - valueEuropean)
        testCases.print("PUT:",
                        "%9.6f" % spot_fx_rate,
                        "%9.7f" % valueEuropean,
                        "%9.7f" % valueAmerican,
                        "%9.7f" % diff)

###############################################################################


test_FinFXOptionSABR()
testCases.compareTestCases()
