import pandas as pd
import numpy as np 
import calendar
from prophet import Prophet
import matplotlib.pyplot as plt
import matplotlib.style as style

def process_product_data(product, month, beg_year, end_year, last_date=None):

    # Receives product, contract month, start year and end year as parameters, 
    # returns a dataframe with the processed closing prices.

    # Validate the data types of the parameters
    if not isinstance(product, str):
        raise TypeError("product must be string.")
    
    if not isinstance(month, (int, float)):
        raise TypeError("month must be numeric values.")
    
    if not isinstance(beg_year, (int, float)) or not isinstance(end_year, (int, float)):
        raise TypeError("beginning year and ending must be numeric values.")
    
    # Initialize an empty list to store dataframes
    dataframes = []

    # Create a list of years from beg_year to end_year
    years = list(range(beg_year, end_year + 1))

    # Loop through each year
    for year in years:
        # Generate file path based on product, month, and year
        file_path = f'Data/{product}/{month}/{year}.csv'
        
        # Read the CSV file and select the desired columns
        df = pd.read_csv(file_path, encoding='latin1', usecols=['Fecha', 'Cierre'])
        
        # Rename the columns for consistency
        df = df[['Fecha', 'Cierre']].rename(columns={'Fecha': 'date', 'Cierre': 'close'})
        
        # Add a column to store the expiration year
        df['expiration'] = year
        
        # Replace commas with periods in the 'close' column
        df['close'] = df['close'].str.replace(',', '.').astype(float)
        
        # Convert the 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')

        # Filter rows based on the last_date for subsequent years
        if last_date and year > years[0]:
            df = df[df['date'] > last_date]

        # Append the dataframe to the list
        dataframes.append(df)
    
        # Check if the DataFrame has at least one record
        if not df.empty:
            last_date = df['date'].iloc[-1]

    # Concatenate the dataframes in the list into a single dataframe
    return pd.concat(dataframes)


def plot_future(product, month, beg_year, end_year, last_date=None):

    # Receives product, contract month, start year and end year as parameters,
    # returns a matplotlib plot of the analyzed future.

    # Validate the data types of the parameters
    if not isinstance(product, str):
        raise TypeError("product must be string.")
    
    if not isinstance(month, (int, float)):
        raise TypeError("month must be numeric values.")
    
    if not isinstance(beg_year, (int, float)) or not isinstance(end_year, (int, float)):
        raise TypeError("beginning year and ending must be numeric values.")

    df = process_product_data(product, month, beg_year, end_year)

    # Set dark theme
    style.use('dark_background')

    # Create a list of unique expiration values
    expirations = df['expiration'].unique()

    # Create a figure with the desired size
    fig, ax = plt.subplots(figsize=(15, 5))

    # Set format
    ax.set_title('Evolution of historical prices: ' + calendar.month_name[month])
    ax.set_xlabel('Date')
    ax.set_ylabel('Close')

    # Define a color palette for the lines
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:cyan', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:brown']

    # Plot each expiration as a line with a different color
    for i, expiration in enumerate(expirations):
        df_plot = df[df['expiration'] == expiration]
        ax.plot(df_plot['date'], df_plot['close'], label=str(expiration), color=colors[i % len(colors)])

    # Adjust legend position
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.3), ncol=len(expirations))

    # Display the plot
    return plt.show()

def make_forecasts(prod_1,month_1,beg_1,end_1,prod_2,month_2,beg_2,end_2, periods,same_year=True):

    # Receives as parameters the products to analyze from a possible pairs strategy 
    # (like a calendar spread but also accepts combinations of products), months of the contracts, 
    # start and end years and period to forecast. Returns a dataframe with the forecasts 
    # made by Prophet based on the historical prices of the selected products of the analyzed period.

    # Validate the data types of the parameters
    if not isinstance(prod_1, str) or not isinstance(prod_2, str):
        raise TypeError("prod_1 and prod_2 must be strings.")
    
    if not isinstance(month_1, (int, float)) or not isinstance(month_2, (int, float)):
        raise TypeError("month_1 and month_2 must be numeric values.")
    
    if not isinstance(beg_1, (int, float)) or not isinstance(end_1, (int, float)):
        raise TypeError("beg_1 and end_1 must be numeric values.")
    
    if not isinstance(beg_2, (int, float)) or not isinstance(end_2, (int, float)):
        raise TypeError("beg_2 and end_2 must be numeric values.")
    
    if not isinstance(same_year, bool):
        raise TypeError("same_year must be True or False.")
    
    if not isinstance(periods, (int, float)):
        raise TypeError("periods must be a numeric value.")

    # Process data for prod_1
    df_1 = process_product_data(prod_1, month_1, beg_1, end_1)

    # Process data for prod_2
    df_2 = process_product_data(prod_2, month_2, beg_2, end_2)

    # Create column names based on product and month
    column_1 = f'_{prod_1}_{calendar.month_name[month_1][:3].lower()}'
    column_2 = f'_{prod_2}_{calendar.month_name[month_2][:3].lower()}'

    # Merge the two dataframes on 'date' column with appropriate suffixes
    df = pd.merge(df_1, df_2, on='date', suffixes=(column_1, column_2))

    # Calculate the spread by subtracting the 'close' values of column_2 from column_1
    df['spread'] = pd.to_numeric(df['close'+str(column_1)], errors='coerce') - pd.to_numeric(df['close'+str(column_2)], errors='coerce')

    # Create an empty list to store spread names
    spread_names = []

    # Iterate over each index in the dataframe
    for index in df.index:
        # Construct the spread name using various components
        spread_name = str(prod_1) + '_' + calendar.month_name[month_1].lower() + '_' + str(df.iloc[index,2]) + '_vs_' + str(prod_2) + '_' + calendar.month_name[month_2].lower() + '_' + str(df.iloc[index,4])
        # Append the spread name to the list
        spread_names.append(spread_name)

    # Assign the spread names to the 'spread_name' column in the dataframe
    df['spread_name'] = spread_names

    # Create a mask to compare the expiration values of column_1 and column_2
    if same_year == True:
        mask = df['expiration'+str(column_1)] != df['expiration'+str(column_2)]
    else:
        mask = df['expiration'+str(column_1)] == df['expiration'+str(column_2)]

    # Drop rows from the dataframe where the expiration values match
    df = df.drop(df[mask].index)

    # Create an empty DataFrame df_obs
    df_obs = pd.DataFrame()

    # Assign the 'date' column from df to 'ds' column in df_obs
    df_obs['ds'] = df['date']

    # Assign the 'spread' column from df to 'y' column in df_obs, converting it to float
    df_obs['y'] = df['spread'].astype(float)

    # Display the first few rows of df_obs
    df_obs.head()

    # Create a Prophet instance
    m = Prophet()

    # Fit the Prophet model to the observed data
    m.fit(df_obs)

    # Create a future dataframe with 200 additional periods
    future = m.make_future_dataframe(periods=periods)

    # Generate the forecast using the trained model
    forecast = m.predict(future)

    return forecast

def plot_forecast_data(prod_1,month_1,beg_1,end_1,prod_2,month_2,beg_2,end_2, periods, same_year=True, smoothed=False):

    # Receives as parameters the products to be analyzed from a possible pair strategy 
    # (like a calendar spread but also accepts combinations of products),
    # months of the contracts, start and end years and period to forecast. 
    # Returns a graph of the forecasts.

    # Validate the data types of the parameters
    if not isinstance(prod_1, str) or not isinstance(prod_2, str):
        raise TypeError("prod_1 and prod_2 must be strings.")
    
    if not isinstance(month_1, (int, float)) or not isinstance(month_2, (int, float)):
        raise TypeError("month_1 and month_2 must be numeric values.")
    
    if not isinstance(beg_1, (int, float)) or not isinstance(end_1, (int, float)):
        raise TypeError("beg_1 and end_1 must be numeric values.")
    
    if not isinstance(beg_2, (int, float)) or not isinstance(end_2, (int, float)):
        raise TypeError("beg_2 and end_2 must be numeric values.")
    
    if not isinstance(same_year, bool):
        raise TypeError("same_year must be True or False.")

    # Process data for prod_1
    df_1 = process_product_data(prod_1, month_1, beg_1, end_1)

    # Process data for prod_2
    df_2 = process_product_data(prod_2, month_2, beg_2, end_2)

    # Create column names based on product and month
    column_1 = f'_{prod_1}_{calendar.month_name[month_1][:3].lower()}'
    column_2 = f'_{prod_2}_{calendar.month_name[month_2][:3].lower()}'

    # Merge the two dataframes on 'date' column with appropriate suffixes
    df = pd.merge(df_1, df_2, on='date', suffixes=(column_1, column_2))

    # Calculate the spread by subtracting the 'close' values of column_2 from column_1
    df['spread'] = pd.to_numeric(df['close'+str(column_1)], errors='coerce') - pd.to_numeric(df['close'+str(column_2)], errors='coerce')

    # Create an empty list to store spread names
    spread_names = []

    # Iterate over each index in the dataframe
    for index in df.index:
        # Construct the spread name using various components
        spread_name = str(prod_1) + '_' + calendar.month_name[month_1].lower() + '_' + str(df.iloc[index,2]) + '_vs_' + str(prod_2) + '_' + calendar.month_name[month_2].lower() + '_' + str(df.iloc[index,4])
        # Append the spread name to the list
        spread_names.append(spread_name)

    # Assign the spread names to the 'spread_name' column in the dataframe
    df['spread_name'] = spread_names

    # Create a mask to compare the expiration values of column_1 and column_2
    if same_year == True:
        mask = df['expiration'+str(column_1)] != df['expiration'+str(column_2)]
    else:
        mask = df['expiration'+str(column_1)] == df['expiration'+str(column_2)]

    # Drop rows from the dataframe where the expiration values match
    df = df.drop(df[mask].index)

    # Create an empty DataFrame df_obs
    df_obs = pd.DataFrame()

    # Assign the 'date' column from df to 'ds' column in df_obs
    df_obs['ds'] = df['date']

    # Assign the 'spread' column from df to 'y' column in df_obs, converting it to float
    df_obs['y'] = df['spread'].astype(float)

    # Display the first few rows of df_obs
    df_obs.head()

    # Create a Prophet instance
    m = Prophet()

    # Fit the Prophet model to the observed data
    m.fit(df_obs)

    # Create a future dataframe with 200 additional periods
    future = m.make_future_dataframe(periods=periods)

    # Generate the forecast using the trained model
    forecast = m.predict(future)

    smoothed_forecast = pd.DataFrame()

    smoothed_forecast['ds'] = forecast['ds']

    # Smooth the 'yhat', 'yhat_lower', and 'yhat_upper' columns using a rolling mean with window size 7
    smoothed_forecast['yhat'] = forecast['yhat'].rolling(window=7, min_periods=1, center=True).mean()
    smoothed_forecast['yhat_lower'] = forecast['yhat_lower'].rolling(window=7, min_periods=1, center=True).mean()
    smoothed_forecast['yhat_upper'] = forecast['yhat_upper'].rolling(window=7, min_periods=1, center=True).mean()

    if smoothed == True:

        forecast = smoothed_forecast
    
    # Set dark theme
    style.use('default')
    
    # Create a figure with the desired size
    fig, ax = plt.subplots(figsize=(15, 5))

    # Plot the observed data
    ax.plot(m.history['ds'], m.history['y'], 'k.', label='Observed')

    # Plot the forecasted values
    ax.plot(forecast['ds'], forecast['yhat'], color='blue', label='Forecast')

    # Plot the uncertainty interval
    ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.3)

    # Set style and format
    plt.style.use('default')  # Revert to default style
    ax.set_title('Corn Futures Calendar Spread (Apr 2024 vs Dec. 2023) Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.legend()

    # Display the plot
    plt.show()
