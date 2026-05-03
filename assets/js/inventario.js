// Funzione principale che viene eseguita una volta che il DOM è pronto
document.addEventListener("DOMContentLoaded", function () { });
toastr.options = {
  timeOut: "1500",
};

var categorieMenuMap = {};
let firstTime = 1;
let categoryId = 1

// Modifica la funzione loadExternalJsonAndInitialize per utilizzare la chiamata API
async function loadExternalJsonAndInitialize(apiUrl) {
  try {
    const response = await fetch(apiUrl); // Esegui la chiamata API
    //console.log("Chiamata API riuscita:", response);
    const data = await response.json(); // Estrai i dati JSON dalla risposta
      //display page
      document.getElementById("button-apri-inventario").style.pointerEvents = "none"
      document.getElementById("preloader-container").style.display = "none"
      document.getElementById("whole-page").style.display = ""

      // Inizializza l'applicazione con il JSON caricato
      initializeApp(data);
      // Simula un click sulla prima categoria per avviare il caricamento del menu promozionale
      const primaCategoriaCheckbox = document.querySelector(
        '#category-list input[type="checkbox"]'
      );
      if (firstTime){
      primaCategoriaCheckbox.click();
      firstTime = 0
      }
      updateMenu(categoryId);
  } catch (error) {
    console.error("Errore nel caricamento dei dati dall'API:", error);
  }
}


// Funzione per inizializzare l'applicazione con il JSON (Lista prodotti) fornito
function initializeApp(data) {
  // Mappa delle categorie ai rispettivi array di menu
  const json = data;
  console.log(json);
  //key = category, item= list of products
  categorieMenuMap = {
    pizza: json["pizza"] || [],
    panini_singoli: json["panini"] || [],
    menu_birra: json["menu birra"] || [],
    cucina: json["cucina"] || [],
    bar: json["bevande"] || [],
    menu_bibita: json["menu bibita"] || [],
  };

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
    categoryId = checkbox.id;

    // Esegui le azioni desiderate con l'ID della categoria
    console.log(`Hai cliccato sulla categoria con ID: ${categoryId}`);

    // Aggiorna il menu in base alla categoria selezionata
    updateMenu(categoryId);
  }






  // Your array of categories menu laterale
  const categories = [
    "Cucina",
    "Panini Singoli",
    "Pizza",
    "Bar",
  ];

  console.log("Array di categorie:", categories);

  // Get the container element
  const categoryListContainer = document.getElementById("category-list");

  // Seleziona la prima categoria come inizialmente selezionata
  let primaCategoria = true;

  // Loop through the categories and create elements
  if (firstTime){
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
}


async function inviaUpdate(updatePayload) {
    let response = await fetch("http://" + self.location.host + "/api/updateInventory", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updatePayload),
    });
    let data = await response.json();
    if (data.status == "success") {
      closePopup();
      init();
    } else {
      const updateButton = document.querySelector("#update-item");
      updateButton.style.pointerEvents = "all"
      updateButton.classList.remove("opacity-50");
      updateButton.disabled = false
      toastr.error("Errore nell'invio dell'aggiornamento. Riprovare:", "Errore", { timeOut: 10000 });
    }
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
    // Nascondi il popup e l'overlay
    popupContainer.style.display = "none";
    overlay.style.display = "none";
}

// Funzione per aggiornare il menu in base alla categoria selezionata
function updateMenu(categoryId) {
    // Seleziona il container del menu
    const containerMenu = document.getElementById("container-menu");

    // Seleziona l'array di menu corrispondente alla categoria
    const arrayMenu = categorieMenuMap[categoryId];

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
        if (oggetto.inventoryCheck == 0){
         menuElement.style.backgroundColor = "rgba(211,211,211,0.6)"
         }
        menuElement.className =
          "xl:order-1 order-2 border border-default-200 rounded-lg p-4 overflow-hidden hover:border-primary hover:shadow-xl transition-all duration-300";

        menuElement.innerHTML = `

        <div class="relative rounded-lg overflow-hidden divide-y divide-default-200 group">

          <div class="pt-2">
            <div id="obj-desc-container" style="flex-flow: column;" class="flex justify-between mb-4">
              <span class="text-default-800 text-xl font-semibold line-clamp-3 after:absolute after:inset-0">${oggetto.name}</span>

            </div>
            <label for="enableCheckbox_${menuId}">Abilita disponibilità</label>
            <input type="checkbox" disabled id="enableCheckbox_${menuId}" style="width: 20px; height: 20px; border: 2px solid #333; border-radius: 3px; cursor: pointer; position: relative;">

            <br>
            <label>Disponibilità: <span id="disponibilita_${menuId}">0</span></label>
            <div class="flex items-end justify-between mb-4">
              <h4 class="font-semibold text-xl text-default-900">€ ${oggetto.price}</h4>
            </div>

            <a id="modifica-elemento" class="relative z-10 w-full inline-flex items-center justify-center rounded-full border border-primary bg-primary px-6 py-3 text-center text-sm font-medium text-white shadow-sm transition-all duration-500 hover:bg-primary-500" href="cart.html">Modifica</a>
          </div>
        </div>

            `;

        // Aggiungi l'elemento del menu al container
        containerMenu.appendChild(menuElement);
        menuElement.querySelector("#disponibilita_" + menuId).textContent = oggetto.availability //todo rivedere inventario
        menuElement.querySelector("#enableCheckbox_" + menuId).checked = oggetto.inventoryCheck
        // Aggiungi eventi di click ai pulsanti e all'elemento "add-cart"
        const modifyButton = menuElement.querySelector("#modifica-elemento");

        // Aggiungi l'event listener all'elemento "modifica-elemento" solo se è stato trovato
        if (modifyButton) {
          modifyButton.addEventListener("click", function (event) {
          // Previeni il comportamento di default del link
          event.preventDefault();
          //make screen unclickable
        const MenuContainer1 = (document.getElementById(
          "container-menu"
        ).style.pointerEvents = "none");
        const MenuContainer2 = (document.getElementById(
          "filter_Offcanvas"
        ).style.pointerEvents = "none");
          openModifyPopup(oggetto);

        })
       }

      }
    }
  }
function openModifyPopup(oggetto){
    console.log(oggetto)
    const popupContainer = document.getElementById("popup-container");
    let enableDefault = oggetto.inventoryCheck
    // Creare HTML dinamico con i dati mappati
    let htmlContent = `<h4 class="text-xl text-default-700 font-bold mb-5 text-center">${oggetto.name}</h4>
                        <hr>
                        <label style="display: flex; align-items: center; gap: 10px; font-size: 18px; margin: 5px 0;">
  Abilita disponibilità
  <input type="checkbox" id="modificaCheck"
         style="width: 20px; height: 20px; cursor: pointer;">
</label>

<label for="modificaDisponibilita" style="display: flex; align-items: center; font-size: 18px; margin: 5px 0 15px;">
  Disponibilità
<input type="number" id="modificaDisponibilita"
       style="width: 140px; padding: 8px 12px; font-size: 18px; border: 1px solid #ccc; border-radius: 6px; margin: 0 10px 0"
       placeholder="Inserisci numero">
</label>`
    htmlContent += `<a id="update-item" class="relative w-full inline-flex items-center justify-center rounded-full border border-primary bg-primary px-6 py-3 text-center text-sm font-medium text-white shadow-sm transition-all duration-500 hover:bg-primary-500" href="#">Aggiorna</a>`
    popupContainer.innerHTML = `<span class="font-semibold text-primary text-xl" id="close-button" ><button><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="x-circle" class="lucide lucide-x-circle w-5 h-5 text-primary text-default-400"><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg></button></span>${htmlContent}`;
    const checkbox = document.getElementById("modificaCheck")
    checkbox.checked = enableDefault
    const closePopupButton = popupContainer.querySelector("#close-button");
    const inputDispo = document.getElementById("modificaDisponibilita");
    inputDispo.value = oggetto.availability
    closePopupButton.addEventListener("click", function () {
      //scarta le modifiche
      closePopup();
    });

    const updateButton = popupContainer.querySelector("#update-item")
    if (updateButton) {
          updateButton.addEventListener("click", function (event) {
          // Previeni il comportamento di default del link
          event.preventDefault();
          let disponibilita = parseInt(inputDispo.value);
          payload = {"itemId": oggetto.productId, //todo rivedere inventario
               "availability": disponibilita,
               "inventoryCheck": checkbox.checked ? 1 : 0, }
          updateButton.classList.add("opacity-50");
      updateButton.style.pointerEvents = "none"
      updateButton.disabled = true
      inviaUpdate(payload)
       })
    }
    // Mostra il pop-up
    popupContainer.style.display = "flex";
  }