//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording
var duration;                       //output_audio duration

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

feature_just_selected = "";

window.onload = function(){

    welcomeMessage = document.getElementById('default-messages'); 
    
    var xhttp = new XMLHttpRequest();
    
    xhttp.open('POST', encodeURI('http://127.0.0.1:5000/getWelcomeMessage'));
    xhttp.setRequestHeader('Content-Type', 'application/json');
    xhttp.responseType = 'blob';
    xhttp.onload = function(evt) {
        var blob = new Blob([xhttp.response], {type: 'audio/wav'});
        var objectUrl = URL.createObjectURL(blob);
    
        welcomeMessage.src = objectUrl;
        // Release resource when it's loaded
        welcomeMessage.onload = function(evt) {
            URL.revokeObjectURL(objectUrl);     
        };
        welcomeMessage.load();
        welcomeMessage.play();  
    };
    xhttp.send();
}


function ListeningMode() {
    document.getElementById("mic-box").style.pointerEvents = "none";
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
    recordMode();
}

function ProcessMode() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_processing.gif)";
    var xhttp = new XMLHttpRequest();
    var req = "no";
    // xhttp.open('GET',"http://127.0.0.1:5000/check",false);
    do{
        sleep(1000);
        xhttp.open('GET',"http://127.0.0.1:5000/check_audio_available",false);
        xhttp.send();
        req = xhttp.responseText;
    }while(req=="no");
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
    xhttp.onload = function(evt) {
        var blob = new Blob([xhttp.response], {type: 'audio/wav'});
        var objectUrl = URL.createObjectURL(blob);

        output_aud.src = objectUrl;
        // Release resource when it's loaded
        output_aud.onload = function(evt) {
            URL.revokeObjectURL(objectUrl);     
        };
        output_aud.load();
        output_aud.play();  
    };
    xhttp.send();

    var xhtp = new XMLHttpRequest();
    xhtp.open('GET',"http://127.0.0.1:5000/getfeature_name",false);
    xhtp.send();
    feature_just_selected = xhtp.responseText;

    additional_request(feature_just_selected.split(", "),output_aud.duration);
    // var xhr = new XMLHttpRequest();
    // xhttp.responseType = 'text';
    // var req = "stay";

    // do{
    //   xhr.open('GET',"http://127.0.0.1:5000/fetch_output_audio",true);
    //     xhr.send();
    //     req = xhr.responseText;
    // }while(req != "output file removed")

    // if (req == "output file removed"){reset();}
    
}

function additional_request(feature_just_selected,duration_sleep)
{
    // sleep(duration_sleep*1000)

    for(i=0;i<feature_just_selected.length;i++)
    {
        if (feature_just_selected[i] == "music"){

            document.getElementById('music-modal').style.display = "block";
            // document.body.style.backgroundImage = "url(../static/images/VA_anim4_speaking.gif)";
            console.log("music feature");

            //fetching music name and thumbnail url
            var xhtp = new XMLHttpRequest();
            xhtp.open('GET',"http://127.0.0.1:5000/getMusicDetails_toShow",false);
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
            xhttp.onload = function(evt) {
                var blob = new Blob([xhttp.response], {type: 'audio/m4a'});
                var objectUrl = URL.createObjectURL(blob);
    
                music_player.src = objectUrl;
                // music_player.style = "display: inline-block";
                // Release resource when it's loaded
                music_player.onload = function(evt) {
                    URL.revokeObjectURL(objectUrl);     
                };
                music_player.load();
                music_player.play();  
            };
            xhttp.send();

            //display modal
        }
    }

    var xhtp = new XMLHttpRequest();
    xhtp.open('GET',"http://127.0.0.1:5000/check_audio_available",false);
    xhtp.send();
    feature_just_selected = xhtp.responseText;
    reset();
}

function reset() {
    document.getElementById("mic-box").style.pointerEvents = "auto";
    document.body.style.backgroundImage = "url(../static/images/VA_anim4-0.png)";
}

function recordMode() {

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

            rec.exportWAV(uploadWAVFile);

            console.log("Recording done")

        }, 5100);
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

function uploadWAVFile(blob) {
    var input = document.createElement('input');
    input.type = "file";
    var filename = new Date().toISOString();

    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    fd.append("audio_data", blob, filename + '.wav');
    xhr.open("POST", "http://127.0.0.1:5000/process", true);

    xhr.send(fd);

    ProcessMode();

}