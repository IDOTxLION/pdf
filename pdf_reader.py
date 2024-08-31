#region imports & requirements
#requirements
#have java installed
#pip install tabula-py
#pip install JPype1
#pip install pdfplumber
#pip install "camelot-py[base]"
#import pymupdf
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
pd.set_option("display.max_columns", None)  
pd.set_option("display.max_rows", None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
#endregion
pdf_path = r"ddr4.pdf"
#region singular core extracts
def extract_tables_plumber(pdf_path):

    tables_with_context = {}
    
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
                tables_with_context[name] = table
    table_data = pd.DataFrame.from_dict(tables_with_context,orient="index").reset_index()
    table_data.columns = ['tablename', 'tabledata']
    return table_data
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
#region extract for specific word
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
#endregion
#region dynamicCode
def FilterTable(table_data): #filters anything that doesnt start with Table
        removeTablenames = table_data[table_data['tablename'].str.startswith('Table')]
        resetIndex = removeTablenames.reset_index(drop=True)
        return resetIndex
def find_symbol_column(headers_row1, headers_row2):#Find the index of the 'Symbol' column from 1st or 2nd row.
    if 'Symbol' in headers_row1:
        return headers_row1.index('Symbol')
    elif 'Symbol' in headers_row2:
        return headers_row2.index('Symbol')
    else:
        raise ValueError("Symbol column not found")
def extract_ddr_options_and_columns(first_row):# Find all DDR options and their column indexes. 
    ddr_options = []
    ddr_columns = []
    for idx, value in enumerate(first_row):
        if value and 'DDR' in value:
            ddr_options.append(value)
            ddr_columns.append(idx)
    return ddr_options, ddr_columns
def select_ddr_option(ddr_options):#Allow user to select a DDR option.
    print("DDR Options:")
    for idx, ddr in enumerate(ddr_options):
        print(f"{idx}: {ddr}")

    while True:
        try:
            chosen_ddr = input(f"Choose a DDR option (0-{len(ddr_options) - 1}): ")
            chosen_ddr = int(chosen_ddr)
            if 0 <= chosen_ddr < len(ddr_options):
                return chosen_ddr
            else:
                print(f"Invalid choice. Please choose a number between 0 and {len(ddr_options) - 1}.")
        except ValueError:
            print("Invalid input. Please enter a number corresponding to the DDR options.")
def print_table(selected_table):
    for row in selected_table:
        print(row)
def UserChoice(table_data): #Main code
    while True:
        print(table_data['tablename']) #print every table name for user to choose from
        try: #choose the table from the available indexes
            chosen_table = input(f"Choose an option (0-{len(table_data['tablename']) - 1}) or press 'z' to exit: ")
            if chosen_table.lower() == 'z':
                print("Exiting the selection.")
                break
            chosen_table = int(chosen_table)
            #Table[0-tableLenght-1]
            if 0 <= chosen_table < len(table_data):
                selected_table = table_data['tabledata'][chosen_table]
                table_name = table_data['tablename'][chosen_table]
                selected_table = selected_table.extract()
                print(table_name)

               #save first row for ddr search
                first_row = selected_table[0]
                #appends all ddr and associated column
                ddr_options, ddr_columns = extract_ddr_options_and_columns(first_row)
                
                #appends the symbols columns
                symbol_column_index = find_symbol_column(first_row, selected_table[1])
                
                if symbol_column_index is None:
                    print("Unable to find the 'Symbol' column in the table.")
                    continue

               #option to choose from printing whole table and to choose from all ddr option
                choice = input("Press 't' to print the whole table, 'd' to print DDR options: ").lower()
                if choice == 't':
                    print_table(selected_table)
                elif choice == 'd':
                    chosen_ddr_idx = select_ddr_option(ddr_options)
                    
                  
                    ddr_column_index = ddr_columns[chosen_ddr_idx]

                    
                    print(f"Selected DDR: {ddr_options[chosen_ddr_idx]}")
                    #print the all the colums of Symbol Min Max from each column
                    for row in selected_table[2:]:
                        symbol = row[symbol_column_index]
                        min_value = row[ddr_column_index]
                        max_value = row[ddr_column_index + 1]
                        print(f"{symbol}: {min_value} {max_value}")
                else:
                    print("Invalid input. Returning to table selection.")
                choice = input("Press 'b' to go back to the table selection or 'z' to exit: ").lower()
                if choice == 'z':
                    print("Exiting the selection.")
                    break
                elif choice != 'b':
                    print("Invalid input. Returning to table selection.")
            else:
                print(f"Invalid choice. Please choose a number between 0 and {len(table_data['tablename']) - 1}.")
        except ValueError:
            print("Invalid input. Please enter a number or 'z' to exit.")

#endregion
if __name__ == '__main__':
    start = time.perf_counter() 
    table_data = extract_tables_plumber(pdf_path)
    table_data = FilterTable(table_data)
    UserChoice(table_data)
  
    
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






        
        
