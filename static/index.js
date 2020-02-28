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
        $("form#queryForm").submit();
    });

    $("#settings").click(function() {
        $("#configModal").modal('toggle');
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
