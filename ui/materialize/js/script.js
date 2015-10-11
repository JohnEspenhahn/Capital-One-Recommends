$(document).ready(function() {
	$('#modalLogin').openModal();

	$("#loginButton").click(function() {
		$('#map').show();
		$('#mapSidebar').show();
		$('#modalRegister').hide();
		$('#modalLogin').hide();


		$.post("http://localhost:5000/login", {
				username: $("#lusername").val(),
				password: $("#lpassword").val()
			},
			function(data, textStatus, jqxhr) {
				console.log(data);
				if(data.substring(0,4) == "fail") {
					Materialize.toast("Invalid username/password. Please try again.", 4000);
				} else {
					Materialize.toast("Login successful.", 4000);
				}
			}
		);
	});
});