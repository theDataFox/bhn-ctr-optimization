"""
Copyright (C) Lyla Yang - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Written by Lyla Yang <https://www.linkedin.com/in/lyla-yang-aa850080/>, May 2019
"""

"""
Reference of field attributes
https://developers.google.com/adwords/api/docs/appendix/reports#field-attributes
#init oauth refresh token client
oauth_client = oauth2.GoogleRefreshTokenClient(client_id=YOUR_GOOGLE_CLIENT_ID, client_secret=YOUR_GOOGLE_CLIENT_SECRET,refresh_token=YOUR_GOOGLE_REFRESH_TOKEN, proxy_config=proxy_config )

#adwords client
adwords_client = adwords.AdWordsClient(YOUR_DEVELOPER_TOKEN,oauth_client, user_agent=YOUR_USER_AGENT, client_customer_id=YOUR_CLIENT_CUSTOMER_ID, proxy_config=proxy_config)
"""

import glob
import io
from datetime import datetime, timedelta

import pandas as pd
from googleads import adwords

# Define the report date range: last 28 days including today
start = datetime.today().date().isoformat().replace("-", "")
end = datetime.now() + timedelta(days=- 28)
end = end.date().isoformat().replace("-", "")

# create a dictionary to storge three ad accounts information
Ad_acc = {'Brand-1': 'Adwords account ID 01', 'Brand-3': 'Adwords account ID 02', 'Brand-3': 'Adwords account ID 03'}


def run_Hour0fDay_kip_report(key, acc_id, start_date, end_date):
    '''
    This functioin is using report_downloader = adwords_client.GetReportDownloader(version='v201809') and 'CAMPAIGN_PERFORMANCE_REPORT'
    for more detail, please visit:
    input is the adwords account ID in dictionary items, start date, and end date, date format is yyymmdd
    out put is the campaign level reports
    '''

    '''
   Input variables: 
   1. key (brand name): from Dictionary Ad_acc. Type: string
   2. acc_id (adwords account ID): from Dictionary Ad_acc. Type: string
   3. start_date: report start date. Type: yyymmdd
   4. end_date: report end date. Type: yyymmdd
   Output: csv file 
    '''

    # Define output as a string
    output = io.StringIO()

    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage('.../adwords_config.yaml')

    adwords_client.SetClientCustomerId(acc_id)

    report_downloader = adwords_client.GetReportDownloader(version='v201809')

    report_query = (adwords.ReportQueryBuilder()
                    .Select('CampaignId', 'CampaignName', 'Date', 'DayOfWeek', 'HourOfDay', 'Clicks',
                            'Impressions', 'Cost', 'Conversions', 'ConversionValue')
                    .From('CAMPAIGN_PERFORMANCE_REPORT')
                    .Where('CampaignStatus').In('ENABLED')
                    .During(end_date + ',' + start_date)
                    .Build())

    report_downloader.DownloadReportWithAwql(report_query, 'CSV', output, skip_report_header=True,
                                             skip_column_header=False, skip_report_summary=True,
                                             include_zero_impressions=False)

    output.seek(0)

    types = {'CampaignId': pd.np.int64, 'Clicks': pd.np.float64, 'Impressions': pd.np.float64,
             'Cost': pd.np.float64, 'Conversions': pd.np.float64, 'ConversionValue': pd.np.float64}

    df = pd.read_csv(output, low_memory=False, dtype=types, na_values=[' --'])
    # delete the first and last column
    df['Brand'] = key
    # micro amount 1000000
    df['Cost'] = df.Cost / 1000000
    print(df.head())
    return df


# retrive KPIs for each adword account and generate csv file named by the brand name
for k, v in Ad_acc.items():
    df = run_campaign_performance_report(k, v, start, end)
    df.to_csv('.../' + k + '_adwords_HourOfDay_kpi.csv')

# Optional.You can also integrate all accounts data together. Comment lines below if you don't need them.
path = '.../HourOfDay Spend'
all_csv = glob.glob(path + '/*.csv', recursive=True)
list_df = (pd.read_csv(f) for f in all_csv)
all_df = pd.concat(list_df)
all_df.to_csv('.../all_adwords_HourOfDay_kpi.csv')
