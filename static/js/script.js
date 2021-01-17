document.addEventListener("DOMContentLoaded", function (event) {
    window.onresize = function () {
        resize_info();
    };
});

function resize_info() {
    if (document.documentElement.clientHeight > document.documentElement.clientWidth){
        document.getElementById('newsimages').className = "card-img-top";
    }
    else{
        document.getElementById('newsimages').className = "card-img-news";
    }
}

function show(name, second_name) {
    var elem = document.getElementById(name);
    var second_elem = document.getElementById(second_name);
    if (elem){
        console.log(second_elem);
        if (elem.style.display == "block"){
            elem.style.display = "none";
            second_elem.innerHTML="Подробнее...";
        }
        else{
            elem.style.display = "block";
            second_elem.innerHTML="Свернуть";
        }
    }
}