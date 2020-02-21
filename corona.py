#
# Corona
# Author: Andrew M. Bray (Seungyeon Choi)
# Repository: https://github.com/andrewcell/Corona
# pymed : https://github.com/gijswobben/pymed
#
import os
import sys
import multiprocessing
import webbrowser
import requests
import json

from pymed import PubMed
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo


# 엑셀 파일 생
def createWorksheet(data):
    # { Example Data
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
    # }
    wb = Workbook()
    sheet = wb.active

    columns = {
        "A": {
            "title": "Journal",
            "width": 15.0
        },
        "B": {
            "title": "Title",
            "width": 100.0
        },
        "C": {
            "title": "Abstract",
            "width": 150.0
        },
        "D": {
            "title": "URL",
            "width": 40.0
        }
    }

    sheet.append([""])

    for id, article in enumerate(data):  # id 는 enumerate 를 통해 생성 0부터 시작하는 인덱스 값, article 은 data에 저장된 각 논문
        print("Found : " + article.pubmed_id)  # 정상 작동 여부를 확인하기 위한 아이디 노출.

        url = "https://www.ncbi.nlm.nih.gov/pubmed/" + article.pubmed_id # 해당 논문의 URL 값 처리
        journal_year = article.journalissue["PubDate_Year"]
        journal_year =  "" if journal_year is None else journal_year  # 저널의 연도 정보를 체크하여 없으면 공백으로 표시함.
        journal = article.journalissue["ISOName"] + " " + journal_year

        lst = [journal, article.title, article.abstract, url]  # 저널명 - 제목 - Abstract - 주소 순으로 정렬함.

        sheet.append(lst)  # 엑셀 워크시트에 위 정렬된 것을 마지막 줄에 추가.
        sheet['D' + str(id + 2)].hyperlink = url # URL 셀 하이퍼링크 처리.

    for columnLetter, column in columns.items():  # 각 열의 가로 길이를 설정하고 스타일을 설정함.
        sheet[columnLetter + "1"] = column["title"] # 첫번째 열에 컬럼의 이름을 입력합니다.
        sheet.column_dimensions[columnLetter].width = column["width"]
        for index in range(len(data) + 2): # 컬럼 자체를 스타일 설정이 불가능하여 논문(데이터)의 개수를 세어 개수+1만큼의 행마다 스타일을 설정합니다.
            sheet[columnLetter + str(index + 1)].alignment = Alignment(wrapText=True, vertical='center')

    table = Table(displayName="Data", ref="A1:D" + str(len(data) + 1))  # 리스트를 테이블화 함
    style = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)

    table.tableStyleInfo = style # 테이블에 스타일을 적용함
    sheet.add_table(table)  # 워크시트에 테이블을 적용함

    filename = datetime.now().strftime("%m-%d-%Y, %H-%M-%S") + ".xlsx" # 현재 일자 시간
    wb.save(filename)  # 현재의 일자 시간을 파일명에 사용

    if sys.platform.startswith('win'):  # 윈도우에서 실행 시
        os.startfile(filename)  # 엑셀 파일 실행 (윈도우가 기본 스프레드시트 프로그램을 통해 실행함)
    return filename  # 파일 이름을 최종 반환.


def getversion():
    try:
        latest = json.loads(requests.get("https://api.github.com/repos/andrewcell/Corona/releases").text)[0]
        asset = latest["assets"][0]
        return [latest["name"], latest["published_at"], asset["browser_download_url"]]
    except:
        return None

if getattr(sys, 'frozen', False): # EXE 파일 실행 시
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else: # 스크립트 파일로 실행
    app = Flask(__name__)

store = list()  # 검색 결과가 여기에 저장됨.


@app.route("/", methods=["GET", "POST"])  # 첫 화면.
def root():
    global store  # 위에서 만든 store 를 사용
    if request.method == 'POST':  # 검색 버튼으로 요청했을 경우.
        pubmed = PubMed(tool="MyTool", email="my@email.address")

        if (not "query" in request.form) or request.form["query"] == "":  # 쿼리문을 받지 못했을 경우.
            return render_template("index.html", err="필수 입력 값이 입력되지 않았습니다.")

        query = request.form["query"]  # 페이지의 쿼리문 입력 공간 = query.

        results = pubmed.query(query, max_results=100)  # 최대 결과 개수를 100개로 제한하고 쿼리문으로 검색함. (여기 수정 시 밑에도 수정해야 함.)
        store = list(results)  # 받은 값을 배열화하고 바깥 store 에 저장함

        if len(store) == 100: # 데이터의 개수가 100개 인 경우 검색 결과가 잘렸음을 알림
            resultMessage = "검색 결과가 많아 100개로 제한하였습니다. 검색어를 구체화하세요."
        else:
            resultMessage = str(len(store)) + "개를 찾았습니다."

        return render_template('index.html', data=store, resultMsg=resultMessage)
    else: # 접속 시.
        version = getversion()
        print(version)
        return render_template('index.html', version=version)


@app.route("/open", methods=["POST", "GET"])  # 선택된 논문을 처리합니다.
def open():
    global store
    if request.method == "POST":
        if (not "selected" in request.form) or request.form["selected"] == "":  # 선택된 논문이 없을경우.
            return render_template("index.html", err="선택된 논문이 없습니다.")

        lists = []

        for item in request.form.getlist("selected"):
            lists.append(store[int(item)])  # 선택된 논문을 배열에 집어넣습니다.

        filename = createWorksheet(lists)
        if filename:  # 파일명을 받은 경우 파일명과 함께 메세지를 표출합니다.
            return render_template("index.html", msg=filename + " 파일이 생성되었습니다.")
    else:
        return redirect(url_for('root'))


@app.route("/terminate", methods=["GET"])
def terminate():
    os._exit(0)

@app.after_request
def add_header(r):
    """
    HTML, CSS, Javascript 파일이 브라우저 캐시에 의해 최신 변경점이 반영되지 않는 문제점이 있습니다.
    브라우저에 캐시를 사용하지 말 것을 보냅니다.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # 윈도우에서의 오류 제거
        multiprocessing.freeze_support()

    webbrowser.open("http://127.0.0.1:8484/", autoraise=True)  # Open Web browser to Local Server
    app.run(port=8484)
