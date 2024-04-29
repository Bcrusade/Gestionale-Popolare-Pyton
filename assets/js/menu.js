// Funzione per aggiornare il menu in base alla categoria selezionata
function updateMenu(categoryId) {
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
      const cleanedName = name.replace(/\s/g, "_").toLowerCase();
      const cleanedCategoryId = categoryId.replace(/\s/g, "_").toLowerCase();
      return `${cleanedCategoryId}-${cleanedName}`;
    }

    // Ciclo sugli oggetti dell'array e generazione dinamica degli elementi del menu
    for (let i = 0; i < arrayMenu.length; i++) {
      const oggetto = arrayMenu[i];

      // Creazione dell'elemento del menu con un ID univoco basato sul nome e l'ID della categoria
      const menuElement = document.createElement("div");
      const menuId = generateUniqueId(oggetto.name, categoryId); // Aggiunto categoryId come secondo parametro
      menuElement.id = menuId;
      menuElement.className =
        "xl:order-1 order-2 border border-default-200 rounded-lg p-4 overflow-hidden hover:border-primary hover:shadow-xl transition-all duration-300";

      // Inizializza la variabile prezzoIniziale per questo ID se non esiste
      if (!prezzoInizialeMap[menuId]) {
        prezzoInizialeMap[menuId] = parseFloat(oggetto.price) || 0;
      }

      menuElement.innerHTML = `
            
        <div class="relative rounded-lg overflow-hidden divide-y divide-default-200 group">
          <div class="mb-4 mx-auto">
            <img class="w-full h-full group-hover:scale-105 transition-all" src="${oggetto.img}" />
          </div>
  
          <div class="pt-2">
            <div id="obj-desc-container" style="flex-flow: column;" class="flex justify-between mb-4">
              <span class="text-default-800 text-xl font-semibold line-clamp-1 after:absolute after:inset-0">${oggetto.name}</span>
              <i class="text-m text-default-500">${oggetto.desc}</i>
              <div class="border border-default-200 inline-flex justify-between mt-2 p-1 relative rounded-full z-10">
              <input id="input_${menuId}" type="text" placeholder="Inserisci modifiche" class="border-none h-3 w-full" />
              </div>
            </div>
  
            <div class="flex items-end justify-between mb-4">
              <h4 class="font-semibold text-xl text-default-900">€ ${oggetto.price}</h4>
              <div class="relative z-10 inline-flex justify-between border border-default-200 p-1 rounded-full">
                <button class="minus flex-shrink-0 bg-default-200 text-default-800 rounded-full h-6 w-6 text-sm inline-flex items-center justify-center" type="button">–</button>
                <input id="quantity" class="w-8 border-0 text-sm text-center text-default-800 focus:ring-0 p-0 bg-transparent" max="100" min="0" readonly="" type="text" value="1" />
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
      const quantityInput = menuElement.querySelector("input#quantity");

      minusButton.addEventListener("click", function () {
        // Verifica se la quantità è maggiore di 0 prima di ridurla
        if (parseInt(quantityInput.value, 10) > 0) {
          // Riduci la quantità, assicurandoti che non scenda al di sotto del minimo
          quantityInput.value = Math.max(
            parseInt(quantityInput.value, 10) - 1,
            0
          );

          // Aggiorna la variabile prezzoIniziale specifica per questo ID
          prezzoInizialeMap[menuId] = calculateUpdatedPrice(
            prezzoInizialeMap[menuId],
            oggetto.price,
            -1
          );
        } else {
          console.log(
            "La quantità è già 0, impossibile ridurre ulteriormente."
          );
          toastr.warning(
            "La quantità è già 0. Impossibile ridurre ulteriormente."
          );
        }
      });

      plusButton.addEventListener("click", function () {
        // Aumenta la quantità, assicurandoti che non superi il massimo
        quantityInput.value = Math.min(
          parseInt(quantityInput.value, 10) + 1,
          100
        );

        // Aggiorna la variabile prezzoIniziale specifica per questo ID
        prezzoInizialeMap[menuId] = calculateUpdatedPrice(
          prezzoInizialeMap[menuId],
          oggetto.price,
          1
        );

        // Visualizza il prezzoIniziale nel log
        console.log(
          `Prezzo Iniziale per ${menuId} (dopo click su plus):`,
          prezzoInizialeMap[menuId]
        );
      });

      // Aggiungi l'event listener all'elemento "add-cart" solo se è stato trovato
      if (addCartButton) {
        addCartButton.addEventListener("click", function (event) {
          // Previeni il comportamento di default del link
          event.preventDefault();

          // Seleziona l'elemento input per l'oggetto corrente
          const inputId = `input_${menuId}`;
          const noteInput = document.getElementById(inputId);

          // Verifica se la quantità è maggiore di 0 prima di procedere con l'aggiunta al carrello
          if (parseInt(quantityInput.value, 10) > 0) {
            // Salva le informazioni desiderate come variabili globali
            globalPrice = Math.max(prezzoInizialeMap[menuId], 0);
            globalQuantity = Math.max(parseInt(quantityInput.value, 10), 0);
            globalImage = oggetto.img;
            globalName = oggetto.name;
            globalID = menuId;

            // Ottieni il valore dall'input solo se la lunghezza è maggiore di 0
            if (noteInput && noteInput.value.trim().length > 0) {
              globalNote = noteInput.value.trim();
            } else {
              globalNote = ""; // Imposta globalNote a una stringa vuota se la lunghezza è 0
            }

            // Chiama la funzione per salvare le variabili globali
            saveGlobalVariables();

            // Chiama la funzione per generare l'HTML dinamico
            generateDynamicHTML();
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

  // Funzione per calcolare il prezzo aggiornato in base all'incremento o decremento
  function calculateUpdatedPrice(currentPrice, unitPrice, increment) {
    return currentPrice + parseFloat(unitPrice) * increment || 0;
  }
}
