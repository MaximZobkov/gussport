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