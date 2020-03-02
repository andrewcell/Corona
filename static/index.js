function generateOptions() {
    const values = [
        ["All Fields", "전체(질환/성분)"],
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

function startsWith(str, word) {
    return str.lastIndexOf(word, 0) === 0;
}

function generateQuery() {
    const queryField = $("#query");

    var query = "";

    queryField.val("");
    const arr = $("form#fields").serializeArray();
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
function abstractPreprocessor(abstractObject, sentenceColor, keywordColor) {
        var HTML = "";
        $.each(abstractObject, function (index, sentence) {
            var code = "";
            if(typeof(sentence) === "object") {
                code += "<div style='color: " + sentenceColor + "'>";
                $.each(sentence, function (index, seperatedSentences) {
                    if(typeof(seperatedSentences) === "object") {
                        code += "<div style='color: " + keywordColor + "'>" + seperatedSentences.matched + "</div>"
                    } else {
                        code += seperatedSentences;
                    }
                });
                code += " </div>";
            } else {
                code += sentence + " ";
            }
            HTML += code;
        });
        return HTML;
}

function setDisable(object) {
    object.val("Searching...");
    object.prop('disabled', true);
}

function setEnable(object) {
    object.val("Search");
    object.prop('disabled', false);
}

function checkMessage(comment) {
    if (comment === undefined) {
        return false;
    } else {
        return "<div class=\"container-fluid\">" +
                    "                    <div class=\"alert alert-success\" role=\"alert\">" + comment + "</div>" +
                    "                </div>"
    }
}

function returnJournal(journalissue) {
    try {
        if (journalissue === undefined) {
            return "<td></td>";
        } else {
            if (typeof (journalissue.ISOName) !== undefined) {
                if (typeof(journalissue.PubDate_Year) === undefined) {
                    return "<td>" + journalissue.ISOName + "</td>"
                } else {
                    return "<td>" + journalissue.ISOName + ", " + journalissue.PubDate_Year + "</td>"
                }
            } else {
               return "<td></td>"
            }
        }
    } catch {
        return "<td></td>"
    }
}

$(document).ready(function() {
    $("#defaultOption").empty();
    $("#defaultOption").append(generateOptions());

    var count = 1;

    $("input#add").click(function() {
        count++;
        $("div [data=first]").append(
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
                    generateOptions() +
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

    $("form [data=first]").on("click", "#delete", function () {
        $(".form-group [data-index=" + $(this).attr("data-index") + "]").remove();
    });

    $("#search").click(function() {
        setDisable($(this)); // 검색 버튼 비활성화
        $(".alert").remove(); // 알림 제거
        $("table").remove(); // 기존 테이블 제거
        $.ajax({
            type: "POST",
            url: "/",
            data: $("form#queryForm").serialize(),
            error: function() {
                $(".container-fluid").prepend("<div class='alert alert-danger'>오류로 인해 검색이 되지 않았습니다.</div>");
                setEnable($("#search"));
            },
            success: function(data) {
                $(".container-fluid").append("<form action=\"/open\", method=\"post\">" +
                                checkMessage(data.comment) +
                    "           <table class=\"table\">" +
                    "               <thead>" +
                    "                   <tr>" +
                    "                       <th scope=\"col\">#</th>" +
                    "                       <th scope=\"col\">Include</th>" +
                    "                       <th scope=\"col\">Journal</th>" +
                    "                       <th scope=\"col\">Title</th>" +
                    "                       <th scope=\"col\">Abstract</th>" +
                    "                   </tr>" +
                    "                </thead>" +
                    "                <tbody>"
                );
                $.each(data.data, function (index, article) {
                    $("tbody").append("<tr>" +
                                        "<td>" + (index+1) + "</td>" + // index가 0부터 시작함.
                                        "<th scope='row'><input type='checkbox' name='selected' value=" + index + " checked></th>" +
                                         returnJournal(article.journalissue) +
                                        "<td style='width: 12%'>" + article.title + "</td>" +
                                        "<td>" + abstractPreprocessor(article.abstract, data.color.sentence, data.color.keyword) +"</td>" +
                                      "</tr>")

                });
                $("table").append("</tbody></table><button class=\"btn btn-success\">Submit</button>")
                setEnable($("#search"));
            }
        });
    });

    $("#settings").click(function() {
        $.get("/getconfig", function (data) {
            $("#resultLimit").val(data.result);
            $("#titleColor").val(data.keyword);
            $("#sentColor").val(data.sentence);
            $("#configModal").modal('toggle');
        });
    });


    $(document).on('change', 'input', function(event) {
        if(event.target.id === "query") {
            return;
        }

        if(event.target.id === "resultLimit" || event.target.id === "titleColor" || event.target.id === "sentColor") {
            $(".modal-body > .alert").remove();
            $.ajax({
                type: "POST",
                url: "/saveconfig",
                data: $("#configForm").serialize(),
                error: function() {
                    $(".modal-body").prepend("<div class='alert alert-danger'>오류로 인해 설정이 반영되지 않았습니다.</div>");
                }
            });
        } else {
            generateQuery()
        }
    });

    $(document).on('change', 'select', function() {
        generateQuery()
    });
});
