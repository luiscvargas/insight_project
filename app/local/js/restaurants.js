$( document ).ready(function() {

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
   
   var cuisines = ["mexican", "chinese", "japanese", "latin", "greek",
                   "puertorican","cuban","indpak","italian","newamerican",
                   "tradamerican","vegetarian","arabian", "brazilian", 
                   "cafes", "diners", "ethiopian", "korean", "mideastern", 
                   "peruvian","colombian", "pizza", "seafood", "soup", 
                   "spanish", "french", "turkish", "vegan"] 
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
      var zipcode = $(this).children(".list-results-zip").text();
      var map_url = "https://www.google.com/maps/embed/v1/place?key=AIzaSyCq-IuPHd2vSr9fSgcMzkRupw02DjDLJ2o&zoom=13&q="+zipcode;
      $("#google-map").attr("src",map_url);
      console.log(zipcode);
   });
   
});

