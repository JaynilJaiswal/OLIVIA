//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var rec; 							//Recorder.js object
var input; 							//MediaStreamAudioSourceNode we'll be recording
var duration;                       //output_audio duration

// shim for AudioContext when it's not avb. 
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

function ListeningMode() {
    document.getElementById("mic-box").style.pointerEvents = "none";
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_listening.gif)";
    recordMode();
}

function ProcessMode() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_processing.gif)";
    var xhttp = new XMLHttpRequest();
    xhttp.open('GET',"http://127.0.0.1:5000/process",false);
    do{
        sleep(1000);
        xhttp.open('POST',"http://127.0.0.1:5000/check",false);
        xhttp.send();
        // console.log(xhttp.responseText);
        var req = xhttp.responseText;
    }while(req=="no");
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
     async function fetchAudio(word) {
        const requestOptions = {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ "word": word })
        };  let url = 'http://127.0.0.1:5000/check';
        // fetch() returns a promise that
        // resolves once headers have been received
        return fetch(url, requestOptions)
          .then(res => {
            if (!res.ok)
              throw new Error(`${res.status} = ${res.statusText}`);      // response.body is a readable stream.
            // Calling getReader() gives us exclusive access to
            // the stream's content      
            var reader = res.body.getReader();
            // read() returns a promise that resolves
            // when a value has been received      
            return reader
              .read()
              .then((result) => {
                return result;
              });
          })
      }
      fetchAudio("check")
      .then((response) => {
        // response.value for fetch streams is a Uint8Array
        var blob = new Blob([response.value], { type: 'audio/x-wav' });
        var url = window.URL.createObjectURL(blob)
        window.audio = new Audio();
        window.audio.src = url;
        window.audio.load();
        window.audio.play();
      })
      .catch((error) => {
        this.setState({
            error: error.message
        });
      });
    document.getElementById("mic-box").style.pointerEvents = "auto";
}

function reset() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4-0.png)";
}

function recordMode() {

    var constraints = { audio: true, video: false }

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        console.log("getUserMedia() success, stream created, initializing Recorder.js ...");

        /*
            create an audio context after getUserMedia is called
            sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
            the sampleRate defaults to the one set in your OS for your playback device

        */
        audioContext = new AudioContext();


        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        /* 
            Create the Recorder object and configure to record mono sound (1 channel)
            Recording 2 channels  will double the file size
        */
        rec = new Recorder(input, { numChannels: 1 })

        //start the recording process
        rec.record()

        console.log("Recording started");

        setTimeout(function () {

            rec.stop();

            //stop microphone access
            gumStream.getAudioTracks()[0].stop();

            //create the wav blob and pass it on to uploadWAVFile
            rec.exportWAV(uploadWAVFile);
            //tell the recorder to stop the recording

            console.log("Recording done")

            ProcessMode();

        }, 5100);
    }).catch(function (err) { });
}

function blobToFile(theBlob, fileName) {
    //A Blob() is almost a File() - it's just missing the two properties below which we will add
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}

function uploadWAVFile(blob) {
    var input = document.createElement('input');
    input.type = "file";
    var filename = new Date().toISOString();

    // input.addEventListener("click", function(event){
    var xhr = new XMLHttpRequest();
    var fd = new FormData();
    fd.append("audio_data", blob, filename + '.wav');
    xhr.open("POST", "http://127.0.0.1:5000/process", true);

    xhr.send(fd);
    //   })
    //   $(input).click();

}