/*	Script invoked from web-page that reads a local JSON file and displays the remaining budget for the teams

	File contains something like:
	x={
		"session": {
			"end": "2013-06-21 18:00",		(end of the session)
			"pi-factor": 1					(scaling factor on time logged in on the pi)
		},
		"login": {
			"tomato": 10,					(team name & logged in seconds on pi)
			"erac": 0.0,
			"gold": 20, 
			"lime": 0
		},
		finished: {
			"unknown": "2013-06-21 12:00",	(team named and wall time team finished)
			"erac": "2013-06-21 13:00"
		}
	}
*/

// Global variable
var ACTIVITY_NAME = 'activity.jsonp';
var INTERVAL = 1000;

var ctx = null;

function init() {
	// Grab the canvas element
	var canvas = document.getElementById('canvas');
	
	// Canvas supported?
	if (canvas.getContext('2d')) {
		ctx = canvas.getContext('2d');
		setInterval(reload, INTERVAL);
	} else {
  		alert("Canvas not supported!");
  	}
}

function reload() {
	$.getScript(ACTIVITY_NAME, draw);
}

function draw(dataString, status) {
	//console.log("dataString", dataString)

	// Fill window with canvas
	ctx.canvas.width = window.innerWidth;
	ctx.canvas.height = window.innerHeight;

	// Parse fresh dataString
	var data = eval(dataString);
	var login = data["login"];
	var finished = data["finished"]
	try {
		piFactor = data["session"]["pi-factor"]
	} catch (TypeError) {
		dontPanic()
	}
	
	// Collect cumulative spend then sort, largest balance wins (NB hence have to be objects)
	var endTime = new Date(data["session"]["end"])
	var balance = (endTime - new Date())

	spend = [];
	for (key in login) {
		var t = new Object();
		t.name = String(key);
		t.balance = (t.name in finished
				? endTime - new Date(finished[t.name]) 
				: balance) / 1000
					- piFactor * login[key];
		spend.push(t);
	}
	spend.sort(function(a, b) {return b.balance - a.balance;});

	// Draw team results
	var y = 0
	for (var i = 0; i < spend.length; i++) {
		//console.log(y, spend[i])
		drawTeam(y, spend[i])
		y += 90
	}

}

function drawTeam(y, team) {
	ctx.save();
	ctx.translate(0, y);

	// Do the text
	ctx.font="40px Arial";
	ctx.textAlign = 'center';
	ctx.fillStyle = team.name;
	ctx.fillText(team.name, 100, 60);
	ctx.textAlign = 'right';

	if (team.balance > 0) {
		ctx.fillRect(400, 10, team.balance / 50, 70);
		ctx.fillStyle = "black"
	} else {
		ctx.fillStyle = "red";
	}
	ctx.fillText('\u00A3' + Math.round(team.balance), 360, 60);
	
	// Restore the previous drawing state
	ctx.restore();
}

function dontPanic() {
	ctx.save();

	// Do the text
	ctx.font="100px Arial";
	ctx.textAlign = 'center';
	ctx.fillStyle = 'tomato';
	ctx.fillText("Don't Panic", ctx.canvas.width / 2, ctx.canvas.height / 2);

	// Restore the previous drawing state
	ctx.restore();
}