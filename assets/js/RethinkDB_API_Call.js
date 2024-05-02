// Funzione principale che viene eseguita una volta che il DOM è pronto
document.addEventListener("DOMContentLoaded", function () {});
toastr.options = {
  timeOut: "1500",
};

// Modifica la funzione loadExternalJsonAndInitialize per utilizzare la chiamata API
async function loadExternalJsonAndInitialize(apiUrl) {
  try {
    const response = await fetch(apiUrl); // Esegui la chiamata API
    //console.log("Chiamata API riuscita:", response);
    const data = await response.json(); // Estrai i dati JSON dalla risposta
    //console.log(data);

    const response2 = await fetch(
      "http://" + self.location.host + "/api/requestOrderNumber"
    ); // Esegui la chiamata API
    console.log("Chiamata API riuscita:", response2);
    responseObject = await response2.json(); // Estrai i dati JSON dalla risposta
    orderNumber = responseObject.orderId;
    console.log(orderNumber);

    // Inizializza l'applicazione con il JSON caricato
    initializeApp(data);

    // Simula un click sulla prima categoria per avviare il caricamento del menu promozionale
    const primaCategoriaCheckbox = document.querySelector(
      '#category-list input[type="checkbox"]'
    );
    primaCategoriaCheckbox.click();
  } catch (error) {
    console.error("Errore nel caricamento dei dati dall'API:", error);
  }
}

// Variabile per salvare i totale di tutti i valori in globalPrice
let grandTotal = 0;
// variabile globale per i dati dell'ordine da portare in JSON
let orderData = [];
// variabile per il numero dell'ordine
let orderNumber = -1;

//clear html containers of cart
function clearContainers() {
  const containerRiepilogo = document.getElementById("container-riepilogo");
  const containerTotale = document.getElementById("Totale");

  if (containerRiepilogo && containerTotale) {
    // Rimuovere tutto il contenuto HTML dal div "container-riepilogo"
    containerRiepilogo.innerHTML = "";

    // Rimuovere tutto il contenuto HTML dal div "Totale"
    containerTotale.innerHTML = "";

    console.log("Contenuto dei container eliminato con successo.");
  } else {
    console.error("Errore: Impossibile trovare uno o entrambi i container.");
  }
}

// Funzione per inizializzare l'applicazione con il JSON (Lista prodotti) fornito
function initializeApp(data) {
  // Mappa delle categorie ai rispettivi array di menu
  const json = JSON.parse(data);
  console.log(json);
  //key = category, item= list of products
  const categorieMenuMap = {
    pizza: json["pizza"] || [],
    panini_singoli: json["panini"] || [],
    menu_birra: json["menu birra"] || [],
    cucina: json["cucina"] || [],
    bevande: json["bevande"] || [],
    menu_bibita: json["menu bibita"] || [],
  };

  // Funzione per generare HTML dinamico basato sulle >variabili globali< (NEL RIEPILOGO a lato)
  function generateDynamicHTML(itemProperties) {
    // Creare un array di dettagli dell'oggetto basato sulle variabili globali
    const objectDetails = itemProperties;
    // Selezionare il container in cui si desidera aggiungere l'HTML (sostituire 'container-id' con il tuo effettivo ID del container)
    const container = document.getElementById("container-riepilogo");
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
      deleteObject();
    });

    // Aggiungere il nuovo div al container senza cancellare quello già esistente
    container.appendChild(objectDiv);

    // Funzione di eliminazione voce
    function deleteObject() {
      // Selezionare il div padre da rimuovere
      const container = document.getElementById("container-riepilogo");
      const divToRemove = document.getElementById(objectDetails.ID);

      // Log per il debugging
      console.log("Elemento da rimuovere:", divToRemove);

      // Verificare che l'elemento da rimuovere sia un figlio diretto del contenitore
      if (divToRemove && divToRemove.parentNode === container) {
        // Rimuovere l'elemento corrispondente dall'array di dettagli dell'oggetto
        orderData = orderData.filter((item) => item.ID != objectDetails.ID);
        grandTotal = calculateTotalOrderValue(orderData);
        // Rimuovere il div dal DOM
        container.removeChild(divToRemove);

        // Aggiornare il contenuto dell'elemento con la nuova somma totale
        totaleElement.textContent = `€ ${grandTotal.toFixed(2)}`;

        console.log("Totale aggiornato dopo l'eliminazione:", grandTotal);
        console.log("ID da eliminare:", objectDetails.ID);

        // Ottieni il riferimento al bottone "check-out"
        var checkoutButton = document.getElementById("check-out");
        if (grandTotal == 0) {
          // Toggle della classe opacity-50 sul div del bottone "check-out"
          checkoutButton.classList.add("opacity-50");
        }
      } else {
        // Log se l'elemento non è stato trovato o non è un figlio diretto del contenitore
        console.error(
          "Errore: Elemento non trovato o non è un figlio diretto del contenitore."
        );
      }
    }

    // Creare un oggetto di dettagli dell'ordine basato sulle variabili globali
    const orderDetailsObject = {
      name: itemProperties.name,
      quantity: itemProperties.quantity,
      price: itemProperties.price,
      notes: "",
      ID: itemProperties.ID,
      itemId: itemProperties.productId,
    };

    if (itemProperties.note) {
      orderDetailsObject["notes"] = itemProperties.note;
    }

    // Aggiungere i dati correnti alla variabile globale orderData
    orderData.push(orderDetailsObject);

    // Ora puoi utilizzare orderDataJson per ottenere la rappresentazione JSON dei dati dell'ordine
    console.log("Ordine:", orderDetailsObject);
    // Convertire l'oggetto in una stringa JSON e assegnarla a orderDataJson
    const orderDataJson = JSON.stringify(orderData);

    // Ora puoi utilizzare orderDataJson per ottenere la rappresentazione JSON dei dati dell'ordine
    console.log("Ordine JSON:", orderDataJson);
    // Ora puoi utilizzare orderDataJson per ottenere la rappresentazione JSON dei dati dell'ordine
    console.log("Ordine:", orderData);

    grandTotal = calculateTotalOrderValue(orderData);
    console.log("Totale riepilogo:", grandTotal);

    // Selezionare l'elemento <p> con l'ID "Totale"
    const totaleElement = document.getElementById("Totale");

    // Aggiornare il contenuto dell'elemento con la somma totale
    totaleElement.textContent = `€ ${grandTotal.toFixed(2)}`;
    // Ottieni il riferimento al bottone "check-out"
    var checkoutButton = document.getElementById("check-out");
    if (grandTotal > 0) {
      // Toggle della classe opacity-50 sul div del bottone "check-out"
      checkoutButton.classList.remove("opacity-50");
    }
  }

  // Aggiungi l'evento di click all'elemento con ID "check-out"
  const checkoutButton = document.getElementById("check-out");
  if (checkoutButton) {
    checkoutButton.addEventListener("click", function () {
      if (grandTotal !== 0) {
        //make screen unclickable
        const MenuContainer1 = (document.getElementById(
          "container-menu"
        ).style.pointerEvents = "none");
        const MenuContainer2 = (document.getElementById(
          "filter_Offcanvas"
        ).style.pointerEvents = "none");
        const MenuContainer3 = (document.getElementById(
          "right-panel"
        ).style.pointerEvents = "none");
        // Chiamare la funzione per pulire il carrello
        clearContainers();
        // Toggle della classe opacity-50 sul div del bottone "check-out"
        checkoutButton.classList.add("opacity-50");

        // Ottenere il JSON risultante dalla variabile globale orderData
        const orderDataJson = JSON.stringify(orderData);

        // Chiamare la funzione transformAndSaveOrderData con il JSON risultante
        const transformedOrderData = transformAndSaveOrderData(orderDataJson);

        // Chiamare la funzione showPopupOrderData con i dati trasformati
        showPopupOrderData(transformedOrderData, grandTotal);
      } else {
        // Alert o messaggio che informa l'utente che non può effettuare il check-out
        toastr.error("Il carrello è vuoto!", "Errore");
      }
    });
  }

  // Funzione per inviare i dati dell'ordine al database
  async function inviaDatiOrdine(cleanedOrderData) {
    // Crea un oggetto con i dati dell'ordine da mandare al server
    const datiOrdine = {
      customerType: GuestTypeSelectedInput,
      paymentType: paymentType,
      orderId: orderNumber,
      totalValue: grandTotal,
      items: cleanedOrderData,
    };

    console.log("Dati dell'ordine:", datiOrdine);

    let response = await fetch("http://" + self.location.host + "/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(datiOrdine),
    });
    let data = await response.json();
    if (data.status == "success") {
      // Svuotare le variabile dopo l'invio dell'ordine
      closePopup();
      clearDataState();
      location.reload(); //reload the page after submitting the order to the server
    } else {
      toastr.error("Errore nell'invio dell'ordine. Riprovare:");
    }
  }

  // Aggiungi un listener per l'evento beforeunload per assicurarti che i dati vengano salvati prima di lasciare la pagina
  window.addEventListener("beforeunload", () => {});

  // Funzione per aggiungere numero ordine a orderData (useless at the moment)
  function transformAndSaveOrderData(newOrderData) {
    // Convertire la stringa JSON in un array di oggetti
    const orderArray = JSON.parse(newOrderData);
    const transformedData = [];

    // Riempire l'array dell'oggetto contenitore
    orderArray.forEach((orderDetails) => {
      transformedData.push(orderDetails);
    });

    // Convertire l'oggetto in una stringa JSON
    const transformedDataJson = JSON.stringify(transformedData);
    // Ora puoi utilizzare transformedDataJson per ottenere la rappresentazione JSON dei dati trasformati
    console.log("Dati trasformati JSON:", transformedDataJson);
    // Restituire la stringa JSON risultante
    return transformedDataJson;
  }

  function cleanOrderData(data) {
    data.forEach((item) => {
      delete item["name"]; //remove useless data used only for visualization
      delete item["price"];
      delete item["ID"];
    });
    return data;
  }

  // Funzione per creare e mostrare il pop-up con i dati trasformati
  function showPopupOrderData(transformedDataJson, grandTotal) {
    // Converti la stringa JSON in un oggetto JavaScript
    const orderItems = JSON.parse(transformedDataJson);
    // Ottieni il contenitore del pop-up
    const popupContainer = document.getElementById("popup-container");
    // Creare HTML dinamico con i dati mappati
    let htmlContent = `<h4 class="text-xl text-default-700 font-bold mb-5 text-center">Ordine Nr. ${orderNumber}</h4>
    <div style="overflow:auto;">`;
    let noteHtml = `
    </div>
    <div class="mt-5 mx-5">
      <div id="grandTotal-container" class="flex flex-shrink-0 gap-3 items-center justify-center mb-5 text-xl">
        <p class="text-default-700 font-bold">Totale: </p>
        <p class="text-default-700 font-medium">${grandTotal} €</p>
      </div>

      `;
    if ((paymentType = "cash" && GuestTypeSelectedInput === "Client")) {
      noteHtml += `
      <div id="change-container" class="flex gap-2 items-center justify-between mb-5 hs-collapse open w-full overflow-hidden transition-all duration-300">
        <label for="num1">Contante:</label>
        <input type="text" id="num1" class="border dark:bg-default-50 duration-500 font-medium items-center px-2.5 py-1.5 rounded-full shadow-sm text-center text-sm w-16" />
        <button class="bg-primary border border-primary duration-500 font-medium hover:bg-primary-500 items-center px-6 py-1.5 relative rounded-full shadow-sm text-center text-sm text-white" id="resto-btn">RESTO</button>
        <div id="risultato" class="font-bold text-center flex-grow text-primary"></div>
      </div>
    </div>
    `;
    }
    orderItems.forEach((item) => {
      htmlContent += `

      <div class="mx-5">
  <div style="
  display: grid;
  grid-template-columns: auto auto;
  column-gap: 40px;
  justify-content: start;
  ">
    <h4 class="mt-0.5 mb-0.5 text-default-600 text-lg select-none">Piatto:</h4>
    <span class="ps-3 inline-flex items-center text-default-600 text-lg select-none">${
      item.name
    }</span>
    
    <h4 class="mt-0.5 mb-0.5 text-default-600 text-lg select-none">Quantità:</h4>
    <span class="ps-3 inline-flex items-center text-default-600 text-lg select-none">${
      item.quantity
    }</span>
    
    <h4 class="mt-0.5 mb-0.5 text-default-600 text-lg select-none">Prezzo:</h4>
    <span class="ps-3 inline-flex items-center text-default-600 text-lg select-none">${
      item.price
    } €</span>
    
    <h4 class="mt-0.5 mb-0.5 text-default-600 text-lg select-none">Note:</h4>
    <span class="ps-3 inline-flex items-center text-default-600 text-lg select-none text-primary">${
      item.notes ?? ""
    }</span>
  </div>
  <hr class="mb-3 mt-3">
</div>


    `;
    });
    htmlContent += noteHtml;
    if (GuestTypeSelectedInput === "Client") {
      htmlContent += `
    <div id="checkbox-paymant" class="flex justify-around mb-5 mx-5">
                      <div>
                        <input class="hs-collapse-toggle open form-checkbox rounded-full text-primary border-default-400 bg-transparent w-5 h-5 focus:ring-0 focus:ring-transparent ring-offset-0 cursor-pointer" id="cash" name="all" type="checkbox" onclick="paymentCheckboxMutex('cash', 'pos')">
                        <label class="hs-collapse-toggle open transition-all ps-3 inline-flex items-center text-default-600 text-sm select-none" for="cash">Contanti</label>
                      </div>
                      <div>
                        <input class="hs-collapse-toggle open form-checkbox rounded-full text-primary border-default-400 bg-transparent w-5 h-5 focus:ring-0 focus:ring-transparent ring-offset-0 cursor-pointer" id="pos" name="all" type="checkbox" onclick="paymentCheckboxMutex('pos', 'cash')">
                        <label class="hs-collapse-toggle open transition-all ps-3 inline-flex items-center text-default-600 text-sm select-none" for="pos">POS</label>
                      </div>
                </div>
                `;
    }
    htmlContent += `
    <div id="button-order-container" class="flex gap-12 justify-around  mx-5">
    <a id="send-order" class="bg-primary border border-primary duration-500 font-medium hover:bg-primary-500 inline-flex items-center justify-center px-6 py-3 relative rounded-full shadow-sm text-center text-sm text-white transition-all w-full" href="#">PREPARAZIONE</a>
    <button id="btn-confirm-order" class="bg-primary border border-primary duration-500 font-medium hover:bg-primary-500 inline-flex items-center justify-center px-6 py-3 relative rounded-full shadow-sm text-center text-sm text-white transition-all w-full">Stampa</button>
    </div>
    `;
    // Assegna l'HTML al contenitore del pop-up
    popupContainer.innerHTML = `<span class="font-semibold text-primary text-xl" id="close-button" ><button><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="x-circle" class="lucide lucide-x-circle w-5 h-5 text-primary text-default-400"><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg></button></span>${htmlContent}`;

    // Mostra il pop-up
    popupContainer.style.display = "flex";
    if (GuestTypeSelectedInput === "Client") {
      document.getElementById("cash").checked = true;
      paymentType = "cash";
    } else {
      paymentType = "free";
    }

    console.log(paymentType);

    //Calcolo resto
    function calcolaSottrazione() {
      var num1 = parseFloat(
        document.getElementById("num1").value.replace(",", ".")
      );

      var risultatoElement = document.getElementById("risultato");

      if (isNaN(num1) || isNaN(grandTotal)) {
        alert("Inserisci un numero valido.");
        return;
      }

      if (num1 < grandTotal) {
        alert(
          "C'è un errore sul pagamento. Il numero inserito è inferiore al totale."
        );
        return;
      }

      var risultato = Math.abs(grandTotal - num1);

      risultatoElement.textContent = "Resto: " + risultato.toFixed(2) + " €";
    }

    function handleKeyPress(event) {
      if (event.keyCode === 13) {
        calcolaSottrazione();
      }
    }

    if (GuestTypeSelectedInput === "Client") {
      const restoButton = document.getElementById("resto-btn");
      restoButton.addEventListener("click", function () {
        calcolaSottrazione();
      });
      const restoInputField = document.getElementById("num1");
      restoInputField.addEventListener("keydown", function (event) {
        handleKeyPress(event);
      });
    }

    // Aggiungi il codice per mostrare l'overlay
    const overlay = document.getElementById("overlay");
    overlay.style.display = "block";

    const sendOrderButton = popupContainer.querySelector("#send-order");
    sendOrderButton.addEventListener("click", function (event) {
      // Previeni il comportamento di default del link
      event.preventDefault();
      // Chiama la funzione per inviare i dati dell'ordine al database
      let cleanedData = cleanOrderData(orderData);
      inviaDatiOrdine(cleanedData);
    });
    const closePopupButton = popupContainer.querySelector("#close-button");
    closePopupButton.addEventListener("click", function () {
      // Svuotare le variabile dopo l'invio dell'ordine

      closePopup();
      clearDataState();
    });
    const printButton = popupContainer.querySelector("#btn-confirm-order");
    printButton.addEventListener("click", function () {
      printOrderData(transformedDataJson, grandTotal, orderNumber);
    });
  }

  // Funzione per chiudere il pop-up
  function closePopup() {
    const popupContainer = document.getElementById("popup-container");
    const overlay = document.getElementById("overlay");
    popupContainer.style.display = "none";
    //make clickable everything again
    const MenuContainer1 = (document.getElementById(
      "container-menu"
    ).style.pointerEvents = "");
    const MenuContainer2 = (document.getElementById(
      "filter_Offcanvas"
    ).style.pointerEvents = "");
    const MenuContainer3 = (document.getElementById(
      "right-panel"
    ).style.pointerEvents = "");
    // Nascondi il popup e l'overlay
    popupContainer.style.display = "none";
    overlay.style.display = "none";
  }

  function printOrderData(transformedDataJson, grandTotal, idOrdineCreato) {
    // JSON da parsare
    const jsonData = transformedDataJson;
    // Converti la stringa JSON in un oggetto JavaScript
    const orderItems = JSON.parse(jsonData);
    console.log(transformedDataJson);
    // Ottieni il totale
    const GragrandTotal = grandTotal;

    // Creare HTML dinamico con i dati mappati
    let htmlContent = `<div id="print-content">`;
    htmlContent += `<h4 class="text-base text-default-700 font-bold">Ordine N.${idOrdineCreato}</h4>`;
    orderItems.forEach((item) => {
      htmlContent += `
         <div>
            <span>${item.quantity}x</span>
            <span>${item.name}</span><br>
            <span style="margin-left:20px">      ${item.price} €</span>
         </div>
     `;
    });
    htmlContent += `
     <div>
         <h4 class="mt-1.5 mb-1.5 text-default-600 text-sm text-primary">TOTALE: <span class="ps-3 inline-flex items-center text-default-600 text-lg select-none text-primary">${GragrandTotal} €</span></h4>
     </div>
 `;
    htmlContent += `</div>`;

    // Chiamata alla funzione per inviare i dati al server
    //sendDataToServer();
    // Creazione di un elemento div temporaneo nel DOM
    const printContainer = document.createElement("div");
    printContainer.innerHTML = htmlContent;
    document.body.appendChild(printContainer);

    // Chiamata alla funzione per inviare l'HTML  Comanda al server
    //sendHTMLToServer(htmlContent);

    // Stampare l'elemento HTML utilizzando Print.js con la stampante specificata
    printJS({
      printable: "print-content", // Utilizza l'ID del div come riferimento
      type: "html",
      showModal: false, // Impedisci l'apertura della finestra di dialogo di stampa del browser
      printer: "POS-58", // Specifica il nome della stampante di rete desiderata
    });

    // Rimuovere l'elemento div temporaneo dal DOM dopo la stampa
    document.body.removeChild(printContainer);
  }

  function clearDataState() {
    orderData = [];
    paymentType = "";
    grandTotal = 0;
  }
  // Funzione per gestire il click sulla categoria
  function categoriaClick(event) {
    // Deseleziona la categoria precedentemente selezionata
    const categorieSelezionate = document.querySelectorAll(
      '#category-list input[type="checkbox"]:checked'
    );
    categorieSelezionate.forEach((categoria) => {
      categoria.checked = false;
    });

    // Seleziona la categoria cliccata
    const checkbox = event.currentTarget.querySelector(
      'input[type="checkbox"]'
    );
    checkbox.checked = true;

    // Ottieni l'ID della categoria cliccata
    const categoryId = checkbox.id;

    // Esegui le azioni desiderate con l'ID della categoria
    console.log(`Hai cliccato sulla categoria con ID: ${categoryId}`);

    // Aggiorna il menu in base alla categoria selezionata
    updateMenu(categoryId);
  }

  // Funzione per aggiornare il menu in base alla categoria selezionata
  function updateMenu(categoryId) {
    // Seleziona il container del menu
    const containerMenu = document.getElementById("container-menu");

    // Seleziona l'array di menu corrispondente alla categoria
    const arrayMenu = categorieMenuMap[categoryId];

    // Dichiarare la variabile addCartButton fuori dal ciclo
    let addCartButton;

    // Controlla se l'array esiste e ha una proprietà 'length'
    if (Array.isArray(arrayMenu) && arrayMenu.length > 0) {
      // Pulisci il container del menu
      containerMenu.innerHTML = "";

      // Funzione per generare un ID univoco basato sul nome e sull'ID della categoria senza spazi
      function generateUniqueId(name, categoryId) {
        // Sostituisci gli spazi con l'underscore, convergi tutto in minuscolo e aggiungi un prefisso
        const cleanedName = name
          .replace(/\s/g, "_")
          .replace(",", "-")
          .toLowerCase();
        const cleanedCategoryId = categoryId.replace(/\s/g, "_").toLowerCase();
        return `${cleanedCategoryId}-${cleanedName}`;
      }

      // Ciclo sugli oggetti dell'array e generazione dinamica degli elementi del menu centrale
      for (let i = 0; i < arrayMenu.length; i++) {
        const oggetto = arrayMenu[i];

        // Creazione dell'elemento del menu con un ID univoco basato sul nome e l'ID della categoria
        const menuElement = document.createElement("div");
        const menuId = generateUniqueId(oggetto.name, categoryId); // Aggiunto categoryId come secondo parametro
        menuElement.id = menuId;
        menuElement.className =
          "xl:order-1 order-2 border border-default-200 rounded-lg p-4 overflow-hidden hover:border-primary hover:shadow-xl transition-all duration-300";

        menuElement.innerHTML = `
            
        <div class="relative rounded-lg overflow-hidden divide-y divide-default-200 group">
          <div class="mb-4 mx-auto">
            <img class="w-full h-full group-hover:scale-105 transition-all" src="${oggetto.img}" />
          </div>
  
          <div class="pt-2">
            <div id="obj-desc-container" style="flex-flow: column;" class="flex justify-between mb-4">
              <span class="text-default-800 text-xl font-semibold line-clamp-2 after:absolute after:inset-0">${oggetto.name}</span>
              <i class="text-m text-default-500">${oggetto.desc}</i>
              <div class="border border-default-200 inline-flex justify-between mt-2 p-1 relative rounded-full z-10 truncate overflow-auto">
              <input id="input_${menuId}" type="text" placeholder="Inserisci modifiche" class="bg-white border-none dark:bg-default-50 h-3 overflow-auto truncate w-full" />
              </div>
            </div>
  
            <div class="flex items-end justify-between mb-4">
              <h4 class="font-semibold text-xl text-default-900">€ ${oggetto.price}</h4>
              <div class="relative z-10 inline-flex justify-between border border-default-200 p-1 rounded-full">
                <button class="minus flex-shrink-0 bg-default-200 text-default-800 rounded-full h-6 w-6 text-sm inline-flex items-center justify-center" type="button">–</button>
                <input id="quantity_${menuId}" class="w-8 border-0 text-sm text-center text-default-800 focus:ring-0 p-0 bg-transparent" max="100" min="0" readonly="" type="text" value="1" />
                <button class="plus flex-shrink-0 bg-default-200 text-default-800 rounded-full h-6 w-6 text-sm inline-flex items-center justify-center" type="button">+</button>
              </div>

            </div>
  
            <a id="add-cart" class="relative z-10 w-full inline-flex items-center justify-center rounded-full border border-primary bg-primary px-6 py-3 text-center text-sm font-medium text-white shadow-sm transition-all duration-500 hover:bg-primary-500" href="cart.html">Aggiungi al carrello</a>
          </div>
        </div>
      
            `;

        // Aggiungi eventi di click ai pulsanti e all'elemento "add-cart"
        const minusButton = menuElement.querySelector(".minus");
        const plusButton = menuElement.querySelector(".plus");
        const addCartButton = menuElement.querySelector("#add-cart");
        const quantityInput = menuElement.querySelector(
          "input#quantity_" + menuId
        );

        minusButton.addEventListener("click", function () {
          // Verifica se la quantità è maggiore di 1 prima di ridurla
          if (parseInt(quantityInput.value, 10) > 1) {
            // Riduci la quantità, assicurandoti che non scenda al di sotto del minimo
            quantityInput.value = Math.max(
              parseInt(quantityInput.value, 10) - 1,
              0
            );
          }
        });

        plusButton.addEventListener("click", function () {
          // Aumenta la quantità, assicurandoti che non superi il massimo
          quantityInput.value = Math.min(
            parseInt(quantityInput.value, 10) + 1,
            100
          );
        });

        // Aggiungi l'event listener all'elemento "add-cart" solo se è stato trovato
        if (addCartButton) {
          addCartButton.addEventListener("click", function (event) {
            // Previeni il comportamento di default del link
            event.preventDefault();

            // Ottieni il riferimento al bottone "check-out"
            var checkoutButton = document.getElementById("check-out");

            // Toggle della classe opacity-50 sul div del bottone "check-out"
            checkoutButton.classList.add("opacity-50");

            // Seleziona l'elemento input per l'oggetto corrente
            const inputId = `input_${menuId}`;
            const noteInput = document.getElementById(inputId);

            // Verifica se la quantità è maggiore di 0 prima di procedere con l'aggiunta al carrello

            if (parseInt(quantityInput.value, 10) > 0) {
              let itemProperties = {
                price: oggetto.price,
                quantity: Math.max(parseInt(quantityInput.value, 10), 0),
                image: oggetto.img,
                name: oggetto.name,
                ID:
                  menuId +
                  Date.now().toString(36) +
                  Math.random().toString(36).substr(2), //true random id for <div>
                productId: oggetto.productId,
                note: "",
              };

              // Ottieni il valore dall'input solo se la lunghezza è maggiore di 0
              if (noteInput && noteInput.value.trim().length > 0) {
                itemProperties.note = noteInput.value.trim();
              }
              //reset input data after adding item to cart (notes and quantities) by updating menu to same category
              updateMenu(categoryId);
              // Chiama la funzione per generare l'HTML dinamico
              generateDynamicHTML(itemProperties);

              toastr.success(
                "<b>" +
                  itemProperties.name +
                  "</b> <br> aggiunto con successo al carrello!"
              );
            } else {
              console.log(
                "Impossibile aggiungere al riepilogo. La quantità è 0."
              );
              toastr.error("Impossibile aggiungere prodotto: la quantità è 0.");
              // Aggiungi qui il codice per visualizzare un toast con l'avviso
              // Ad esempio, usando una libreria di toast come Toastify o simile
            }
          });
        }

        // Aggiungi l'elemento del menu al container
        containerMenu.appendChild(menuElement);
      }
    }

    function editInput(menuId) {
      // Costruisci l'id dell'input
      const inputId = `input_${menuId}`;

      // Seleziona l'elemento input
      const inputElement = document.getElementById(inputId);

      // Verifica se l'elemento input esiste
      if (inputElement) {
        // Aggiungi un listener per il click sull'input
        inputElement.addEventListener("click", function () {
          console.log(`Input con id ${inputId} cliccato.`);

          // Salva il valore dell'input nella variabile globale
          globalNote = inputElement.value;
        });

        // Imposta il focus sull'input per attivare la modalità di modifica
        inputElement.focus();
      } else {
        console.error(`Elemento input con id ${inputId} non trovato.`);
      }
    }

    // Funzione per salvare le variabili globali
    function saveGlobalVariables() {
      // Puoi fare quello che vuoi con le variabili globali qui
      // Ad esempio, puoi inviarle a un'altra funzione o eseguire altre operazioni
      console.log("Global Price:", globalPrice);
      console.log("Global Quantity:", globalQuantity);
      console.log("Global Image:", globalImage);
      console.log("Global Name:", globalName);
      console.log("Global ID:", globalID);
      console.log("Global Note:", globalNote);
    }
  }

  function calculateTotalOrderValue(data) {
    let totalValue = 0;
    data.forEach((item) => {
      totalValue += item.quantity * item.price;
    });
    return totalValue;
  }

  // Your array of categories menu laterale
  const categories = [
    "Cucina",
    "Menu Birra",
    "Menu Bibita",
    "Panini Singoli",
    "Pizza",
    "Bevande",
  ];

  console.log("Array di categorie:", categories);

  // Get the container element
  const categoryListContainer = document.getElementById("category-list");

  // Seleziona la prima categoria come inizialmente selezionata
  let primaCategoria = true;

  // Loop through the categories and create elements
  categories.forEach((category) => {
    // Replace spaces with underscores in category IDs and names
    const categoryId = category.toLowerCase().replace(/\s+/g, "_");
    const categoryName = category.toLowerCase().replace(/\s+/g, "_");

    // Create a new div element
    const categoryDiv = document.createElement("div");
    categoryDiv.className = "flex items-center";

    // Create an input element
    const inputElement = document.createElement("input");
    inputElement.className =
      "form-checkbox rounded-full text-primary border-default-400 bg-transparent w-5 h-5 focus:ring-0 focus:ring-transparent ring-offset-0 cursor-pointer";
    inputElement.id = categoryId;
    inputElement.name = categoryName; // Corretto da categoryId a categoryName
    inputElement.type = "checkbox";
    inputElement.checked = primaCategoria; // Imposta il check sulla prima categoria
    primaCategoria = false;

    // Create a label element
    const labelElement = document.createElement("label");
    labelElement.className =
      "ps-3 inline-flex items-center text-default-600 text-lg select-none";
    labelElement.htmlFor = categoryId;
    labelElement.textContent = category;

    // Append the input and label elements to the category div
    categoryDiv.appendChild(inputElement);
    categoryDiv.appendChild(labelElement);

    // Aggiungi l'evento di click al div della categoria
    categoryDiv.addEventListener("click", categoriaClick);

    // Append the category div to the category list container
    categoryListContainer.appendChild(categoryDiv);
  });
}
