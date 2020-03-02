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
import re
import xlsxwriter

from pymed import PubMed
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from nltk import tokenize, word_tokenize, sent_tokenize, download
from nltk.tokenize.treebank import TreebankWordDetokenizer


# 엑셀 파일 생성.
def createWorksheet(data):
    filename = datetime.now().strftime("%m-%d-%Y, %H-%M-%S") + ".xlsx"  # 현재 일자 시간
    wb = xlsxwriter.Workbook(filename)  # 현재의 일자 시간을 파일명에 사용
    sheet = wb.add_worksheet()

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

    keywordStyle = wb.add_format({'color': keywordHighlightColor})
    sentenceStyle = wb.add_format({'color': sentenceHighlightColor})
    cellformat = wb.add_format({'align': 'vcenter', 'text_wrap': True})

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

        newAbstract = list()
        for sentence in article.abstract:
            if type(sentence) is list:
                newAbstract.append(sentenceStyle)
                for partid, part in enumerate(sentence):
                    if type(part) is dict:
                        newAbstract.append(keywordStyle)  # 키워드에 대한 스타일
                        newAbstract.append(str(part["matched"]))
                        newAbstract.append(sentenceStyle)
                    else:

                        if len(sentence) - 1 == partid:
                            newAbstract.append(part + " ")
                        else:
                            newAbstract.append(part)
            else:
                newAbstract.append(str(sentence) + " ")
        index = str(id + 2)
        sheet.write_string('A' + index, journal, cell_format=cellformat)
        sheet.write_string('B' + index, article.title, cell_format=cellformat)
        if len(newAbstract) >= 1:
            sheet.write_rich_string('C' + str(id + 2), *newAbstract)
        else:
            sheet.write('C' + index, "")
        sheet.write_string('D' + str(id + 2), url, cell_format=cellformat)  # URL 셀 하이퍼링크 처리.

    columnTitle = list()
    for columnLetter, column in columns.items():  # 각 열의 가로 길이를 설정하고 스타일을 설정함.
        columnTitle.append({'header': column["title"]})  # 첫번째 열에 컬럼의 이름을 입력합니다.
        sheet.set_column(columnLetter + ":" + columnLetter, column["width"], cell_format=cellformat)

    sheet.add_table("A1:D" + str(len(data) + 1),
                    {'style': 'Table Style Light 9', 'columns': columnTitle})  # 리스트를 테이블화 함

    wb.close()
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


def isSpecialChar(string):
    # Make own character set and pass
    # this as argument in compile method
    regex = re.compile('[.,@_!#$%^&*()<>?/\|}{~:]')

    # Pass the string in search
    # method of regex object.
    if (regex.search(string) == None):
        return True

    else:
        return False


if getattr(sys, 'frozen', False):  # EXE 파일 실행 시
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:  # 스크립트 파일로 실행
    app = Flask(__name__)

store = list()  # 검색 결과가 여기에 저장됨.
resultLimit = 100  # 최대 결과 수
keywordHighlightColor = "#ff0000"  # 검색한 키워드 강조 색상 (기본 값: 빨간색)
sentenceHighlightColor = "#008000"  # 키워드 포함 문장 강조 색상 (기본 값: 초록색)


@app.route("/", methods=["GET", "POST"])  # 첫 화면.
def root():
    global store, resultLimit, keywordHighlightColor, sentenceHighlightColor  # 위에서 만든 변수들을 사용
    if request.method == 'POST':  # 검색 버튼으로 요청했을 경우.
        pubmed = PubMed(tool="MyTool", email="my@email.address")

        if (not "query" in request.form) or request.form["query"] == "":  # 쿼리문을 받지 못했을 경우.
            return render_template("index.html", err="필수 입력 값이 입력되지 않았습니다.")

        query = request.form["query"]  # 페이지의 쿼리문 입력 공간 = query.

        results = pubmed.query(query, max_results=int(resultLimit))  # 최대 결과 개수를 resultLimit개로 제한하고 쿼리문으로 검색함.

        keywords = str(query).split()
        searchKeywords = list()
        for keyword in keywords:
            keyword = keyword.split("[")
            option = ""
            if len(keyword) == 2:
                option = keyword[1].split("]")[0]
            word = keyword[0]
            if (
                    option == "" or option == "Title/Abstract") and word.lower() != "and" and word.lower() != "or":  # 일단 Abstract 제외한 검색 유형은 제외함. AND OR는 연산자 이므로 제외함.
                searchKeywords.append({"word": word, "option": option})
        store = list(results)  # 받은 값을 배열화하고 바깥 store 에 저장함.

        newStore = list()
        for article in store:
            if article.abstract or not article.abstract == "":
                sentences = sent_tokenize(str(article.abstract))
                newAbstractSentences = list()

                count = 1
                for sentence in sentences:
                    count = count + 1
                    words = word_tokenize(sentence)
                    newSentence = list()
                    otherWords = list()
                    for id, word in enumerate(words):
                        found = False
                        for searchWord in searchKeywords:
                            if word.lower() == searchWord["word"].lower():
                                found = True

                        if found:
                            if isSpecialChar(words[id - 1][-1]):
                                word = " " + word
                            newSentence.append(TreebankWordDetokenizer().tokenize(tokens=otherWords))
                            otherWords.clear()
                            if isSpecialChar(words[id + 1][0]):
                                word = word + " "
                            newSentence.append({"matched": word})
                        else:
                            otherWords.append(word)

                    if len(otherWords) >= 1:  # 해당 단어 뒤에 있는 내용들이 있으면 함께 추가함.
                        newSentence.append(TreebankWordDetokenizer().tokenize(tokens=otherWords))

                    if len(newSentence) <= 0:
                        newSentence.append(TreebankWordDetokenizer().tokenize(tokens=words))
                    else:
                        if len(newSentence) == 1:
                            newAbstractSentences.append(newSentence[0])
                        else:
                            newAbstractSentences.append(newSentence)
                article.abstract = newAbstractSentences
            newStore.append({
                "abstract": article.abstract,
                "journalissue": {
                    "ISOName": article.journalissue["ISOName"],
                    "PubDate_Year": article.journalissue["PubDate_Year"]
                },
                "title": article.title
            })
        # Hello world. This server is normal server you know. thank you. // Keyword : server
        # ["Hello world.", ["This ", {"matched": "server"}, "is normal ", {"matched": "server"}, " you know."], ". thank you"]
        # check it is object or list object, first list, it is highlight sentence, in that sentence if object, it is highlighted word.
        # ["Seperated Sentence #1", ["Seperated word #1", {"matched": "searchWord"}, "Seperated word #2"], "Seperated Sentence #2]

        if len(store) == int(resultLimit):  # 데이터의 개수가 resultLimit개 인 경우 검색 결과가 잘렸음을 알림
            resultMessage = "검색 결과가 많아 " + str(resultLimit) + "개로 제한하였습니다. 검색어를 구체화하세요."
        else:
            resultMessage = str(len(store)) + "개를 찾았습니다."
        return jsonify({"code": 200, "comment": resultMessage, "data": newStore,
                        "color": {"sentence": sentenceHighlightColor, "keyword": keywordHighlightColor}})
    else:  # 접속 시.
        version = getversion()
        return render_template('index.html', version=version)


@app.route("/open", methods=["POST", "GET"])  # 선택된 논문을 처리합니다.
def open():
    global store, keywordHighlightColor, sentenceHighlightColor
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


@app.route("/saveconfig", methods=["POST"])  # 설정을 저장합니다
def saveConfig():
    global resultLimit, keywordHighlightColor, sentenceHighlightColor
    if request.method == "POST":
        form = request.form
        if request.form is None or (not "resultLimit" in form) or (not "titleColor" in form) or (
        not "sentColor" in form):
            return Response(status=400)
        try:
            resultLimit = form["resultLimit"]
            keywordHighlightColor = form["titleColor"]
            sentenceHighlightColor = form["sentColor"]
        except:
            return Response(status=400)
        finally:
            return jsonify({'comment': 'success'})


@app.route("/getconfig", methods=["GET"])  # 설정을 불러옵니다.
def getConfig():
    global resultLimit, keywordHighlightColor, sentenceHighlightColor
    return jsonify({"result": resultLimit, "keyword": keywordHighlightColor, "sentence": sentenceHighlightColor});


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
    download("punkt")
    webbrowser.open("http://127.0.0.1:8484/", autoraise=True)  # Open Web browser to Local Server
    app.run(port=8484)
