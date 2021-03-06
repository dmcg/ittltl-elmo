/*	Script invoked from web-page that reads a local JSON file and displays the remaining budget for the teams

	File contains something like:
	x={
		"session": {
			"end": "2013-06-21 18:00",		(end of the session)
			"session-factor": 100,			(multiplier for number of runs)
			"seconds-factor": 200,			(multiplier for cumulative run-time)
			"bar-duration": 5.5				(bar duration in hours for scaling)
		},
		"remotes": [
			["raspberry", "pi@raspberrypi.local"],	(list of remotes to interrogate)
			["raspberry", "pi@raspberrypi2.local"]
		],
		"login": {
			'tomato': (36, 1.6200000000000008),	(teamname: (number of runs, cumulative time of runs) )
			'green': (3, 0.44000000000000006),
			'red': (4, 1.92)
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
var barDuration = 5

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
		sessionFactor = data["session"]["session-factor"]
		secondsFactor = data["session"]["seconds-factor"]
		barDuration = data["session"]["bar-duration"]
	} catch (TypeError) {
		dontPanic()
	}
	
	// Collect cumulative spend then sort, largest balance wins (NB hence have to be objects)
	var endTime = new Date(data["session"]["end"])
	var balance = (endTime - new Date())
	//console.log('endTime', endTime)

	spend = [];
	for (key in login) {
		var t = new Object();
		t.name = String(key);
		t.balance = t.name in finished
				? (endTime - new Date(finished[t.name])) / 1000
				: balance / 1000 - spending(t.name, login[key][0], login[key][1]);
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

	// Do the team name
	ctx.font = "40px Arial";
	ctx.textAlign = 'center';
	ctx.fillStyle = team.name;
	ctx.fillText(team.name, 100, 60);
	ctx.textAlign = 'right';

	// Draw outlined bar (if balance +ve)
	if (team.balance > 0) {
		barWidth = ctx.canvas.width - 420
		durationSeconds = 3600 * barDuration
		width = barWidth * team.balance / durationSeconds

		ctx.fillRect(400, 10, width, 70);

		ctx.strokeStyle="black";
		ctx.rect(400, 10, barWidth, 70)
		ctx.stroke();

		ctx.fillStyle = "black"
	} else {
		ctx.fillStyle = "red";
	}
	
	// Draw balance numerically (red for -ve)
	prefix = team.balance > 0 ? ' ' : '-'
	millis = Math.abs(1000 * team.balance)
	timeStr = prefix + new Date(millis).toTimeString().substring(0,8)
	//console.log(team.name, timeStr, Math.round(team.balance))
	ctx.fillText(timeStr, 380, 60);

	// Restore the previous drawing state
	ctx.restore();
}

function spending(name, count, seconds) {
	var result = sessionFactor * count + secondsFactor * seconds;
	console.log(name, count, seconds, result);
	return result;
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