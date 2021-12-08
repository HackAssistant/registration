let hw = (()=>{
    let obj = {}
    obj.canNotify = false
    //Sends an ajax request using POST
    //The response must be an html string
    obj.ajax_req = (data, cb, cberr)=>{
        data['csrfmiddlewaretoken'] = window.CSRF_TOKEN
        success= cb || function(){}
        error = cberr || function(){}
        $.ajax({
            method: 'POST',
            data: data,
            success: success,
            error: error
        })
    }

    obj.toast = (msg)=>{
        $.snackbar({
            content: msg,
            timeout: 3000
        })
    }

    obj.pad =(num)=>{
        return (''+num).length == 1 ? '0'+num : num
    }

    //Checks wether the browser is 
    //compatible and asks for permission
    obj.initNotifications =(cb)=>{
        if(!("Notification" in window)) return
        //if(Notification.permission === 'denied') return

        Notification.requestPermission((permission)=>{
            if(permission === 'granted')
                obj.canNotify = true

            if(cb) cb(obj.canNotify)
        })
    }

    //Makes a desktop notification
    //This function should be preceded 
    //by a call to initNotifications
    obj.notify = (msg_in, title_in, icon, cb, time)=>{
        if(!obj.canNotify) return 
        let msg = msg_in || ""
        let title = title_in || "HackathonAssistant"
        let closeIn = time || 10000
        var icon = icon || window.location.origin + "/static/favicon.png"
        let notification = new Notification(title, {
            body: msg,
            icon: icon
        })

        let timer = setTimeout(()=>{
            notification.close()
        }, closeIn)

        notification.onclick = ()=>{
            if(cb) cb()
            clearTimeout(timer)
            notification.close()
        }
    }

    //davidwalsh.name
    obj.debounce = function(func, wait, immediate){
        let timeout;
        return function(){
            let context = this, args = arguments
            var later = function(){
                timeout = null
                if (!immediate) func.apply(context, args)
            }
            var callNow = immediate && !timeout
            clearTimeout(timeout)
            timeout = setTimeout(later, wait)
            if(callNow) func.apply(context, args)
        }
    }

    return obj
})()
