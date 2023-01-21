function Scanner(videoId, scanFunction=null, extraOpts={}) {
    const self = this
    this.videoId = videoId
    this.popup = extraOpts.popup ?? false
    let opts = {
        maxScansPerSecond: 4,
        highlightScanRegion: scanFunction !== null,
        ...extraOpts,
    }
    let video = $(`#${videoId}`)
    if (this.popup) {
        video.wrap('<div id="video-scan-all" style="display: none; position: relative; overflow: hidden; border-radius: 5px" class="mt-4 bg-primary">')
    } else {
        video.wrap('<div id="video-scan-all" style="display: none; position: relative; overflow: hidden; border-radius: 5px; width: 100%" class="mt-2 bg-primary">')
    }
    video.after('<i id="toggle-flash" class="fa fa-bolt fs-1" style="display: none; position: absolute; z-index: 1252; right: 3%; top: 3%; cursor: pointer; font-size: xx-large;"></i>')
    video.after('<i id="toggle-cam" class="fa fa-repeat fs-1" style="display: none; position: absolute; z-index: 1252; right: 3%; bottom: 3%; cursor: pointer; font-size: xx-large;"></i>')
    video.show()
    if (this.popup) {
        let video_wrap = video.parent()
        video_wrap.before('<div class="row m-0 mt-3">' +
    '                          <div class="col-2 text-start"><h2><i id="close-button" class="fa fa-arrow-left" style="cursor: pointer"></i></h2></div>' +
    `                          <div class="col-8"><h2>${extraOpts.popup_title ?? 'QR scanner'}</h2></div>` +
    '                      </div>')
        let all = $.merge(video_wrap.prev(), video_wrap)

        all.wrapAll(`<div id="popup-scan-container" class="${extraOpts.popup_class ?? ''} p-2 col-lg-4 mt-lg-5 text-center">`).first().parent()
            .wrap('<div class="row justify-content-center m-0">').parent()
            .wrap('<div id="popup-scan" display: none">')

        $(document).on('keyup', function(e) {
            if (e.key === "Escape") self.hide()
        })
        const div = document.createElement('div')
        div.style = 'display: none;'
        div.className = 'veil'
        div.id = 'veil'
        document.body.appendChild(div)
        $('#close-button').on('click', () => {self.hide()})
        $('#popup-scan').on('click', () => {self.hide()})
        $('#popup-scan-container').on('click', (e) => e.stopPropagation())
    }
    this.scanner = new QrScanner(video.get(0), scanFunction, opts)
    let flash = $('#toggle-flash')
    flash.on('click', () => {
        self.scanner.toggleFlash()
    })
    QrScanner.listCameras(true).then(function (cameras) {
        if (cameras.length > 0) {
            let cameraId = localStorage.getItem("camera-id")
            if (cameraId === null || cameraId === undefined) {
                cameraId = "0"
                localStorage.setItem("camera-id", cameraId)
            }
            let camera_choices = ['environment', 'user']
            self.scanner.setCamera(camera_choices[parseInt(cameraId)])
            if (cameras.length > 1) {
                let toggle_cam = $('#toggle-cam')
                toggle_cam.show()
                let switcher = {0: "1", 1: "0"}
                toggle_cam.on('click', () => {
                    cameraId = switcher[cameraId] ?? "0"
                    localStorage.setItem("camera-id", cameraId)
                    self.scanner.setCamera(camera_choices[parseInt(cameraId)])
                })
            }
        } else {
            console.error('No cameras found.');
        }
    }).catch(function (e) {
        console.error(e);
    });
}

Scanner.prototype.start = function () {
    this.scanner.hasFlash().then((response) => {
        let flash = $('#toggle-flash')
        if (response) flash.show()
        else flash.hide()
    })
    this.scanner.start()
}

Scanner.prototype.stop = function () {
    this.scanner.stop()
}

Scanner.prototype.show = function () {
    $('#video-scan-all').css('display', 'inline-block')
    $('#popup-scan').show()
    $('#veil').show()
    this.start()
}

Scanner.prototype.hide = function () {
    $('#video-scan-all').hide()
    $('#popup-scan').hide()
    $('#veil').hide()
    this.stop()
}

Scanner.prototype.addPhotoToForm = function (triggerId, inputId, reloadId=null) {
    const self = this
    function save_image(ev, pause) {
        let video = document.getElementById(self.videoId);
	    self.canvas = document.createElement("canvas");
        self.canvas.style.display = "none"
        document.body.appendChild(self.canvas);
	    self.canvas.width  = video.videoWidth;
        self.canvas.height = video.videoHeight;
	    self.canvas.getContext('2d').drawImage(video, 0, 0);
        document.getElementById(inputId).value = self.canvas.toDataURL("image/png");
        self.scanner.stop()
        if (pause) {
            $(video).css("background-image", "url(" + self.canvas.toDataURL("image/png") + ")").css('background-size', 'cover')
        }
    }
    let trigger = $(`#${triggerId}`)
    if (trigger.is('form')) {
        trigger.on('submit', (ev) => {save_image(ev, false)})
    } else {
        trigger.on('click', (ev) => {save_image(ev, true)})
        if (reloadId !== null) {
            $(`#${reloadId}`).on('click', () => {
                self.scanner.start()
            })
        }
    }
}
