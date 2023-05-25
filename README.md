# Time Series Forecasting in Calendar Spread Strategies: An Application in the Argentine Corn Market

By Facundo Joel Allia Fernandez

To navigate the complexities of calendar spread trading and identify profitable opportunities, traders have turned to the power of time series forecasting. By analyzing historical market data and applying advanced forecasting techniques, traders can gain valuable insights into future price movements and make more informed trading decisions. 

In this repository we analyze possible calendar spread strategies in the Argentine derivatives market (MatbaRofex). The purpose of the developed code is to serve to analyze different strategies that combine futures of agricultural products, specifically soybeans, wheat and corn.

## An Application in the Argentine Corn Market

In the file "An Application in the Argentine Corn Market.ipynb" an analysis is proposed of a strategy that combines the purchase of a corn futures contract for April 2024 and the simultaneous sale of a corn contract for December 2023 seeking to obtain a gain in the face of a possible increase in the differential between the value of both.

Historical price data is processed, the strategy is formulated and possible future values are predicted using a time series forecasting model from the Prophet library.

![plot_corn_apr_vs_dec](https://github.com/facundoallia/calendar-spread-time-series-forecasting/raw/main/Assets/plot_corn_apr_vs_dec.png)

![plot_corn_apr_vs_dec_forecast_smoothed](https://github.com/facundoallia/calendar-spread-time-series-forecasting/raw/main/Assets/plot_corn_apr_vs_dec_forecast_smoothed.png)


The code can be modified in order to analyze other products, months, or years. In the folder 'Data' you can find the historical prices for corn, soy, and wheat from 2010 to the date (21–5–2023). Feel free to replace the parameters to analyze calendar spreads with different combinations of products and months. Remember to refresh the latest contracts.

## Analyzer

In the "analyzer.py" file there are functions that can be used to access the code easily:

process_product_data(): receives product, contract month, start year and end year as parameters and returns a dataframe with the processed closing prices.

plot_future(): receives product, contract month, start year and end year as parameters and returns a matplotlib plot of the analyzed future.

make_forecasts(): receives as parameters the products to analyze from a possible pairs strategy (like a calendar spread but also accepts combinations of products), months of the contracts, start and end years and period to forecast. Returns a dataframe with the forecasts made by Prophet based on the historical prices of the selected products of the analyzed period.

plot_forecast_data(): receives as parameters the products to be analyzed from a possible pair strategy (like a calendar spread but also accepts combinations of products), months of the contracts, start and end years and period to forecast. Returns a graph of the forecasts.
