$(document).ready(function() {
	$('#modalLogin').openModal();
	// $('#map').show();
    // $('#mapSidebar').show();

    $("#openRegisterButton").click(function() {
        $("#modalLogin").closeModal();
        $("#modalRegister").openModal();
    });

    $("#registerButton").click(function() {
    	$.ajax({
    		url: "http://globmont.com/capone/register.php",
    		dataType:"jsonp",
    		data: { username: $("#rusername").val(), password: $("#rpassword").val(), name: $("#rname").val(), account: $("#raccount").val(), mycallback: 'registerCallback' }
	    });
    });

    $("#loginButton").click(function() {
        $.ajax({
        	url: "http://globmont.com/capone/login.php", 
        	dataType:"jsonp",
        	data: { username: $("#lusername").val(), password: $("#lpassword").val(), mycallback: 'loginCallback' }
        });
    });
});

function registerCallback(data) {
	data = JSON.parse(data);
    if (data.success) {
    	$("#modalRegister").closeModal();
		$("#modalLogin").openModal();
    } else {
    	Materialize.toast('Failed to register', 1500);
    } 
}

function loginCallback(data) {
	console.log(data);
    data = JSON.parse(data);
    if (data.success) {
    	$("#modalLogin").closeModal();
        $('#map').show();
        $('#mapSidebar').show();

        captial_one_recommends.accID = data.id;
        $.post(
	        '/geojson',
	        {
	            accID: data.id
	        },
	        function(data) {
	            captial_one_recommends.geojson = JSON.parse(data);
	            console.log(captial_one_recommends.geojson);
	        });
    } else {
        Materialize.toast('Invalid login details', 1500);
    }
}