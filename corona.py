import os
import sys
import multiprocessing
from openpyxl.styles import Alignment
from pymed import PubMed
from datetime import datetime
from flask import Flask, render_template, request
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo


def createWorksheet(data):
    wb = Workbook()
    sheet = wb.active
    sheet.append(["Article ID", "Title", "Abstract"])

    for id, article in enumerate(data):
        print("Found : " + article.pubmed_id)
        lst = [article.pubmed_id, article.title, article.abstract]
        sheet.append(lst)
        for col in ["B", "C"]:
            sheet[col + str(id + 2)].alignment = Alignment(wrapText=True)


    table = Table(displayName="Data", ref="A1:C" + str(len(data) + 1))
    style = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)
    table.tableStyleInfo = style
    sheet.add_table(table)
    sheet.column_dimensions["B"].width = 150.0
    sheet.column_dimensions["C"].width = 200.0


    now = datetime.now().strftime("%m-%d-%Y, %H-%M-%S")
    wb.save(now+".xlsx")
    file = now+".xlsx"
    if sys.platform.startswith('win'):
        os.startfile(file)

    return now

app = Flask(__name__)

store = list()

@app.route("/", methods=["GET", "POST"])
def root():
    global store
    if request.method == 'POST':
        pubmed = PubMed(tool="MyTool", email="my@email.address")
        #query = "occupational health[Title]"
        if (not "query" in request.form) or request.form["query"] == "":
            return render_template("index.html", err="You must fill query input field.")
        query = request.form["query"]

        # Execute the query against the API
        results = pubmed.query(query, max_results=100)
        store = list(results)
        return render_template('index.html', data=store)
    else:
        return render_template('index.html')


@app.route("/open", methods=["POST"])
def open():
    global store
    if (not "selected" in request.form) or request.form["selected"] == "":
        return render_template("index.html", err="You must fill query input field.")

    lists = []

    for item in request.form.getlist("selected"):
        lists.append(store[int(item)])

    filename = createWorksheet(lists)
    if filename:
        return render_template("index.html", err=filename+".xlsx is created.")


if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    app.run()


