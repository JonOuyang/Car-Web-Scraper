import pandas as pd

read_file = pd.read_csv('data.csv')
read_file.to_excel('dataSpreadsheet.xlsx', index=None, header=True)