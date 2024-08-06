function toggleMenu() {
    var menuList = document.getElementById("menuList");
    menuList.style.display = (menuList.style.display === "block") ? "none" : "block";
}


$(function() {
    $('[data-toggle="tooltip"]').tooltip()
});

$(document).ready(function() {
    $('#copyButton').click(function() {
        var copyText = document.querySelector(".form-control");
        copyText.select();
        document.execCommand("copy");
        alert("Copied to clipboard!");
    });
});