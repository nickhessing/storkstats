import numpy as np
#from openpyxl.workbook import Workbook
import pandas as pd
from sqlalchemy import create_engine
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pprint import pprint
import os

print('KPI Framework started')

outname = 'KPIFramework_Python.csv'
outdir = 'assets/Attributes/dashboard_data'

if not os.path.exists(outdir):
    os.mkdir(outdir)

fullname = os.path.join(outdir, outname)
directory = 'assets/Attributes/dashboard_data'

f_kpi_synthetix = pd.DataFrame(pd.read_csv(
    "assets/Attributes/dashboard_data/f_kpi_synthetix.csv", sep=';', decimal=',', index_col=False))

facts = [f_kpi_synthetix]
f_kpi = pd.concat(facts)

# Dataframes Dimensions/attributes
tmp_d_kpi = pd.DataFrame(pd.read_csv(
    "assets/Attributes/dashboard_data/d_kpi_synthetix.csv", sep=';', index_col=False))
d_kpi = tmp_d_kpi[['d_kpi_id', 'Calculation', 'numerator_id',
                   'denominator_id', 'AggregateNum', 'AggregateDenom']]
d_date = pd.DataFrame(pd.read_csv(
    "assets/Attributes/dashboard_data/d_date.csv", sep=',', index_col=False))

keys = ['d_kpi_id', 'd_date_id']  # ,'d_level0_id','d_level1_id','d_level2_id'
Grain = ['full_date', 'LD_Month', 'LD_Quarter', 'LD_Year']
GrainName = ['D', 'M', 'Q', 'Y']
KPIIDList = d_kpi['d_kpi_id']
AggregateNumList = d_kpi['AggregateNum']
AggregateDenomList = d_kpi['AggregateDenom']


def AggregateNumerator(Aggregate):
    if Aggregate == 1:
        CalculationString = "'sum'"
        return CalculationString
    elif Aggregate == 2:
        CalculationString = "'mean'"
        return CalculationString
    elif Aggregate == 3:
        CalculationString = "'max'"
        return CalculationString


def AggregateDenominator(Aggregate):
    if Aggregate == 1:
        CalculationString = "'sum'"
        return CalculationString
    elif Aggregate == 2:
        CalculationString = "'mean'"
        return CalculationString
    elif Aggregate == 3:
        CalculationString = "'max'"
        return CalculationString


"""
-Create all newly created kpi's by searching for the numerator and the denominator in the existing kpi's
- Concat the old f_kpi with the newly created kpi's
"""

d_kpi_calculate = d_kpi[['d_kpi_id', 'numerator_id', 'denominator_id']]
a = d_kpi_calculate[d_kpi_calculate.denominator_id > 0]

Denomvaluedf = f_kpi[['d_kpi_id', 'd_level0_id',
                      'd_level1_id', 'd_level2_id', 'd_date_id', 'Numerator']]
f_kpi_cook = pd.merge(a, Denomvaluedf, how='left',
                      left_on='denominator_id', right_on='d_kpi_id')
f_kpi_cook.rename(columns={"Numerator": "Denominator",
                  "d_kpi_id_x": "d_kpi_id"}, inplace=True)
f_kpi_cook = f_kpi_cook.drop(
    columns=['d_kpi_id_y', 'numerator_id', 'denominator_id'], axis=1)
f_kpi_cook["Join"] = f_kpi_cook['d_kpi_id'].astype(str) + f_kpi_cook["d_level0_id"].astype(str) + f_kpi_cook["d_level1_id"].astype(
    str) + f_kpi_cook["d_level2_id"].astype(str) + f_kpi_cook["d_date_id"].astype(str)  # .astype(str)

f_kpi_cook2 = pd.merge(a, Denomvaluedf, how='left',
                       left_on='numerator_id', right_on='d_kpi_id')
f_kpi_cook2.rename(columns={"d_kpi_id_x": "d_kpi_id"}, inplace=True)
f_kpi_cook2 = f_kpi_cook2.drop(
    columns=['d_kpi_id_y', 'numerator_id', 'denominator_id'], axis=1)
f_kpi_cook2["Join"] = f_kpi_cook2['d_kpi_id'].astype(str) + f_kpi_cook2["d_level0_id"].astype(str) + f_kpi_cook2["d_level1_id"].astype(
    str) + f_kpi_cook2["d_level2_id"].astype(str) + f_kpi_cook2["d_date_id"].astype(str)  # .astype(str)

f_kpi_cook3 = f_kpi_cook.merge(f_kpi_cook2, on='Join', how='left')
f_kpi_cook3.drop(f_kpi_cook3.filter(regex='_y$').columns, axis=1, inplace=True)
f_kpi_cook3.columns = f_kpi_cook3.columns.str.rstrip('_x')
f_kpi_cook3 = f_kpi_cook3.drop(columns=['Join'], axis=1)
f_kpi_cook3.to_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Pythontmp4.csv', index=False)

f_kpi = pd.concat([f_kpi, f_kpi_cook3])
df_list = [f_kpi, d_kpi, d_date]

"""
-Join all reference tables to the dataframe with a loop
-Group by all relevant columns to calculate the numerator and denominator
-Loop through to repeat this for all the grains provided (time-grains)
-Create file for every grain calculated
"""


for z, o in zip(Grain, GrainName):
    for d, l, c in zip(KPIIDList, AggregateNumList, AggregateDenomList):
        df = df_list[0]
        for i, x in zip(df_list[1:], range(len(keys))):
            df = df.merge(i, on=keys[x])
        #del df['d_date_id']
        dfgrouped = df.groupby(['d_kpi_id', 'd_level0_id', 'd_level1_id', 'd_level2_id', z, o]).agg({'Numerator': [eval(
            AggregateNumerator(l))], 'Denominator': [eval(AggregateDenominator(c))]})  # 'Calculation','d_level0_id','d_level1_id','d_level2_id',
        grouped_multiple = dfgrouped.reset_index()
        grouped_multiple.columns = grouped_multiple.columns.droplevel(1)
        grouped_multiple['Grain'] = o
        grouped_multiple.rename(columns={z: 'Period_int'}, inplace=True)
        grouped_multiple.rename(columns={o: 'PeriodName'}, inplace=True)
        grouped_multiple.to_csv(
            r'assets/Attributes/dashboard_data/KPIFramework_Python_' + str(o) + '.csv')
KPIFrameworkDay = pd.DataFrame(pd.read_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Python_D.csv'))
KPIFrameworkMonth = pd.DataFrame(pd.read_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Python_M.csv'))
KPIFrameworkQuarter = pd.DataFrame(pd.read_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Python_Q.csv'))
KPIFrameworkYear = pd.DataFrame(pd.read_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Python_Y.csv'))

"""
-Concatenate the files created in previous step and create a new file with all grains concatenated. Distinguish by filtering on column 'grain'
-Convert period integer to datetime (needed later for visualisation and calculations)
-Calculate an extra column named 'Period in lp' meaning: the data of the previous period. This will be used later to join the numerator and denominator of the previous period
"""


KPIFrameworktmp = pd.concat(
    [KPIFrameworkDay, KPIFrameworkMonth, KPIFrameworkQuarter, KPIFrameworkYear])
KPIFrameworktmp["Period_int"] = pd.to_datetime(KPIFrameworktmp["Period_int"])
KPIFrameworktmp['Period_int_lp'] = KPIFrameworktmp[['Grain', 'Period_int']].apply(lambda x: x['Period_int'] + timedelta(days=+1) if x['Grain'] == 'D' else x['Period_int'] + timedelta(
    days=+365) if x['Grain'] == 'Y' else x['Period_int'] + relativedelta(months=+1) if x['Grain'] == 'M' else x['Period_int'] + relativedelta(months=+3) if x['Grain'] == 'Q' else x['Period_int'], axis=1)

"""
-Create two row-id's. One is for the dataframe itself and one is manipulated to be used to join
-Create second KPIFramework and only select numerator and denominator with the row_id_lp
-Merge the two ID's to add last period numerator and denominator to existing framework
-Drop unnesseccary columns
-Save file
"""

KPIFrameworktmp['Row_id'] = KPIFrameworktmp.apply(lambda x: x['Period_int'].strftime(
    '%Y%m%d') + str(x['d_kpi_id']) + str(x['d_level0_id']) + str(x['d_level1_id']) + str(x['d_level2_id']) + str(x['Grain']), axis=1)
KPIFrameworktmp['Row_id_lp'] = KPIFrameworktmp.apply(lambda x: x['Period_int_lp'].strftime(
    '%Y%m%d') + str(x['d_kpi_id']) + str(x['d_level0_id']) + str(x['d_level1_id']) + str(x['d_level2_id']) + str(x['Grain']), axis=1)

KPIFramework_LP = KPIFrameworktmp[['Row_id_lp', 'Numerator', 'Denominator']]
KPIFrameworktmp = KPIFrameworktmp.merge(KPIFramework_LP, how='left', left_on=[
                                        'Row_id'], right_on=['Row_id_lp'], suffixes=("", "_LP"))

KPIFrameworktmp = KPIFrameworktmp.drop(
    columns=['Row_id_lp', 'Row_id_lp_LP', 'Row_id', 'Unnamed: 0'], axis=1)


KPIFrameworktmp.to_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Pythontmp.csv', index=False)



KPIFrameworkOld = pd.DataFrame(pd.read_csv(
    r'assets/Attributes/dashboard_data/KPIFramework_Python.csv'))

KPIFrameworkNew = pd.concat(
    [KPIFrameworkOld, KPIFrameworktmp]).drop_duplicates().reset_index(drop=True)
# KPIFrameworkNew = KPIFrameworktmp  #Zet deze aan als je helemaal een nieuw framework wilt bouwen
KPIFrameworkNew.drop_duplicates()
KPIFrameworkNew2 = KPIFrameworkNew.drop_duplicates(
    subset=['d_kpi_id', 'd_level0_id', 'd_level1_id', 'd_level2_id', 'PeriodName', 'Grain'], keep='last')
KPIFrameworkNew2.to_csv(fullname, index=False)

print('KPI Framework loaded')
