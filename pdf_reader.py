#region imports & requirements
#requirements
#have java installed
#pip install tabula-py
#pip install JPype1
#pip install pdfplumber
import pymupdf
import camelot
import tabula
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
import multiprocessing
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor
import os
import time
#endregion
pdf_path = r"ddr4.pdf"
#region singular core extracts
def extract_tables_plumber(pdf_path):

    tables_with_context = []
    
    with pdfplumber.open(pdf_path) as pdf:
        
        for page in pdf.pages:
            lines = page.extract_text_lines()
            for table in page.find_tables(dict(snap_tolerance=5)):
                previous_line = None
                for line in lines:
                    if line['top'] > table.bbox[1]:
                        break
                    previous_line = line
                if previous_line:
                    name = previous_line['text']
                else:
                    name = "Unknown"
                tables_with_context.append((name, table))
    return tables_with_context
def extract_tables_pymupdf(pdf_path):
    tables_with_context = []
    

    return tables_with_context
#endregion
#region multiple core extracts
def process_page(page_number):
    tables_with_context = []
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_number]
        lines = page.extract_text_lines()
        for table in page.find_tables({"snap_tolerance": 5}):
            previous_line = None
            for line in lines:
                if line['top'] > table.bbox[1]:
                    break
                previous_line = line
            if previous_line:
                name = previous_line['text']
            else:
                name = "Unknown"
            tables_with_context.append((name, table))
    return tables_with_context
def extract_tables_multiprocessingP(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        num_pages = len(pdf.pages)
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_page, range(num_pages))
    
    # Flatten the list of results
    tables_with_context = [item for sublist in results for item in sublist]
    return tables_with_context
def extract_tables_multiprocessingC(pdf_path):
    tables_with_context = []
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='all')
    for table in tables:
        for i, (index, row) in enumerate(table.df.iterrows()):
            name = row[0] if i == 0 else "Unknown"
            tables_with_context.append((name, table.df))
    return tables_with_context
#endregion
#region original  Extract for debugging purposes
def ExtractDesiredIndex1(cat):
    indices = []
    for i, inner_list in enumerate(table_data):
        for j, word in enumerate(inner_list):
            if word == cat: # Based on the MIN/MAX, you are not appending the rest
                #print ("DEBUG MIR", i, j)
                indices.append([i,j])  # Store the index as a tuple (outer list index, inner list index)          
    return indices
def ExtractDataOfCat1(cat):
    data = []
    listOfIndex = ExtractDesiredIndex(cat)
    index = listOfIndex[0][1]
    for innerList in table_data:
        data.append(innerList[index])
    return data
#endregion

def ExtractDesiredIndex(cat):
    indices = []
    label = []
    for i, inner_list in enumerate(table_data):
        for j, word in enumerate(inner_list):
            if word == cat: # Based on the MIN/MAX, you are not appending the rest
                indices.append([i,j])  # Store the index as a tuple (outer list index, inner list index)
            
    return indices
def ExtractDataOfCat(cat):
    data = []
    listOfIndex = ExtractDesiredIndex(cat)
    if len(listOfIndex) == 0:
        print(f"No occurrences of '{cat}' found.")
        return []
    if len(listOfIndex) > 1:
        print(f"'{cat}' found at multiple locations:")
        for idx, (i, j) in enumerate(listOfIndex):
            print(f"Option {idx}: Index [{i}, {j}]")
        
        try:
            user_choice = int(input(f"Choose an option (0-{len(listOfIndex) - 1}): "))
            if user_choice < 0 or user_choice >= len(listOfIndex):
                print("Invalid choice. Defaulting to the first option.")
                user_choice = 0
        except ValueError:
            print("Invalid input. Defaulting to the first option.")
            user_choice = 0
        
        selected_index = listOfIndex[user_choice]
    else:
        selected_index = listOfIndex[0]
    
    # Only use the inner index (j) from the selected index
    _, inner_index = selected_index
    for inner_list in table_data:
        data.append(inner_list[inner_index])
    
    return data
def CleanData(cat):
    data = ExtractDataOfCat(cat)
    try:
        index = data.index(cat)
        return data[index + 1:]  # Return elements after the index of cat
    except ValueError:
        return data  # Return the original list if cat is not found

def AllInfo():
        results = []
        data1=CleanData("Symbol")
        data2=CleanData("MIN")
        data3=CleanData("MAX")
        for d1, d2, d3 in zip(data1, data2, data3):
            results.append(f"{d1}: {d2} {d3}")
        return results
if __name__ == '__main__':
    start = time.perf_counter() 
    tables_with_context = extract_tables_plumber(pdf_path)
    for table in tables_with_context:
        print(table)
    # Create a DataFrame from the list of tuples
    # df = pd.DataFrame(tables_with_context, columns=["Table Name", "Table"])
    # specific_table_name = "Timing Parameters by Speed Bin"

    # #find the table with the specific name
    # table = df[df["Table Name"] == specific_table_name]
    # table_data = table["Table"].iloc[0].extract()
    # for i ,p in enumerate(table_data):
    #     print(i,p)
    
    # for line in AllInfo():
    #     print(line)   
    
    # data1 = CleanData("Symbol")
    # data2 = CleanData("MIN")
    # for d1,d2 in zip(data1,data2):
    #    print(d1,":",d2)
    #print(data)
   
    finish = time.perf_counter()

    print(f'Finishes in {round(finish-start, 2)} second(s)')






        
        
