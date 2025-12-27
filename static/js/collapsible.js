var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
	let content = coll[i].nextElementSibling;

    coll[i].addEventListener("click", function() {

		let arrow = this.querySelector(".arrow");

       	content = this.nextElementSibling;
        // content.classList.toggle("hidden");

        if ((content.style.maxHeight && content.style.maxHeight !== "0px")){
          content.style.maxHeight = "0px";
		  arrow.classList.add("fa-chevron-left")
		  arrow.classList.remove("fa-chevron-down")
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
		  arrow.classList.remove("fa-chevron-left")
		  arrow.classList.add("fa-chevron-down")
        }
    });
}