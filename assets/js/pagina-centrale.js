// Il tuo JSON pagina centrale
var json = {
  cucina: [
    {
      name: "Pasta Primavera",
      desc: "Pomodoro e Mozzarella",
      img: "",
      price: "4,00",
    },
    {
      name: "Primo del Giorno",
      desc: "",
      img: "",
      price: "8,00",
    },
    {
      name: "Fritto Misto",
      desc: "",
      img: "",
      price: "12,00",
    },
    {
      name: "Grigliata di Carne",
      desc: "",
      img: "",
      price: "10,00",
    },
    {
      name: "Contorno del Giorno",
      desc: "",
      img: "",
      price: "3,50",
    },
    {
      name: "Patatine Fritte",
      desc: "",
      img: "",
      price: "3,00",
    },
  ],
  "menu panini": [
    {
      "menu birra": [
        {
          name: "Hamburger",
          desc: "Pomodori e insalata",
          img: "assets/burger-4-f1185701.png",
          price: "9,50",
        },
        {
          name: "Cheeseburger",
          desc: "Formaggio, pomodori e insalata",
          img: "",
          price: "9,50",
        },
        {
          name: "Baconburger",
          desc: "Formaggio, bacon, pomodori e insalata",
          img: "",
          price: "9,50",
        },
        {
          name: "Wurstel",
          desc: "",
          img: "",
          price: "9,50",
        },
        {
          name: "Wurstel e Crauti",
          desc: "",
          img: "",
          price: "9,50",
        },
        {
          name: "Salamella",
          desc: "",
          img: "",
          price: "9,50",
        },
        {
          name: "Salamella con Cipolle",
          desc: "",
          img: "",
          price: "9,50",
        },
        {
          name: "Vegetariano",
          desc: "Mozzarella, pomodori e insalata",
          img: "assets/burger-dee4db61.png",
          price: "9,50",
        },
      ],
    },
    {
      "menu bibita": [
        {
          name: "Hamburger",
          desc: "Pomodori e insalata",
          img: "",
          price: "8,50",
        },
        {
          name: "Cheeseburger",
          desc: "Formaggio, pomodori e insalata",
          img: "",
          price: "8,50",
        },
        {
          name: "Baconburger",
          desc: "Formaggio, bacon, pomodori e insalata",
          img: "",
          price: "8,50",
        },
        {
          name: "Wurstel",
          desc: "",
          img: "",
          price: "8,50",
        },
        {
          name: "Wurstel e Crauti",
          desc: "",
          img: "",
          price: "8,50",
        },
        {
          name: "Salamella",
          desc: "",
          img: "",
          price: "8,50",
        },
        {
          name: "Salamella con Cipolle",
          desc: "",
          img: "",
          price: "8,50",
        },
        {
          name: "Vegetariano",
          desc: "Mozzarella, pomodori e insalata",
          img: "",
          price: "8,50",
        },
      ],
    },
  ],
  "panini singoli": [
    {
      name: "Hamburger",
      desc: "Pomodori e insalata",
      img: "",
      price: "5,00",
    },
    {
      name: "Cheeseburger",
      desc: "Formaggio, pomodori e insalata",
      img: "",
      price: "5,00",
    },
    {
      name: "Baconburger",
      desc: "Formaggio, bacon, pomodori e insalata",
      img: "",
      price: "5,00",
    },
    {
      name: "Wurstel",
      desc: "",
      img: "",
      price: "5,00",
    },
    {
      name: "Wurstel e Crauti",
      desc: "",
      img: "",
      price: "5,00",
    },
    {
      name: "Salamella",
      desc: "",
      img: "",
      price: "5,00",
    },
    {
      name: "Salamella con Cipolle",
      desc: "",
      img: "",
      price: "5,00",
    },
    {
      name: "Vegetariano",
      desc: "Mozzarella, pomodori e insalata",
      img: "",
      price: "5,00",
    },
  ],
  pizza: [
    {
      name: "Pomodoro",
      desc: "",
      img: "",
      price: "4,50",
    },
    {
      name: "4 Stagioni",
      desc: "",
      img: "",
      price: "4,50",
    },
    {
      name: "Margherita",
      desc: "",
      img: "",
      price: "4,50",
    },
    {
      name: "Diavola",
      desc: "",
      img: "",
      price: "4,50",
    },
  ],
  bevande: [
    {
      name: "Acqua",
      desc: "",
      img: "",
      price: "1,00",
    },
    {
      name: "Bibita in Lattina",
      desc: "",
      img: "",
      price: "1,50",
    },
    {
      name: "Birra 0,4L",
      desc: "",
      img: "",
      price: "5,00",
    },
    {
      name: "Vina Sfuso 0,5L",
      desc: "",
      img: "",
      price: "3,50",
    },
    {
      name: "Vino Sfuso 1L",
      desc: "",
      img: "",
      price: "6,00",
    },
  ],
};

// Seleziona il primo array (categoria "Cucina")
var primoArray = json["cucina"];

// Seleziona il container del menu
var containerMenu = document.getElementById("container-menu");

// Ciclo sugli oggetti del primo array e generazione dinamica degli elementi del menu
for (var i = 0; i < primoArray.length; i++) {
  var oggetto = primoArray[i];

  // Creazione dell'elemento del menu
  var menuElement = document.createElement("div");
  menuElement.className =
    "xl:order-1 order-2 border border-default-200 rounded-lg p-4 overflow-hidden hover:border-primary hover:shadow-xl transition-all duration-300";

  menuElement.innerHTML = `
  <div class="relative rounded-lg overflow-hidden divide-y divide-default-200 group">
    <div class="mb-4 mx-auto">
      <img class="w-full h-full group-hover:scale-105 transition-all" src="${oggetto.img}" />
    </div>

    <div class="pt-2">
      <div class="flex items-center justify-between mb-4">
        <a class="text-default-800 text-xl font-semibold line-clamp-1 after:absolute after:inset-0" href="product-detail.html">${oggetto.name}</a>
        <span>${oggetto.desc}</span>
        <!-- <i class="h-6 w-6 text-red-500 fill-red-500 cursor-pointer" data-lucide="heart"></i> -->
      </div>
      <!-- Altre parti dell'HTML possono essere personalizzate in base alle tue esigenze -->
      <!--  <span class="inline-flex items-center gap-2 mb-4">
        <span class="bg-primary rounded-full p-1">
          <i class="h-3 w-3 text-white fill-white" data-lucide="star"></i>
        </span>
        <span class="text-sm text-default-950 from-inherit">4.5</span>
      </span> --> 

      <div class="flex items-end justify-between mb-4">
        <h4 class="font-semibold text-xl text-default-900">${oggetto.price}</h4>
        <div class="relative z-10 inline-flex justify-between border border-default-200 p-1 rounded-full">
          <button class="minus flex-shrink-0 bg-default-200 text-default-800 rounded-full h-6 w-6 text-sm inline-flex items-center justify-center" type="button">–</button>
          <input class="w-8 border-0 text-sm text-center text-default-800 focus:ring-0 p-0 bg-transparent" max="100" min="0" readonly="" type="text" value="1" />
          <button class="plus flex-shrink-0 bg-default-200 text-default-800 rounded-full h-6 w-6 text-sm inline-flex items-center justify-center" type="button">+</button>
        </div>
      </div>

      <a class="relative z-10 w-full inline-flex items-center justify-center rounded-full border border-primary bg-primary px-6 py-3 text-center text-sm font-medium text-white shadow-sm transition-all duration-500 hover:bg-primary-500" href="cart.html">Aggiungi al carrello</a>
    </div>
  </div>
`;

  // Aggiungi l'elemento del menu al container
  containerMenu.appendChild(menuElement);
}
