/*
 ____
/\  _`\
\ \ \/\_\    ___   _ __   ___     ___      __
 \ \ \/_/_  / __`\/\`'__\/ __`\ /' _ `\  /'__`\
  \ \ \L\ \/\ \L\ \ \ \//\ \L\ \/\ \/\ \/\ \L\.\_
   \ \____/\ \____/\ \_\\ \____/\ \_\ \_\ \__/.\_\
    \/___/  \/___/  \/_/ \/___/  \/_/\/_/\/__/\/_/

index.js - 사용자에게 개선된 UI 를 제공합니다.
Author - Andrew M. Bray (Seungyeon Choi)
*/

function generateOptions() { // 리스트박스에 들어갈 값들을 생성합니다.
    const values = [
        ["All Fields", "전체(질환/성분)"], // 좌- PubMed 의 값, 우-사용자에게 보여지는 값
        ["Author", "저자"],
        ["Journal", "저널명"],
        ["Title", "논문제목"],
        //["Date - Publication", "발행연도"],
        ["Title/Abstract", "논문제목/요약"]
    ];
    var tag = "";
    values.forEach(function (value) {
        tag = tag + "<option value='" + value[0] + "'>" + value[1] + "</option>";
    });
    return tag;
}

function startsWith(str, word) { // 시작 단어를 검색
    return str.lastIndexOf(word, 0) === 0;
}

function generateQuery() { // 최종적으로 전달 될 Query 통문을 생성
    const queryField = $("#query");

    var query = "";

    queryField.val(""); // Query 입력 칸을 지웁니다
    const arr = $("form#fields").serializeArray(); // 각 입력칸들을 배열화하여 저장한비다.
    if (arr[0].value === "All Fields") {
        query = query + arr[1].value;
    } else {
        query = query + arr[1].value + "[" + arr[0].value + "]";
    }
    //console.log(arr);
    for (var i = 2; i < arr.length ; i+=3) {
        var operator = undefined;
        var type = undefined;
        var value = undefined;

        if( arr[i + 2].value !== "") {
            if (startsWith(arr[i].name, "operator")) {
                operator = arr[i].value.toUpperCase();
            }
            /*if (arr[i].name.startsWith("operator")) { // Not working in Internet Explorer.
                operator = arr[i].value.toUpperCase();
            }*/
            
            if (arr[i + 1].name === "type") {
                type = arr[i + 1].value;
            }
            
            if (arr[i + 2].name === "value") {
                value = arr[i + 2].value;
                
            }

            query = query + " " + operator + " " + value;

            if (type !== "All Fields") {
                query = query + "[" + type + "]";
            }

        }

    }
    queryField.val(query);

}

$(document).ready(function() {
    $("#defaultOption").empty(); // 새로고침 발생 시 값들을 초기화합니다.
    $("#defaultOption").append(generateOptions());

    var count = 1;

    $("input#add").click(function() {
        count++;
        $("div [data=first]").append( // 첫번째 입력값이라고 마킹된 항목 밑에 입력칸을 통째로 생성합니다. count 는 이들을 구별하기 위해 사용합니다.
            '<div class="form-group" data-index=' + count + '>' +
            '<div class="form-check form-check-inline">' +
            '<input class="form-check-input" type="radio" name="operator_' +count + '" id="and" value="and" checked>' +
            '<label class="form-check-label" for="and">AND</label>' +
            '</div>' +
            '<div class="form-check form-check-inline">' +
            '    <input class="form-check-input" type="radio" name="operator_' +count + '" id="or" value="or">' +
            '    <label class="form-check-label" for="or">OR</label>' +
            '</div>' +
            '<div class="input-group">' +
            '<div class="input-group-prepend">' +
            '    <select class="custom-select" name="type" index="' + count + '">' +
                    generateOptions() + // <select> 밑에 들어가야하는 <option> 태그들은 generateOptions() 에서 받습니다.
            '    </select>' +
            '</div>' +
            '<input type="text" name="value" index="' + count + '" class="form-control" placeholder="여기에 영문으로 검색하세요.">' +
            '<div class="input-group-append">' +
            '    <input type="button" class="btn btn-outline-secondary" type="button" id="delete" data-index="' + count + '" value="Delete"/>' +
            '  </div>' +
            '</div>' +
            '</div>'
        );
    });

    $("form [data=first]").on("click", "#delete", function () { //삭제 버튼을 누른경우
        $(".form-group [data-index=" + $(this).attr("data-index") + "]").remove();
    });

    $("#search").click(function() { // 검색 버튼을 누른 경우
        $("form#queryForm").submit();
    });

    $("#settings").click(function() { // 설정 버튼을 누른 경우 설정 팝업을 띄움
        $("#configModal").modal('toggle');
    });

    $("#clear").click(function() { // Clear 버튼을 누른 경우 값을 다 지우고 새로고침
        $("input#query").val("");
        $("input#first").val("");
        location.reload();
    });

    $(document).on('change', 'input', function(event) { // 하나라도 입력 칸이 바뀐 경우
        if(event.target.id === "query") { // Query 입력 칸이 변경된 경우 아무것도 하지 않습니다.
            return;
        }

        if(event.target.id === "resultLimit" || event.target.id === "titleColor" || event.target.id === "sentColor") { // 사용자가 설정을 변경한 경우
            $(".modal-body > .alert").remove(); // 설정 팝업 내의 알림들을 제거합니다.
            $.ajax({
                type: "POST",
                url: "/saveconfig",
                data: $("#configForm").serialize(),
                error: function() {
                    $(".modal-body").prepend("<div class='alert alert-danger'>오류로 인해 설정이 반영되지 않았습니다.</div>"); // 오류를 받은 경우
                }
            });
        } else { // 그 외의 경우는 Query 생성기를 작동
            generateQuery()
        }
    });

    $(document).on('change', 'select', function() { // 값 종류를 변경한 경우
        generateQuery()
    });
});
