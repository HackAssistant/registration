function selectFunction(scanner, selectId) {
    function changeCam(){
        // Function called everytime select input changes from value.
        // Used to start the scanner with the selected camera.
        var x = document.getElementById(selectId).value;
        if(x !== 'null'){
            Instascan.Camera.getCameras().then(function (cameras) {
                scanner.stop();
                localStorage.setItem("camera-id", x.toString())
                scanner.start(cameras[parseInt(x)]);
            }).catch(function (e) {
                console.error(e);
            });
        }
    }
    return changeCam
}

function Scanner(videoId, selectId=null, scanFunction=null, start=false, extraOpts={}) {
    const self = this
    this.videoId = videoId
    let opts = {
        ...extraOpts,
        video: document.getElementById(videoId)
    }
    this.scanner = new Instascan.Scanner(opts);
    if (scanFunction !== null) {
        this.scanner.addListener('scan', (content) => scanFunction(content))
    }
    Instascan.Camera.getCameras().then(function (cameras) {
        if (cameras.length > 0) {
            let cameraId = localStorage.getItem("camera-id")
            if (cameraId === null) {
                cameraId = "0"
                localStorage.setItem("camera-id", cameraId)
            }
            if (selectId !== null) {
                let select = document.getElementById(selectId)
                for (let c = 0; c < cameras.length; c++) {
                    let option = document.createElement('option');
                    option.innerText = cameras[c].name;
                    option.value = c;
                    select.appendChild(option);
                }
                select.value = parseInt(cameraId)
                select.onchange = selectFunction(self.scanner, selectId);
            }
            if (start) {
                self.scanner.start(cameras[cameraId])
            }
        } else {
            console.error('No cameras found.');
        }
    }).catch(function (e) {
        console.error(e);
    });
}

Scanner.prototype.start = function () {
    const self = this
    Instascan.Camera.getCameras().then(function (cameras) {
        if (cameras.length > 0) {
            let cameraId = localStorage.getItem("camera-id")
            if (cameraId === null) {
                cameraId = "0"
                localStorage.setItem("camera-id", cameraId)
            }
            self.scanner.start(cameras[parseInt(cameraId)])
        }
    })
}

Scanner.prototype.stop = function () {
    this.scanner.stop()
}

Scanner.prototype.addPhotoToForm = function (formId, inputId) {
    const self = this
    $(`#${formId}`).on("submit", (ev)=>{
        var video = document.getElementById(self.videoId);
	    var canvas = document.createElement("canvas");
        document.body.appendChild(canvas);
	    canvas.width  = video.videoWidth;
        canvas.height = video.videoHeight;
	    canvas.getContext('2d').drawImage(video, 0, 0);
        document.getElementById(inputId).value = canvas.toDataURL("image/png");
    })
}
