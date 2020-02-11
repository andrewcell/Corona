import os
import sys
import multiprocessing
import webbrowser
from openpyxl.styles import Alignment
from pymed import PubMed
from datetime import datetime
from flask import Flask, render_template, request
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo


# Function for Create Excel file
def createWorksheet(data):
    wb = Workbook()
    sheet = wb.active
    sheet.append(["Article ID", "Title", "Abstract"]) # Column Label in First Line.

    for id, article in enumerate(data): # Read Data per article
        print("Found : " + article.pubmed_id) # Print article Id for Debugging
        lst = [article.pubmed_id, article.title, article.abstract] # ArticleID - Title - Abstract
        sheet.append(lst) # Add to worksheet
        for col in ["B", "C"]: # Enable Multi line on Title(Bn) Abstract(Cn) cell.
            sheet[col + str(id + 2)].alignment = Alignment(wrapText=True)

    table = Table(displayName="Data", ref="A1:C" + str(len(data) + 1)) # Make as Table
    style = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True) # Add Style to Table
    table.tableStyleInfo = style
    sheet.add_table(table) # Apply Table to Worksheet
    sheet.column_dimensions["B"].width = 150.0 # Expand cell width
    sheet.column_dimensions["C"].width = 200.0


    now = datetime.now().strftime("%m-%d-%Y, %H-%M-%S") # Current DateTime
    wb.save(now+".xlsx") # Save File with current datetime
    file = now+".xlsx"
    if sys.platform.startswith('win'): # If run on Microsoft Windows
        os.startfile(file) # Start Excel File. (Windows will launch default spreadsheet application)
    return now # Return filename

app = Flask(__name__)

store = list() # Search result will save here.

@app.route("/", methods=["GET", "POST"]) # Homepage
def root():
    global store # Will use global variable, defined above.
    if request.method == 'POST': # If is request from Form.
        pubmed = PubMed(tool="MyTool", email="my@email.address")
        #query = "occupational health[Title]"
        if (not "query" in request.form) or request.form["query"] == "": # If Search Query is empty or not exist
            return render_template("index.html", err="You must fill query input field.")
        query = request.form["query"] # Get querty from request parameters.

        # Execute the query against the API
        results = pubmed.query(query, max_results=100) # Max Result as 100
        store = list(results) # Save result to global variable for further use.
        return render_template('index.html', data=store)
    else:
        return render_template('index.html')


@app.route("/open", methods=["POST"]) # Export to Spreadsheet from selected article.
def open():
    global store
    if (not "selected" in request.form) or request.form["selected"] == "": # If Selected article is empty or not exist
        return render_template("index.html", err="You must fill query input field.")

    lists = []

    for item in request.form.getlist("selected"):
        lists.append(store[int(item)]) # Each selected item add to lists

    filename = createWorksheet(lists)
    if filename: # If Filename returned, Add Message that is created.
        return render_template("index.html", err=filename+".xlsx is created.")


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    webbrowser.open("http://127.0.0.1:5000/", autoraise=True) # Open Web browser to Local Server
    app.run()


