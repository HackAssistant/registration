
let baggage_qr = (()=>{
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
    //-Updates the content
    //-Shows a toast if there's a message
    obj.processResponse = (data)=>{        
        if(data.content){
            $('#baggage-container').fadeTo(200, 0, ()=>{
                $('#baggage-container').html(data.content)
                obj.initListeners()
                //obj.initTypeaheads()
                $('#baggage-container').fadeTo(200, 1)
            })
        }
    }


    obj.initListeners = ()=>{
        $("#id_search-qr").on("click", (ev)=>{
            obj.qrScan($("#id_search")[0])
        })
    }

    //Opens a popup with a camera preview. If a QR is detected,
    //it's value is set into 'inputElem'. 
    //Clicking the bg cancels the operation
    //pre: call initScanner
    obj.qrScan = (inputElem)=>{
        if(!cams) console.error("I can't scan without a camera")
        if(!localStorage.getItem("selectedCam"))
            localStorage.setItem("selectedCam", 0)

        let selectedCam = parseInt(localStorage.getItem("selectedCam"))
        //Create video element for camera output
        let videoElem = document.createElement('video')
        //Create element to darken the rest of the page
        let veil = document.createElement("div")
        //Init scanner with this element
        let scanner = new Instascan.Scanner({ video: videoElem });
        //Once we scan a value, set the inputElem to this value and close the popup
        scanner.addListener('scan', function (content) {
            console.info("Read QR content: "+content)
            inputElem.value = content
            scanner.stop()
            popup.parentNode.removeChild(popup)
            veil.parentNode.removeChild(veil)
            popup = ""
	    document.getElementById("baggage-search").submit()
        });
        //Creating the popup
        let popup = document.createElement("div")
        popup.classList.add("baggage-popup-scan")
        //Append camera selector
        let selectCam = document.createElement("select")
        let optionsStr=""
        for(let i =0; i < cams.length; i++)
            optionsStr += "<option value='"+i+"'>" + (cams[i].name || "Camera "+i) + "</option>"
        selectCam.innerHTML=optionsStr
        popup.appendChild(selectCam)
        selectCam.value = ""+selectedCam
        //On selector change, we stop the scanner preview and change the camera
        selectCam.addEventListener("change", ()=>{
            let selectedCam = parseInt(this.value)
            localStorage.setItem("selectedCam", selectedCam)
            scanner.stop()
            scanner.start(cams[selectedCam])
        })
        //Then we append the video preview
        popup.appendChild(videoElem)
        //Append popup to document
        document.body.appendChild(popup)
        //Darken the rest of the page
        document.body.appendChild(veil)
        veil.classList.add('veil')
        //On click on the bg, cancel the operation
        veil.addEventListener("click", ()=>{
            if(popup){
                scanner.stop()
                popup.parentNode.removeChild(popup)
                veil.parentNode.removeChild(veil)
                popup = ""
            }
        })
        
        //Start the scanner with the stored value
        scanner.start(cams[selectedCam])
        
    }
    
    return obj
})()

document.addEventListener("DOMContentLoaded", ()=>{
    baggage_qr.initListeners()
    //baggage_qr.initTypeaheads()
    baggage_qr.initScanner()
})
