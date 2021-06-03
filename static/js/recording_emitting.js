//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording
var duration;                       //output_audio duration

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record
var interrupt = "no";
feature_just_selected = "";
var stage = 0;
var current_feature = "";
var qr_start_time;

window.onload = function () {
    callWelcomeMessage_and_start();
}

function callWelcomeMessage_and_start() {

    if (document.getElementById('getWeclome_msg').innerHTML == "true") {
        welcomeMessage = document.getElementById('default-messages');

        var xhttp = new XMLHttpRequest();

        xhttp.open('POST', encodeURI('http://127.0.0.1:5000/getWelcomeMessage'));
        xhttp.setRequestHeader('Content-Type', 'application/json');
        xhttp.responseType = 'blob';

        xhttp.onload = function (evt) {
            var blob = new Blob([xhttp.response], { type: 'audio/wav' });

            var objectUrl = URL.createObjectURL(blob);
            welcomeMessage.src = objectUrl;
            // Release resource when it's loaded
            welcomeMessage.onload = function (evt) {
                URL.revokeObjectURL(objectUrl);
            };

            welcomeMessage.onended = function (evt) {
                recordMode(1500);
            };

            welcomeMessage.load();
            var promise = welcomeMessage.play();

            if (promise !== undefined) {
                promise.then(_ => {

                }).catch(error => {
                    recordMode(1500);
                });
            }
        };
        xhttp.send();
    }
    else {
        recordMode(1500);
    }
}

function ListeningMode() {
    interrupt = "yes";
    document.getElementById("mic-box").style.pointerEvents = "none";
}

function ProcessMode() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_processing.gif)";
    console.log("Speaking mode");
    SpeakingMode();
}

function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}

function SpeakingMode() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_speaking.gif)";
    output_aud = document.getElementById('output_voice');

    var xhttp = new XMLHttpRequest();

    xhttp.open('POST', encodeURI('http://127.0.0.1:5000/fetch_output_audio'));
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.responseType = 'blob';
    xhttp.onload = function (evt) {
        var blob = new Blob([xhttp.response], { type: 'audio/wav' });
        var objectUrl = URL.createObjectURL(blob);

        output_aud.src = objectUrl;
        // Release resource when it's loaded
        output_aud.onload = function (evt) {
            URL.revokeObjectURL(objectUrl);
        };
        output_aud.onended = function () {
            interrupt = "no";
            var xhtp = new XMLHttpRequest();
            xhtp.open('GET', "http://127.0.0.1:5000/getfeature_name", false);
            xhtp.send();
            feature_just_selected = xhtp.responseText;
            console.log(feature_just_selected);
            additional_request(feature_just_selected.split(", "), output_aud.duration);
        };
        output_aud.load();
        output_aud.play();
    };
    xhttp.send();

}

function additional_request(feature_just_selected, duration_sleep) {
    // sleep(duration_sleep*1000)

    for (i = 0; i < feature_just_selected.length; i++) {
        if (feature_just_selected[i] == "music") {

            document.getElementById('music-modal').style.display = "block";
            interrupt = "yes";

            // document.body.style.backgroundImage = "url(../static/images/VA_anim4_speaking.gif)";
            console.log("music feature");

            //fetching music name and thumbnail url
            var xhtp = new XMLHttpRequest();
            xhtp.open('GET', "http://127.0.0.1:5000/getMusicDetails_toShow", false);
            xhtp.send();
            name_url = xhtp.responseText;

            music_name = document.getElementById("music-album-name");
            music_name.innerHTML = name_url.split("###--###")[0].slice(0, -4);
            console.log("music name set")

            music_image = document.getElementById("thumbnail-image");
            console.log("thumbnail_fetched!")
            music_image.src = name_url.split("###--###")[1];

            music_player = document.getElementById('music-player');

            // fetching audio api
            var xhttp = new XMLHttpRequest();

            xhttp.open('POST', encodeURI('http://127.0.0.1:5000/fetch_music_audio'));
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.responseType = 'blob';
            xhttp.onload = function (evt) {
                var blob = new Blob([xhttp.response], { type: 'audio/m4a' });
                var objectUrl = URL.createObjectURL(blob);

                music_player.src = objectUrl;
                // music_player.style = "display: inline-block";
                // Release resource when it's loaded
                music_player.onload = function (evt) {
                    URL.revokeObjectURL(objectUrl);
                };
                music_player.load();
                music_player.play();
            };
            xhttp.send();

            //display modal
        }

        else if (feature_just_selected[i] == "find-information") {
            
            console.log("Find Information feature");

            document.getElementById('findInfo-modal').style.display = "block";

            interrupt = "yes";

            // document.body.style.backgroundImage = "url(../static/images/VA_anim4_speaking.gif)";
            console.log("Find Information feature");

            //fetching music name and thumbnail url
            var xhtp = new XMLHttpRequest();
            xhtp.open('GET', "http://127.0.0.1:5000/getFindInfoDetails_toShow", false);
            xhtp.send();
            findInfoData = xhtp.responseText;


            var findInfo_urls = findInfoData.split("#-#")

            var findinfoDiv = document.getElementById('findInfoContent')

            var linebreak = document.createElement("br");

            for (var k=0;k<findInfo_urls.length;k++)
            {
                findInfo_urls_data = findInfo_urls[k].split("#^3^#")

                findInfo_urls_url = findInfo_urls_data[0]
                findInfo_urls_title = findInfo_urls_data[1]
                findInfo_urls_image = findInfo_urls_data[2]
                findInfo_urls_desc = findInfo_urls_data[3]

                

                var card = document.createElement("div");
                card.className="card";


                var makeAnch = document.createElement("a");
                makeAnch.setAttribute("href", findInfo_urls_data[0]);
                makeAnch.setAttribute("title",findInfo_urls_data[1]);
                makeAnch.setAttribute("target","_blank");

                var card_left = document.createElement("div");
                card_left.className="card_left";

                var card_image = document.createElement("img");
                
                var card_right = document.createElement("div");
                card_right.className="card_right";
                var cr_h1 = document.createElement("h1");
                cr_h1.text = findInfo_urls_data[1];
                var card_right_det = document.createElement("div");
                card_right_det.className="card_right__review";
                var cr_p = document.createElement("p");
                cr_p.text = findInfo_urls_data[3];

                
                try{
                    card_image.src = findInfo_urls_data[2];
                }
                catch(error){
                    card_image.src = "https://static.wikia.nocookie.net/nopixel/images/b/b4/Not-found-image-15383864787lu.jpg";
                }
                
                
                card_left.appendChild(card_image);
                
                card_right.appendChild(cr_h1);
                card_right_det.appendChild(cr_p);

                card_right.appendChild(linebreak);
                card_right.appendChild(card_right_det);

                makeAnch.appendChild(card_left);
                makeAnch.appendChild(card_right);
                
                card.appendChild(makeAnch);

                findinfoDiv.appendChild(card);

                findinfoDiv.appendChild(linebreak);
            }
        }

        else if (feature_just_selected[i] == "email-contact-not-found") {
            document.getElementById('contacts-modal').style.display = "block";
            interrupt = "yes";
            console.log("no contact found");
        }

        else if (feature_just_selected[i] == "email") {
            stage = 1;
            current_feature = "email";
            interrupt = "yes";
            console.log("email 1");
            document.getElementById("mic-box").style.pointerEvents = "none";
            document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
            justRecordMode(10000);
        }
        else if (feature_just_selected[i] == "email-stage2") {
            stage = 2;
            current_feature = "email";
            interrupt = "yes";
            console.log("email 2");
            document.getElementById("mic-box").style.pointerEvents = "none";
            document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
            justRecordMode(10000);
        }

        else if (feature_just_selected[i] == "message") {
            stage = 2;
            current_feature = "message";
            interrupt = "yes";
            console.log("message 2");
            document.getElementById("mic-box").style.pointerEvents = "none";
            document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
            justRecordMode(5000);
        }

        else if (feature_just_selected[i] == "message-scan-qr") {
            stage = 1;
            current_feature = "message-scan-qr";
            interrupt = "yes";
            console.log("message 1");
            document.getElementById("mic-box").style.pointerEvents = "none";

            document.getElementById('whats-app-qr-code-modal').style.display = "block";

            var xhttp = new XMLHttpRequest();

            qr_code = document.getElementById('qr-code');

            xhttp.open('GET', encodeURI('http://127.0.0.1:5000/get_qr_code'));
            xhttp.setRequestHeader('Content-Type', 'application/json');
            xhttp.responseType = 'blob';
            xhttp.onreadystatechange = function (evt) {
                if (this.readyState == 4) {
                    var blob = new Blob([xhttp.response], { type: 'image/png' });
                    var objectUrl = URL.createObjectURL(blob);

                    qr_code.src = objectUrl; 
                }
            };
            xhttp.send();
            var res="0";
            qr_start_time = Date.now();
            do {
                res = checkLoggedIn(qr_start_time);
                console.log(res);
                sleep(1500);
            }while(res=="0")
            // if (res == "1"){
            qr_code.src = "";
            document.getElementById('whats-app-qr-code-modal').style.display = "none";
            update_no_input_audio_stage(stage = 1 , current_feature = "message-scan-qr");
            // }
        }        
    }

    if (interrupt == "no") {
        recordMode(1500);
        reset();
    }
}

function checkLoggedIn(time) {
        var xhtp = new XMLHttpRequest();
        xhtp.open('GET', "http://127.0.0.1:5000/whatsapp_logged_in", false)
        
        xhtp.onreadystatechange = function() {
            if(this.readyState == 4)
            { 
                if(Date.now() - time > 20000){
                    var xhttp = new XMLHttpRequest();
                    xhttp.open('GET', encodeURI('http://127.0.0.1:5000/get_qr_code'));
                    xhttp.setRequestHeader('Content-Type', 'application/json');
                    xhttp.responseType = 'blob';
                    xhttp.onreadystatechange = function (evt) {
                        if (this.readyState == 4) {
                            var blob = new Blob([xhttp.response], { type: 'image/png' });
                            var objectUrl = URL.createObjectURL(blob);
                            qr_code.src = objectUrl; 
                        }
                    };
                    qr_start_time = Date.now();
                    xhttp.send();
                }
                // sleep(5000);
            }
        }
        xhtp.send();
        return xhtp.responseText;

     
}

function update_no_input_audio_stage(stage, current_feature){
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    fd.append("stage", stage);
    fd.append("feature", current_feature);
    fd.append("contains_audio","false");

    xhr.open("POST", "http://127.0.0.1:5000/process", true);
    xhr.onreadystatechange = function () {
        if (this.readyState == 4) {
            ProcessMode();
        }
    };

    xhr.send(fd);
}

function reset() {
    stage = 0;
    current_feature = "";
    document.getElementById("mic-box").style.pointerEvents = "auto";
    document.body.style.backgroundImage = "url(../static/images/VA_anim4-0.png)";
}

function justRecordMode(time) {
    var constraints = { audio: true, video: false }

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        audioContext = new AudioContext();

        gumStream = stream;

        input = audioContext.createMediaStreamSource(stream);

        rec = new Recorder(input, { numChannels: 1 })

        rec.record()

        console.log("Recording started");

        setTimeout(function () {

            rec.stop();

            gumStream.getAudioTracks()[0].stop();
            // interrupt = "no";
            rec.exportWAV(justUploadWAVFile);

            console.log("Recording done")

        }, time);
    }).catch((error) => {
        this.setState({
            error: error.message
        });
    });
}
function recordMode(time) {
    var constraints = { audio: true, video: false }

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        audioContext = new AudioContext();

        gumStream = stream;

        input = audioContext.createMediaStreamSource(stream);

        rec = new Recorder(input, { numChannels: 1 })

        rec.record()

        console.log("Recording started");

        setTimeout(function () {

            rec.stop();

            gumStream.getAudioTracks()[0].stop();
            // interrupt = "no";
            if (interrupt == "no") {
                rec.exportWAV(uploadWAVFile);
            }
            else {
                var xhttp = new XMLHttpRequest();
                xhttp.onreadystatechange = function () {
                    if (this.readyState == 4) {
                        document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
                        justRecordMode(10000);
                    }
                };
                xhttp.open("POST", "http://127.0.0.1:5000/set_command", false);
                xhttp.send();
            }

            console.log("Recording done")

        }, time);
    }).catch((error) => {
        this.setState({
            error: error.message
        });
    });
}

function blobToFile(theBlob, fileName) {
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}

function justUploadWAVFile(blob) {
    var input = document.createElement('input');
    input.type = "file";
    var filename = new Date().toISOString();

    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    fd.append("stage", stage);
    fd.append("feature", current_feature);
    fd.append("contains_audio","true");
    fd.append("audio_data", blob, filename + '.wav');
    xhr.onreadystatechange = function () {
        if (this.readyState == 4) {
            // console.log(times);
            if (JSON.parse(xhr.responseText)["continue"] == "YES") {
                recordMode(1500);
            }
            else {
                ProcessMode();
            }
        }
    };
    xhr.open("POST", "http://127.0.0.1:5000/process", true);
    xhr.send(fd);
    // ProcessMode();

}

function uploadWAVFile(blob) {
    var input = document.createElement('input');
    input.type = "file";
    var filename = new Date().toISOString();

    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    fd.append("stage", stage);
    fd.append("feature", current_feature);
    fd.append("contains_audio","true");
    fd.append("audio_data", blob, filename + '.wav');
    xhr.onreadystatechange = function () {
        if (this.readyState == 4) {
            // console.log(times);
            if (JSON.parse(xhr.responseText)["continue"] == "YES") {
                if (JSON.parse(xhr.responseText)["listen"] == "YES") {
                    document.getElementById("mic-box").style.pointerEvents = "none";
                    document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
                    recordMode(10000);
                }
                else {
                    if (JSON.parse(xhr.responseText)['error'] == "YES") {
                        reset();
                    }
                    recordMode(1500);
                }
            }
            else {
                interrupt = "yes";
                ProcessMode();
            }
        }
    };
    xhr.open("POST", "http://127.0.0.1:5000/process", true);
    if (interrupt == "no") {
        xhr.send(fd);
    }
    // ProcessMode();

}