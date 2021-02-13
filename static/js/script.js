function show(name, second_name) {
    var elem = document.getElementById(name);
    var second_elem = document.getElementById(second_name);
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
            if (elem.value == 1){
                second_elem.style.display = "none";
            }
            else{
                second_elem.style.display = "block";
            }
        }
        if (name == "details"){
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


/*function show_table(id, table_name, user_id, user_name){
    var elem = document.getElementsByName(table_name)[0];
    if (elem){
         if (elem.style.display == "none"){
            elem.id = id;
            elem.style.display = "block";
         }
         else{
            elem.style.display = "none";
            if (id == 1){
                var second_elem = document.getElementById("player1");
                second_elem.value = user_name;
                var third_elem = document.getElementById("id_player1");
                third_elem.value = user_id;
            }
            elem.id = 0;

         }
    }
}*/
