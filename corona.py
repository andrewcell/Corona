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
    #{ Example Data
    #    "abstract": "Cancer remains a leading cause of death, despite multimodal treatment approaches. Even in patients with a healthy immune response, cancer cells can escape the immune system during tumorigenesis. Cancer cells incapacitate the normal cell-mediated immune system by expressing immune modulation ligands such as programmed death (PD) ligand 1, the B7 molecule, or secreting activators of immune modulators. Chimeric antigen receptor (CAR) T cells were originally designed to target cancer cells. Engineered approaches allow CAR T cells, which possess a simplified yet specific receptor, to be easily activated in limited situations. CAR T cell treatment is a derivative of the antigen-antibody reaction and can be applied to various diseases. In this review, the current successes of CAR T cells in cancer treatment and the therapeutic potential of CAR T cells are discussed.",
    #    "authors": [
    #        {
    #            "affiliation": "Department of Pharmacology, Chonnam National University Medical School, Hwasun, Korea.",
    #            "firstname": "Somy",
    #            "initials": "S",
    #            "lastname": "Yoon"
    #        },
    #        {
    #            "affiliation": "Department of Pharmacology, Chonnam National University Medical School, Hwasun, Korea.",
    #            "firstname": "Gwang Hyeon",
    #            "initials": "GH",
    #           "lastname": "Eom"
    #       }
    #    ],
    #    "conclusions": null,
    #    "copyrights": "\u00a9 Chonnam Medical Journal, 2020.",
    #    "doi": "10.4068/cmj.2020.56.1.6",
    #    "journal": "Chonnam medical journal",
    #    "keywords": [
    #        "CAR T cell",
    #        "Combined Modality Therapy",
    #        "Ligands",
    #        "Neoplasms",
    #        "T-Lymphocytes"
    #    ],
    #    "methods": null,
    #    "publication_date": "2020-02-06",
    #    "pubmed_id": "32021836\n17344846\n16417215\n25893595\n28799485\n11403834\n31019670\n29742380\n25510272\n28726836\n21994741\n26663085\n19459844\n30592986\n26568292\n30082599\n29385370\n28983798\n18034592\n25765070\n10585967\n31511695\n21293511\n28857075\n29855723\n23636127\n27785449\n25999455\n30261221\n19132916\n19636327\n27365313\n31723827\n28936279\n22129804\n29686425\n27626062\n30747012\n29389859\n25440610\n28652918\n29025771\n18986838\n28555670\n29667553\n28292435\n11585784\n24076584\n24432303\n25501578\n29226797\n18541331\n27207799\n18481901\n23546520\n30036350",
    #    "results": null,
    #    "title": "Chimeric Antigen Receptor T Cell Therapy: A Novel Modality for Immune Modulation.",
    #    "xml": "<Element 'PubmedArticle' at 0x106847f50>"
    #}
    wb = Workbook()
    sheet = wb.active
    sheet.append(["Article ID", "Title", "Abstract", "URL"]) # Column Label in First Line.

    for id, article in enumerate(data): # Read Data per article
        print("Found : " + str(article.toJSON())) # Print article Id for Debugging
        url = "https://www.ncbi.nlm.nih.gov/pubmed/" + article.pubmed_id
        lst = [article.pubmed_id, article.title, article.abstract, url] # ArticleID - Title - Abstract - Article URL
        sheet.append(lst) # Add to worksheet
        sheet['D' + str(id + 2)].hyperlink = url
        for col in ["B", "C"]: # Enable Multi line on Title(Bn) Abstract(Cn) cell.
            sheet[col + str(id + 2)].alignment = Alignment(wrapText=True)

    table = Table(displayName="Data", ref="A1:D" + str(len(data) + 1)) # Make as Table
    style = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True) # Add Style to Table
    table.tableStyleInfo = style
    sheet.add_table(table) # Apply Table to Worksheet
    sheet.column_dimensions["B"].width = 100.0 # Expand cell width
    sheet.column_dimensions["C"].width = 150.0
    sheet.column_dimensions["D"].width = 40.0


    now = datetime.now().strftime("%m-%d-%Y, %H-%M-%S") # Current DateTime
    wb.save(now+".xlsx") # Save File with current datetime
    file = now+".xlsx"
    if sys.platform.startswith('win'): # If run on Microsoft Windows
        os.startfile(file) # Start Excel File. (Windows will launch default spreadsheet application)
    return now # Return filename

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
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


