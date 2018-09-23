
let baggage_webcam = (()=>{
    let obj = {}
    let cams = []

    obj.initScanner = ()=>{
        Instascan.Camera.getCameras().then(function (cameras) {
            if (cameras.length > 0) {
                cams = cameras
                console.log(cams)
            } else {
                console.error('No cameras found.');
            }
        }).catch(function (e) {
            console.error(e);
        });
    }
    
    obj.initListeners = ()=>{
        $(window).on("load", function(){
	    obj.imageScan()
        })
        $("#baggage-form").on("submit", (ev)=>{
            obj.capture()
        })
    }

    //Opens a popup with a camera preview. If a QR is detected,
    //it's value is set into 'inputElem'. 
    //Clicking the bg cancels the operation
    //pre: call initScanner
    obj.imageScan = ()=>{
        if(!cams) console.error("I can't scan without a camera")
        if(!localStorage.getItem("selectedCam"))
            localStorage.setItem("selectedCam", 0)

        let selectedCam = parseInt(localStorage.getItem("selectedCam"))
        //Create video element for camera output
        let videoElem = document.createElement('video')
	videoElem.id = "baggage-scan-video"
        //Init scanner with this element
        let scanner = new Instascan.Scanner({ video: videoElem });
        camerainput = document.getElementById("baggage-scan-image")
        camerainput.classList.add("baggage-inside-scan")
        //Append camera selector
        let selectCam = document.createElement("select")
	selectCam.classList.add("form-control")
        let optionsStr=""
        for(let i =0; i < cams.length; i++)
            optionsStr += "<option value='"+i+"'>" + (cams[i].name || "Camera "+i) + "</option>"
        selectCam.innerHTML=optionsStr
        camerainput.appendChild(selectCam)
        selectCam.value = ""+selectedCam
        //On selector change, we stop the scanner preview and change the camera
        selectCam.addEventListener("change", ()=>{
            let selectedCam = parseInt(this.value)
            localStorage.setItem("selectedCam", selectedCam)
        })
        //Then we append the video preview
        camerainput.appendChild(videoElem)
        
        //Start the scanner with the stored value
        scanner.start(cams[selectedCam])
        
    }
    
    obj.capture = ()=>{
	var video = document.getElementById('baggage-scan-video');
	var canvas = document.createElement("canvas");
        document.body.appendChild(canvas);
	canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
	canvas.getContext('2d').drawImage(video, 0, 0);
        var dataURL = canvas.toDataURL("image/png");
        document.getElementById('baggage-scan-file').value = dataURL;
    }
    
    return obj
})()

document.addEventListener("DOMContentLoaded", ()=>{
    if (Instascan.Camera == null){
	var t = setInterval(obj.initListeners(), 1000)
    }
    else{
	clearInterval(t)
	baggage_webcam.initScanner()
    }
    baggage_webcam.initListeners()
})