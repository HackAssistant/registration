
let meals_webcam = (()=>{
    let obj = {}
    let cams = []

    // Set up AJAX request
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    obj.initScanner = ()=>{
        Instascan.Camera.getCameras().then(function (cameras) {
            if (cameras.length > 0) {
                cams = cameras

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
    }

    //Opens a popup with a camera preview. If a QR is detected,
    //it's value is set into 'inputElem'.
    //Clicking the bg cancels the operation
    //pre: call initScanner
    obj.imageScan = ()=>{
        if(!cams) console.error("I can't scan without a camera")



        //Create video element for camera output
        let videoElem = $('#meals-scan-video')[0]

        //Init scanner with this element
        let scanner = new Instascan.Scanner({ video: videoElem });
        scanner.addListener('scan', function (content) {
            let meal = $('#meals-scan-image').data('mealid')
            let url = $('#meals-scan-image').data('apiurl')
            scanner.stop()
            $.post( url, { meal_id: meal, qr_id: content }).done(function( data ) {
                if (data.hasOwnProperty("error")){
                    alert('Error: '+ data.error)
                } else {
                    alert('Diet:'+data.diet)
                }
                let selectedCam = parseInt(selectCam.val())
                scanner.start(cams[selectedCam])
            })



            // Todo: add call to post and show window
        });

        //Append camera selector
        let selectCam = $('#meals-scan-image select')


        for(let i =0; i < cams.length; i++)
            selectCam.append("<option value='"+i+"'>" + (cams[i].name || "Camera "+i) + "</option>")

        if(!localStorage.getItem("selectedCam"))
            localStorage.setItem("selectedCam", 0)
        let selectedCam = parseInt(localStorage.getItem("selectedCam"))
        //Fix if selectedCam is NaN
        if (isNaN(selectedCam)){
            selectedCam = 0
            localStorage.setItem("selectedCam", 0)
        }

        selectCam.value = ""+selectedCam

        //On selector change, we stop the scanner preview and change the camera
        selectCam[0].addEventListener("change", ()=>{
            let selectedCam = parseInt(selectCam.val())
            localStorage.setItem("selectedCam", selectedCam)
            scanner.stop()
            scanner.start(cams[selectedCam])
        })
        //Start the scanner with the stored value
        scanner.start(cams[selectedCam])

    }

    return obj
})()

document.addEventListener("DOMContentLoaded", ()=>{
    if (Instascan.Camera == null){
	    var t = setInterval(obj.initListeners(), 1000)
    }
    else{
        clearInterval(t)
        meals_webcam.initScanner()
    }
    meals_webcam.initListeners()
})
