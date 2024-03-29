// import { Client } from "@petfinder/petfinder-js";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// curl -d "grant_type=client_credentials&client_id={'nRVIaz6AEO2qZ6DCKXDKcw3EX4zRxbjKz64UQDFheRh5VBdAIE'}&client_secret={'obAhKvjIzSik0WT6T7yrMTkKYQcsSUj8nktFxGJF'}" https://api.petfinder.com/v2/oauth2/token

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

	// This is the Vue data.
	app.data = {
		match_cards: [],
		disp_cards_idx: 1,
		cur_email: "",
		email: "",
		phone: "",
		address: "",
		
		name: "",
		url: "",
		breed: "",
		age: "",
		gender: "",
		size: "",
		fur: "",
		potty: "",
		kid: "",
		image: "",
		loading: false,
	};

	
	app.enumerate = (a) => {
		let k = 0;
		a.map((e) => { e._idx = k++;});
		return a;
	};

	app.getMatchContactFromAPI = async function getMatchContactFromAPI(id) {
		var client = new petfinder.Client({
			apiKey: "nRVIaz6AEO2qZ6DCKXDKcw3EX4zRxbjKz64UQDFheRh5VBdAIE",
			secret: "obAhKvjIzSik0WT6T7yrMTkKYQcsSUj8nktFxGJF"
		});
		app.vue.loading = false;
		client.animal.show(id)
			.then(resp => {
				// Do something with resp.data.animal
				app.vue.email = resp.data.animal.contact.email;
				app.vue.phone = resp.data.animal.contact.phone;
				app.vue.address = 	resp.data.animal.contact.address.city+ ", "+ 
									resp.data.animal.contact.address.state+ ", "+
									resp.data.animal.contact.address.postcode+" " +
									resp.data.animal.contact.address.country;
				app.vue.loading = true;
			});
		var contact_modal = document.getElementById("contact_modal");
		contact_modal.classList.toggle('is-active');
	}

	app.delete_match = function (row_idx) {
		// console.log(row_idx)
		let id = app.vue.match_cards[row_idx].id;
		// console.log(id)
		axios.get(delete_match_url, { params: { id: id } }).then(function (response) {
			for (let i = 0; i < app.vue.match_cards.length; i++) {
				if (app.vue.match_cards[i].id === id) {
					app.vue.match_cards.splice(i, 1);
					app.enumerate(app.vue.match_cards);
					break;
				}
			}
		});
		var delete_modal = document.getElementById("delete_modal");
		delete_modal.classList.toggle('is-active');
	};

	app.select_delete_match = function (row_idx) {
		app.vue.disp_cards_idx = row_idx;
		var delete_modal = document.getElementById("delete_modal");
		delete_modal.classList.toggle('is-active');
	};

	app.getMatchInfoFromAPI = async function getMatchInfoFromAPI(id) {
		var client = new petfinder.Client({
			apiKey: "nRVIaz6AEO2qZ6DCKXDKcw3EX4zRxbjKz64UQDFheRh5VBdAIE",
			secret: "obAhKvjIzSik0WT6T7yrMTkKYQcsSUj8nktFxGJF"
		});
		app.vue.loading = false;
		client.animal.show(id)
			.then(resp => {
				// Do something with resp.data.animal
				app.vue.name= resp.data.animal.name;
                app.vue.url= resp.data.animal.url;
                app.vue.breed= resp.data.animal.breeds.primary;
                app.vue.age= resp.data.animal.age;
				app.vue.gender= resp.data.animal.gender;
				app.vue.size= resp.data.animal.size;
				app.vue.fur= resp.data.animal.colors.primary;
				app.vue.potty= resp.data.animal.attributes.house_trained;
				app.vue.kid= resp.data.animal.environment.children;
				app.vue.loading = true;
			});
		var info_modal = document.getElementById("info_modal");
		info_modal.classList.toggle('is-active');
	}

	// We form the dictionary of all methods, so we can assign them
	// to the Vue app in a single blow.
	app.methods = {
		enumerate: app.enumerate,
		getMatchContactFromAPI: app.getMatchContactFromAPI,
		getMatchInfoFromAPI: app.getMatchInfoFromAPI,
		delete_match: app.delete_match,
		select_delete_match: app.select_delete_match,
	};

	// This creates the Vue instance.
	app.vue = new Vue({
		el: "#vue-matches",
		data: app.data,
		methods: app.methods,
	});


	// And this initializes it.
	// This is where im going to pull current_pup_cards from the data base
	// and then set all their values up, and then set up each cards data
	// make sure to call get_next_pupcards if needed
	app.init = () => {
		// console.log("match init");
		let match_ids = []
		axios.get(get_matches_id_url)
			.then(function (response) {
				match_ids = response.data.match_ids;
				app.vue.match_cards = [];
				for (var i = 0; i < match_ids.length; i++) {
					// console.log("match pup init\n");
					axios.get(get_curr_matches_url, { params: { match_id: match_ids[i] } })
						.then(function (response) {
							// console.log(response);
							// console.log(response)
							let image = response.data.dog_images
		
							app.vue.match_cards.push({
								_idx: 0,
								id: response.data.id,
								user_owned: response.data.user_owned,
								dog_index: response.data.dog_index,
								dog_name: response.data.dog_name,
								dog_images: image,
							})
							app.enumerate(app.vue.match_cards);
						});
						
				}
			});
					
	};


	// Call to the initializer.
	app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
