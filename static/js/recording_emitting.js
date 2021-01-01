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
    ProcessMode();
}

function ProcessMode() {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_processing.gif)";
}

function SpeakingMode(play) {
    document.body.style.backgroundImage = "url(../static/images/VA_anim4_speaking.gif)";
    console.log(play);      
    if (play==1){
        var output_aud = document.getElementById('output_voice');
        output_aud.src="../static/Audio_output_files/result.wav";
        output_aud.addEventListener('loadedmetadata', function(){
            duration = output_aud.duration;
            output_aud.muted-false;
            output_aud.play();
            console.log("The duration of the song is of: " + duration + " seconds");
        },false);
        console.log("play")
    }  
    setTimeout(reset, document.getElementById("output_voice").duration);
}

function reset() {
    window.location = "http://127.0.0.1:5000/";
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

        }, 5100);
    }).catch(function (err) { });
}

function blobToFile(theBlob, fileName){
    //A Blob() is almost a File() - it's just missing the two properties below which we will add
    theBlob.lastModifiedDate = new Date();
    theBlob.name = fileName;
    return theBlob;
}

function uploadWAVFile(blob) {
    var input=document.createElement('input');
    input.type="file";
    var filename = new Date().toISOString();

    // input.addEventListener("click", function(event){
    var xhr=new XMLHttpRequest();
    var fd=new FormData();
    fd.append("audio_data",blob,filename+'.wav');
    xhr.open("POST","http://127.0.0.1:5000/",true);
    
    xhr.send(fd);

//   })
//   $(input).click();
    
}