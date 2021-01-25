function show(name, second_name) {
    alert(1);
    var elem = document.getElementById(name);
    var second_elem = document.getElementById(second_name);
    alert(elem.value);
    if (elem){
        if (name == "type_team"){
            if (elem.value == "Индивидуальное"){
                second_elem.style.display = "none";
            }
            else{
                second_elem.style.display = "block";
            }
        }
        if (name == "pay"){
            alert(elem.value);
            if (elem.value == 1){
                second_elem.style.display = "none";
            }
            else{
                second_elem.style.display = "block";
            }
        }
        if (name == "show_detail"){
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
}
