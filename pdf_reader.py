#requirements
#have java installed
#pip install tabula-py
#pip install JPype1
#pip install pdfplumber
import tabula
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber


pdf_path = r"ddr3.pdf"

def plot_table_tabula():
    dfs = tabula.read_pdf(pdf_path, pages='all')
    #creating multiple csv files for each table
    # for i in range(len(dfs)):
    #     dfs[i].to_csv(f"page_2_table{i}.csv")
    print(dfs)
    
#plot_table_tabula()
    

    #plt.show()
#plot_table_tabula()


def table_pdfplumber():
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            print(len(tables))
          
#table_pdfplumber()   

def extract_tables_with_context(pdf_path):
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



tables_with_context = extract_tables_with_context(pdf_path)

# Create a DataFrame from the list of tuples
df = pd.DataFrame(tables_with_context, columns=["Table Name", "Table"])

# Assuming df is already defined
specific_table_name = "Timing Parameters by Speed Bin"

#find the table with the specific name
table = df[df["Table Name"] == specific_table_name]
table_data = table["Table"].iloc[0].extract()
#print(table_data)
def ExtractDesiredIndex(cat):
    indices = []  
    for i, inner_list in enumerate(table_data):
        for j, word in enumerate(inner_list):
            if word == cat:
                indices.append([i,j])  # Store the index as a tuple (outer list index, inner list index)
    return indices



def ExtractDataOfCat(cat):
    data = []
    listOfIndex = ExtractDesiredIndex(cat)
    firstIndex = listOfIndex[0][1]
    for innerList in table_data:
        data.append(innerList[firstIndex])
    return data
def CleanData(cat):
    data = ExtractDataOfCat(cat)
    try:
        index = data.index(cat)
        
        for i in range(index + 1):
            data.pop(0)  
        return data
    except ValueError:
        return data



        

    
data = CleanData("MIN")
print(data)
            



# Symbol Parameter  Min  Max of DDR3-1066    
# tCK(DLL_OFF)      5     -



        
        
