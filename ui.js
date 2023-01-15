function addRow() {
    // Get a reference to the table
    let tableRef = document.getElementById("album");
  
    // Insert a row at the end of the table
    let newRow = tableRef.insertRow(-1);
  
    // Insert a cell in the row at index 0
    let newCell = newRow.insertCell(0);
  
    // Append a text node to the cell
    let newText = document.createTextNode('New bottom row');
    newCell.appendChild(newText);
  }