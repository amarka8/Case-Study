import os
import weasyprint
from weasyprint import HTML
import re

input_path = './sec_data/2024/QTR1'
#get list of all folders containing contracts 
folders = os.listdir(input_path)
for folder in folders:
    folder_path = os.path.join(input_path, folder)
    htm_files = []
    if os.path.isdir(folder_path):
        htm_files = os.listdir(folder_path)
    for file in htm_files:
        final_path = os.path.join(folder_path,file.replace(".htm",".pdf"))
        HTML(os.path.join(folder_path,file)).write_pdf(final_path)
