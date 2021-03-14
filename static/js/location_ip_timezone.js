// $.get("http://ipinfo.io", function(response) {
  // $.ajax({
  //   type : 'POST',
  //   url : "http://127.0.0.1:5000/",
  //   data : {'data':JSON.stringify(response)}
  // });
// }, "jsonp");
$(window).on('load',function(){
  function showPosition(position) {
    console.log("Latitude "+position.coords.latitude + 
    "Longitude: " + position.coords.longitude);
    $.ajax({
      type: 'POST',
      url: "http://127.0.0.1:5000/home",
      data: { 'data': JSON.stringify({ 'lat': position.coords.latitude, 'long': position.coords.longitude }) }
    });
  }
  navigator.geolocation.getCurrentPosition(showPosition);
});