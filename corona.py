"""
 Corona
 Author: Andrew M. Bray (Seungyeon Choi)
 Author E-mail: lisa.su@kakao.com
 Repository: https://github.com/andrewcell/Corona
 pymed : https://github.com/gijswobben/pymed

"""
import os
import sys
import multiprocessing
import webbrowser
import requests
import json

from pymed import PubMed
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo


# 엑셀 파일 생성.
def createWorksheet(data, query):
    wb = Workbook()
    sheet = wb.active

    columns = {
        "A": {
            "title": "#",
            "width": 2.0
        },
        "B": {
            "title": "Journal",
            "width": 15.0
        },
        "C": {
            "title": "Title",
            "width": 100.0
        },
        "D": {
            "title": "Abstract",
            "width": 150.0
        },
        "E": {
            "title": "URL",
            "width": 40.0
        }
    }

    sheet.append([""])

    for id, article in enumerate(data):  # id 는 enumerate 를 통해 생성 0부터 시작하는 인덱스 값, article 은 data에 저장된 각 논문
        print("Found : " + article.pubmed_id)  # 정상 작동 여부를 확인하기 위한 아이디 노출.

        url = "https://www.ncbi.nlm.nih.gov/pubmed/" + article.pubmed_id  # 해당 논문의 URL 값 처리

        if hasattr(article, "journalissue"):  # 저널의 연도 정보를 체크하여 없으면 공백으로 표시함.
            if "ISOName" in article.journalissue:
                if article.journalissue["ISOName"] is not None:
                    ISOName = article.journalissue["ISOName"]
            else:
                ISOName = ""
            if "PubDate_Year" in article.journalissue:
                if article.journalissue["PubDate_Year"] is not None:
                    journal_year = article.journalissue["PubDate_Year"]
            else:
                journal_year = ""
        else:
            journal_year = ""
            ISOName = ""

        journal = ISOName + " " + journal_year

        lst = [id+1, journal, article.title, article.abstract, url]  # 저널명 - 제목 - Abstract - 주소 순으로 정렬함.

        sheet.append(lst)  # 엑셀 워크시트에 위 정렬된 것을 마지막 줄에 추가.
        sheet['E' + str(id + 2)].hyperlink = url  # URL 셀 하이퍼링크 처리.

    for columnLetter, column in columns.items():  # 각 열의 가로 길이를 설정하고 스타일을 설정함.
        sheet[columnLetter + "1"] = column["title"]  # 첫번째 열에 컬럼의 이름을 입력합니다.
        sheet.column_dimensions[columnLetter].width = column["width"]
        for index in range(len(data) + 2):  # 컬럼 자체를 스타일 설정이 불가능하여 논문(데이터)의 개수를 세어 개수+1만큼의 행마다 스타일을 설정합니다.
            sheet[columnLetter + str(index + 1)].alignment = Alignment(wrapText=True, vertical='center')

    table = Table(displayName="Data", ref="A1:E" + str(len(data) + 1))  # 리스트를 테이블화 함
    style = TableStyleInfo(name="TableStyleLight9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=True)

    table.tableStyleInfo = style  # 테이블에 스타일을 적용함
    sheet.add_table(table)  # 워크시트에 테이블을 적용함

    filename = query + "_" + datetime.now().strftime("%Y%m%d") + ".xlsx"  # 쿼리, 현재 일자
    wb.save(filename)

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


if getattr(sys, 'frozen', False):  # EXE 파일 실행 시
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:  # 스크립트 파일로 실행
    app = Flask(__name__)

store = list()  # 검색 결과가 여기에 저장됨.
resultLimit = 100 # 최대 결과 수
query = ""

@app.route("/", methods=["GET", "POST"])  # 첫 화면.
def root():
    global store, resultLimit, query # 위에서 만든 변수들을 사용
    if request.method == 'POST':  # 검색 버튼으로 요청했을 경우.
        pubmed = PubMed(tool="MyTool", email="my@email.address")

        if (not "query" in request.form) or request.form["query"] == "":  # 쿼리문을 받지 못했을 경우.
            return render_template("index.html", err="필수 입력 값이 입력되지 않았습니다.")

        query = request.form["query"]  # 페이지의 쿼리문 입력 공간 = query.

        results = pubmed.query(query, max_results=int(resultLimit))  # 최대 결과 개수를 resultLimit개로 제한하고 쿼리문으로 검색함.
        store = list(results)  # 받은 값을 배열화하고 바깥 store 에 저장함

        if len(store) == int(resultLimit):  # 데이터의 개수가 resultLimit개 인 경우 검색 결과가 잘렸음을 알림
            resultMessage = "검색 결과가 많아 " + str(resultLimit) + "개로 제한하였습니다. 검색어를 구체화하세요."
        else:
            resultMessage = str(len(store)) + "개를 찾았습니다."

        return render_template('index.html', data=store, resultMsg=resultMessage)
    else:  # 접속 시.
        version = getversion()
        print(version)
        return render_template('index.html', version=version)


@app.route("/open", methods=["POST", "GET"])  # 선택된 논문을 처리합니다.
def open():
    global store, query
    if request.method == "POST":
        if (not "selected" in request.form) or request.form["selected"] == "":  # 선택된 논문이 없을경우.
            return render_template("index.html", err="선택된 논문이 없습니다.")

        lists = []

        for item in request.form.getlist("selected"):
            lists.append(store[int(item)])  # 선택된 논문을 배열에 집어넣습니다.

        filename = createWorksheet(lists, query)
        if filename:  # 파일명을 받은 경우 파일명과 함께 메세지를 표출합니다.
            return render_template("index.html", msg=filename + " 파일이 생성되었습니다.")
    else:
        return redirect(url_for('root'))


@app.route("/terminate", methods=["GET"])
def terminate():
    os._exit(0)


@app.route("/saveconfig", methods=["POST"]) # 설정을 저장합니다
def saveConfig():
    global resultLimit
    if request.method == "POST":
        form = request.form
        if request.form is None or (not "resultLimit" in form):
            return Response(status=400)
        try:
            resultLimit = form["resultLimit"]
        except:
            return Response(status=400)
        finally:
            return jsonify({'comment': 'success'})



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
