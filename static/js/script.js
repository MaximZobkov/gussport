function show(name, second_name) {
    console.log(1);
    var elem = document.getElementById(name);
    var second_elem = document.getElementById(second_name);
    if (elem) {
        if (name == "type_team") {
            if (elem.value == "Индивидуальное") {
                second_elem.style.display = "none";
            } else {
                second_elem.style.display = "block";
            }
        }
        if (name == "pay") {
            if (elem.value == 2) {
                second_elem.style.display = "none";
            } else {
                second_elem.style.display = "block";
            }
        }
        if (name == "details") {
            if (elem.style.display == "block") {
                elem.style.display = "none";
                second_elem.innerHTML = "Подробнее...";
            } else {
                elem.style.display = "block";
                second_elem.innerHTML = "Свернуть";
            }
        }
    }
}
