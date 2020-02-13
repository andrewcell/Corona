function generateOptions() {
    const values = [
        "Affiliation",
        "All Fields",
        "Author",
        "Author - Corporate",
        "Author - First",
        "Author - Full",
        "Author - Identifier",
        "Author - Last",
        "Book",
        "Conflict of Interest Statements",
        "Date - Completion",
        "Date - Create",
        "Date - Entrez",
        "Date - MeSH",
        "Date - Modification",
        "Date - Publication",
        "EC/RN Number",
        "Editor",
        "Filter",
        "Grant Number",
        "ISBN",
        "Investigator",
        "Investigator - Full",
        "Issue",
        "Journal",
        "Language",
        "Location ID",
        "MeSH Major Topic",
        "MeSH Subheading",
        "MeSH Terms",
        "Other Term",
        "Pagination",
        "Pharmacological Action",
        "Publication Type",
        "Publisher",
        "Secondary Source ID",
        "Subject - Personal Name",
        "Supplementary Concept",
        "Text Word",
        "Title",
        "Title/Abstract",
        "Transliterated Title",
        "Volume"
    ];
    var tag = "";
    values.forEach(function (value) {
        tag = tag + "<option value='" + value + "'>" + value + "</option>";
    });
    return tag;
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
            if (arr[i].name.startsWith("operator")) {
                operator = arr[i].value.toUpperCase();
            }
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
            '<input type="text" name="value" index="' + count + '" class="form-control">' +
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
    })
    $(document).on('change', 'input', function(event) {
        if(event.target.id === "query") {
            return;
        }
        generateQuery()
    });

    $(document).on('change', 'select', function() {
        generateQuery()
    });
});