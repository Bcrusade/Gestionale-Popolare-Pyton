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
  const checkbox = event.currentTarget.querySelector('input[type="checkbox"]');
  checkbox.checked = true;

  // Ottieni l'ID e il testo della categoria cliccata
  const categoryId = checkbox.id;
  const categoryText = event.currentTarget.querySelector("label").textContent;

  // Esegui le azioni desiderate con l'ID e il testo della categoria
  console.log(
    `Hai cliccato sulla categoria con ID: ${categoryId} e testo: ${categoryText}`
  );

  // Cambia la pagina (puoi personalizzare l'URL come desiderato)
  window.location.href = `nuova-pagina.html?categoryId=${categoryId}&categoryText=${categoryText}`;
}

// Your array of categories menu laterale
const categories = [
  "Cucina",
  "Menù panini",
  "Panini singoli",
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
  // Create a new div element
  const categoryDiv = document.createElement("div");
  categoryDiv.className = "flex items-center";

  // Create an input element
  const inputElement = document.createElement("input");
  inputElement.className =
    "form-checkbox rounded-full text-primary border-default-400 bg-transparent w-5 h-5 focus:ring-0 focus:ring-transparent ring-offset-0 cursor-pointer";
  inputElement.id = category.toLowerCase().replace(/\s+/g, "-");
  inputElement.name = category.toLowerCase().replace(/\s+/g, "-");
  inputElement.type = "checkbox";
  inputElement.checked = primaCategoria; // Imposta il check sulla prima categoria
  primaCategoria = false;

  // Create a label element
  const labelElement = document.createElement("label");
  labelElement.className =
    "ps-3 inline-flex items-center text-default-600 text-sm select-none";
  labelElement.htmlFor = category.toLowerCase().replace(/\s+/g, "-");
  labelElement.textContent = category;

  // Append the input and label elements to the category div
  categoryDiv.appendChild(inputElement);
  categoryDiv.appendChild(labelElement);

  // Aggiungi l'evento di click al div della categoria
  categoryDiv.addEventListener("click", categoriaClick);

  // Append the category div to the category list container
  categoryListContainer.appendChild(categoryDiv);
});
