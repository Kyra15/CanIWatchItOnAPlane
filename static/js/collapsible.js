var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
	let content = coll[i].nextElementSibling;

    coll[i].addEventListener("click", function() {

		let arrow = this.querySelector(".arrow");

       	content = this.nextElementSibling;

        if ((content.style.maxHeight && content.style.maxHeight !== "0px")){
            content.style.maxHeight = "0px";
            this.style.borderBottomLeftRadius = "5px";
            this.style.borderBottomRightRadius = "5px";
            arrow.classList.add("fa-chevron-left")
            arrow.classList.remove("fa-chevron-down")
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            arrow.classList.remove("fa-chevron-left")
            this.style.borderBottomLeftRadius = "0px";
            this.style.borderBottomRightRadius = "0px";
            arrow.classList.add("fa-chevron-down")
        }
    });
}

var verdict = document.getElementsByClassName("verdict")[0];
console.log(verdict.childNodes[1].innerHTML)

if (verdict.childNodes[1].innerHTML.includes("Yes")) {
    verdict.style.backgroundColor = "#b4cf68"
    verdict.childNodes[1].innerHTML = "Probably Yes <i class='fa fa-check' aria-hidden='true'></i>"
} else if (verdict.childNodes[1].innerHTML.includes("No")) {
    verdict.style.backgroundColor = "#e38080ff"
    verdict.childNodes[1].innerHTML = "Probably Not <i class='fa fa-times' aria-hidden='true'></i>"
} else {
    verdict.style.backgroundColor = "#e8cb4c"
     verdict.childNodes[1].innerHTML = "Maybe <i class='fa fa-question' aria-hidden='true'></i>"
}