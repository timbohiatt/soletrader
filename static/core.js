function gen_NewRowCell(row, value, cellIndex, cellprefix, cellpostfix, delta, CDIndicator, className) {

	//Build Cell ID from Prefix and Postfix.
	var cellID = (cellprefix+cellpostfix)
	//Check if the Cell is already existing
	var existing = !!document.getElementById(cellID);
	
	if (existing == true) {
		//Cell Already Exsits:
		if (delta == true){
			var cell = document.getElementById(cellID)
			cell.innerHTML = value
			animateCellValueChange(cell, CDIndicator)
		}
	}
	else{

		//Cell Doesn't Exist:
		//Generate New Cell in the Row.

		var cell  = row.insertCell(cellIndex);
		//Set Cell ID to the cellPrefix + cellPostfix
	    cell.id = cellID
	    cell.className = className;
	    // Append a value to the cell contents.
		var cellNode  = document.createTextNode(value);
		cell.appendChild(cellNode);
	}
}


//Animates the Cell Based on CD Indication. Up or Down.
function animateCellValueChange(cell, CDIndicator){
		if (CDIndicator == "U"){
			cell.style.animation = "pulse_up 8s steps(50), 1";
		}
		else if (CDIndicator == "D"){
			cell.style.animation = "pulse_down 8s steps(50), 1";	
		}
		else{
			cell.style.animation = "pulse_neutral 8s steps(50), 1";
		}
}

//Determin if the Cell Value is an Increase or a Decrease from the previous Number
function att_profit_numPosNeg(cell, value){
		if (value > 0.00){
			animateCellValueChange(cell, "U")
		}
		else if (value == 0.0){
			animateCellValueChange(cell, "N")
		}
		else{
			animateCellValueChange(cell, "D")
		}
}