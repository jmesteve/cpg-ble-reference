import pandas as pd
import csv
import shutil


from pathlib import Path



template_excel = Path("reports/Memory Optimization Template.xlsx")
csv_file = Path("reports/central_hids/nrf54l15_std1/ram.csv")
excel_file = Path("reports/central_hids/summary.xlsx")


shutil.copy2(template_excel, excel_file)

writer = pd.ExcelWriter(excel_file, engine='openpyxl', mode='a')


csv =pd.read_csv(csv_file)

df1 = pd.DataFrame(csv)

csv.to_excel(writer, sheet_name = "feat12", index=None, header=True)
writer.close()