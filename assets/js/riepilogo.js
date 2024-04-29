// Dichiarare le variabili globali per salvare le informazioni desiderate
let globalPrice;
let globalQuantity;
let globalImage;
let globalName;
let globalID;
let globalNote;

// Variabile per salvare la somma di tutti i valori in globalPrice
let totalPriceSum = 0;
// Variabile per salvare i totale di tutti i valori in globalPrice
let grandTotal = [];

// Funzione per generare HTML dinamico basato sulle variabili globali
function generateDynamicHTML() {
  // Creare un array di dettagli dell'oggetto basato sulle variabili globali
  const objectDetailsArray = [
    {
      img: globalImage,
      name: globalName,
      quantity: globalQuantity,
      price: globalPrice,
      ID: "riepilogo_" + globalID,
      note: globalNote,
    },
    // Puoi aggiungere altri oggetti all'array se necessario
  ];

  // Dichiarare la variabile locale per la lista dei totali
  let totalPriceList = [];

  // Selezionare il container in cui si desidera aggiungere l'HTML (sostituire 'container-id' con il tuo effettivo ID del container)
  const container = document.getElementById("container-riepilogo");

  // Loop attraverso l'array di dettagli dell'oggetto
  objectDetailsArray.forEach((objectDetails, index) => {
    // Aggiungere il prezzo corrente alla somma totale
    totalPriceSum += parseFloat(objectDetails.price);

    // Creare un nuovo div per ogni oggetto
    const objectDiv = document.createElement("div");
    // Impostare l'ID univoco
    objectDiv.id = objectDetails.ID;
    objectDiv.className = "flex items-center mb-4";

    // Verifica se objectDetails.note è maggiore di 0 prima di aggiungere l'elemento <i>
    const noteHtml =
      objectDetails.note && objectDetails.note.trim().length > 0
        ? `<i class="text-sm text-default-600 font-bold text-primary">- ${objectDetails.note}</i>`
        : "";

    objectDiv.innerHTML = `
      <!-- <img src="${objectDetails.img}" class="h-20 w-20 me-2"> -->
      <div>
        <h4 class="text-sm text-default-600 mb-2 font-bold">${objectDetails.name}</h4>
        ${noteHtml}
        <h4 class="text-sm text-default-400 font-bold">${objectDetails.quantity} x <span class="text-primary font-semibold">€${objectDetails.price}</span>
        <button style="float: right;" class="font-bold text-default-950">X</button></h4>
      </div>
    `;

    // Aggiungere il listener di evento al pulsante "X"
    const deleteButton = objectDiv.querySelector("button");
    deleteButton.addEventListener("click", () => {
      // Chiamare la funzione di eliminazione passando l'indice corrente
      deleteObject(index);
    });

    // Aggiungere il nuovo div al container senza cancellare quello già esistente
    container.appendChild(objectDiv);
  });

  // Aggiungere il valore corrente alla somma totale
  grandTotal += totalPriceSum;

  // Aggiungere il valore corrente alla lista dei totali
  totalPriceList.push(totalPriceSum);

  // Ora puoi utilizzare la variabile totalPriceSum per ottenere la somma totale dei prezzi
  console.log("Somma totale dei prezzi di questa chiamata:", totalPriceSum);

  // Calcolare la somma totale di tutti i valori nella lista
  grandTotal = totalPriceList.reduce(
    (acc, currentTotal) => acc + currentTotal,
    0
  );

  // Selezionare l'elemento <p> con l'ID "Totale"
  const totaleElement = document.getElementById("Totale");

  // Aggiornare il contenuto dell'elemento con la somma totale
  totaleElement.textContent = `€ ${grandTotal.toFixed(2)}`;

  console.log("Totale riepilog:", grandTotal);

  // Aggiungere la funzione di eliminazione
  function deleteObject(index) {
    // Selezionare il div padre da rimuovere
    const container = document.getElementById("container-riepilogo");
    const divToRemove = document.getElementById(objectDetailsArray[index].ID);

    // Log per il debugging
    console.log("Elemento da rimuovere:", divToRemove);

    // Verificare che l'elemento da rimuovere sia un figlio diretto del contenitore
    if (divToRemove && divToRemove.parentNode === container) {
      // Rimuovere l'elemento corrispondente dall'array di dettagli dell'oggetto
      const removedObjectPrice = parseFloat(objectDetailsArray[index].price);
      objectDetailsArray.splice(index, 1);

      // Rimuovere il div dal DOM
      container.removeChild(divToRemove);

      // Sottrarre il prezzo dell'oggetto eliminato dalla somma totale
      grandTotal -= removedObjectPrice;

      // Aggiornare il contenuto dell'elemento con la nuova somma totale
      totaleElement.textContent = `€ ${grandTotal.toFixed(2)}`;

      console.log("Totale aggiornato dopo l'eliminazione:", grandTotal);

      // Aggiornare totalPriceSum sottraendo il prezzo dell'oggetto eliminato
      totalPriceSum -= removedObjectPrice;

      console.log("Totale riepilogo aggiornato:", totalPriceSum);
    } else {
      // Log se l'elemento non è stato trovato o non è un figlio diretto del contenitore
      console.error(
        "Errore: Elemento non trovato o non è un figlio diretto del contenitore."
      );
    }
  }
}
