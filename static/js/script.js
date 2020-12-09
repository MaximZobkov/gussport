
function check(){
    var url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address";
    var token = "2ec81e520102ba1f8e3bc0d9fc1b74e656bc1e6a";
    var query = document.getElementById("city").text;

    var options = {
        method: "POST",
        mode: "cors",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Token " + token
        },
        document.getElementById("city").textContent = JSON.stringify({query: query})["suggestions"]["city"];
        body: JSON.stringify({query: query})
    }

    fetch(url, options)
    .then(response => response.text())
    .then(result => console.log(result))
    .catch(error => console.log("error", error));
}