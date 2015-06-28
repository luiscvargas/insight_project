$( document ).ready(function() {
      
   //$(".fancybox").fancybox();

   $(".list-results").hover(
      function() {
         $(this).addClass("hover");
         $(this).next().addClass("hover");
      },
      function() {
         $(this).removeClass("hover");
         $(this).next().removeClass("hover");
      }
   );
   
   var cuisines = ["Mexican", 
	"Chinese", "Japanese", "Latin", 
	"Greek","Puerto Rican","Cuban",
	"Indian","Italian","Modern American",
   "Traditional American","Vegetarian",
    "Arabian", "Brazilian", 
    "Cafes", "Diners", "Ethiopian", 
    "Korean", "Middle Eastern", 
	"Peruvian", "Colombian", "Pizza", 
	"Seafood", "Soup","Spanish", 
	"French", "Turkish", "Vegan"];
   
   // constructs the suggestion engine
   var cuisines = new Bloodhound({
   datumTokenizer: Bloodhound.tokenizers.whitespace,
   queryTokenizer: Bloodhound.tokenizers.whitespace,
   // `states` is an array of state names defined in "The Basics"
   local: cuisines
   });
 
   $('#cuisine-list .typeahead').typeahead({
   hint: true,
   highlight: true,
   minLength: 1
   },
   {
   name: 'cuisines',
   source: cuisines
   });
   
   $(".clickable-row").on("click", function() {
      //get zipcode
      var zipcode = $(this).children(".list-results-zip").text().trim();
      //get cuisine type
      var cuisine = $("#cuisine-type-hidden").text().trim();
      //add zipcode as value to button "more zipcode info"
      $("#detailed-info-button").text("More info on ZIP "+zipcode);
      $("#detailed-info-button").attr("value",zipcode+'_'+cuisine);
      $("#detailed-info-button").removeClass("disabled");
      //produce map for this zipcode
      var map_url = "https://www.google.com/maps/embed/v1/place?key=AIzaSyCq-IuPHd2vSr9fSgcMzkRupw02DjDLJ2o&zoom=13&q="+zipcode;
      $("iframe#google-map").attr("src",map_url);
      //console.log(zipcode);
   });

   
});