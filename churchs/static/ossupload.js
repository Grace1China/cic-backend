function UploaderFactory(

    pbrowse_button = 'selectfiles',  
    pcontainer = 'container',
    possfile = 'ossfile',
    ppostfiles = 'postfiles',
    pconsole = 'console',
    pmyradio = 'myradio',
    pfileurl = 'fileurl',
    pacl = 'private'
    // pwidget_div = 'widget_div'

) {
    var loc_browse_button = pbrowse_button
    var loc_container = pcontainer
    var loc_ossfile = possfile //用来显示链接
    var loc_postfiles = ppostfiles //没有什么作用，下次删除
    var loc_console = pconsole //显示错误信息
    var loc_myradio = pmyradio
    var loc_fileurl = pfileurl //用来上传form里
    var loc_acl = pacl
    // var loc_widget_div = pwidget_div
    var max_file_size = '8gb'
    
    var accessid = ''
    var accesskey = ''
    var sourhost = ''
    var desthost = ''
    var policyBase64 = ''
    var signature = ''
    var callbackbody = ''
    var filename = ''
    var key = ''
    var expire = 0
    var g_object_name = ''
    var g_object_name_type = ''
    var now = timestamp = Date.parse(new Date()) / 1000; 

    
    function send_request()
    {
        var xmlhttp = null;
        if (window.XMLHttpRequest)
        {
            xmlhttp=new XMLHttpRequest();
        }
        else if (window.ActiveXObject)
        {
            xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
        }
    
        if (xmlhttp!=null)
        {
            // serverUrl是 用户获取 '签名和Policy' 等信息的应用服务器的URL，请将下面的IP和Port配置为您自己的真实信息。
            serverUrl = `/rapi/alioss_directup_signature`
            
            xmlhttp.open( "GET", serverUrl, false );
            xmlhttp.send( null );
            return xmlhttp.responseText
        }
        else
        {
            alert("Your browser does not support XMLHTTP.");
        }
    };


    function check_object_radio() {
        var tt = loc_myradio;
        for (var i = 0; i < tt.length ; i++ )
        {
            if(tt[i].checked)
            {
                g_object_name_type = tt[i].value;
                break;
            }
        }
    }

    function get_signature()
    {
        // 可以判断当前expire是否超过了当前时间， 如果超过了当前时间， 就重新取一下，3s 作为缓冲。
        now = timestamp = Date.parse(new Date()) / 1000; 
        if (expire < now + 3)
        {
            res = send_request()
            res = JSON.parse(res)
            token = JSON.parse(res.token)
            // var obj = eval ("(" + body + ")");
            sourhost = token.host//obj['host']
            desthost = token.desthost
            policyBase64 = token.policy//obj['policy']
            accessid = token.accessid//obj['accessid']
            signature = token.signature//obj['signature']
            expire = parseInt(token.expire)//parseInt(obj['expire'])
            callbackbody = token.callback//obj['callback'] 
            key = token.dir//obj['dir']
            return true;
        }
        return false;
    };

    // function random_string(len) {
    // 　　len = len || 32;
    // 　　var chars = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678';   
    // 　　var maxPos = chars.length;
    // 　　var pwd = '';
    // 　　for (i = 0; i < len; i++) {
    //     　　pwd += chars.charAt(Math.floor(Math.random() * maxPos));
    //     }
    //     return pwd;
    // }

    function get_suffix(filename) {
        pos = filename.lastIndexOf('.')
        suffix = ''
        if (pos != -1) {
            suffix = filename.substring(pos)
        }
        return suffix;
    }

    function calculate_object_name(filename)
    {
        // if (g_object_name_type == 'local_name')
        // {
        g_object_name += "${filename}"
        // }
        // else if (g_object_name_type == 'random_name')
        // {
        //     suffix = get_suffix(filename)
        //     g_object_name = key + random_string(10) + suffix
        // }
        return ''
    }

    // function get_uploaded_object_name(filename)
    // {
    //     // if (g_object_name_type == 'local_name')
    //     // {

    //     tmp_name = g_object_name
    //     tmp_name = tmp_name.replace("${filename}", filename);
    //     return tmp_name
    //     // }
    //     // else if(g_object_name_type == 'random_name')
    //     // {
    //     //     return g_object_name
    //     // }
    // }

    // function get_bucket_url(filename){
    //     suffix = get_suffix(filename)
    //     return suffix.toLowerCase() != '.mp4' ? desthost:sourhost
    // }

    function set_upload_param(up, filename, ret)
    {
        if (ret == false)
        {
            ret = get_signature()
        }
        g_object_name = key;
        suffix = get_suffix(filename)

        if (filename != '') { 
            calculate_object_name(filename)
        }
        // that = this
        new_multipart_params = {
            'key' : g_object_name,
            'policy': policyBase64,
            'OSSAccessKeyId': accessid, 
            'success_action_status' : '200', //让服务端返回200,不然，默认会返回204
            'callback' : callbackbody,
            'signature': signature,
            'x-oss-object-acl':loc_acl.value
        };
        console.log('----------set_upload_param-----------')
        console.log(new_multipart_params)
        up.setOption({
            'url':(suffix.toLowerCase() == '.mp4' || suffix.toLowerCase() == '.mov' || suffix.toLowerCase() == '.m4v' ) ? sourhost:desthost,
            'multipart_params': new_multipart_params
        });

        up.start();
    }

    function decodeFileN(key){
        console.log(`encode filename${key}`)
        arr = key.split('/')
        return arr[0]+'/'+encodeURI(arr[1])
    }

   

    return function get_one_uploader(){
        // var upload_config = this
        //当外部得到本函数时，就得到五个闭包。这个函数里面的对像，可以访问本函数外部的作用域。就是这. 这样每个uploader都可以访问一个单独的组件配置。
        var uploader =  new plupload.Uploader({
            runtimes : 'html5,flash,silverlight,html4',
            browse_button : loc_browse_button, 
            //multi_selection: fa           se,
            container: loc_container,
            // flash_swf_url : 'lib/plupload-2.1.2/js/Moxie.swf',
            // silverlight_xap_url : 'lib/plupload-2.1.2/js/Moxie.xap',
            url : 'http://oss.aliyuncs.com',
        
            filters: {
                mime_types : [ //只允许上传图片和zip文件
                { title : "Image files", extensions : "jpg,gif,png,bmp"}, 
                { title : "Zip files", extensions : "zip,rar"},
                { title : "mp4 files", extensions : "mp4,mov,m4v"},
                { title : "mp3 files", extensions : "mp3"},
                { title : "document files", extensions : "pdf,doc,docx,txt"}

        
                ],
                max_file_size : max_file_size, //最大只能上传10mb的文件
                prevent_duplicates : true //不允许选取重复文件
            },
        
            init: {
                PostInit: function() {
                    loc_ossfile.innerHTML = '';
                    // loc_postfiles.onclick = function() {
                    // set_upload_param(uploader, '', false);
                    // return false;
                    // };
                },
        
                FilesAdded: function(up, files) {
                    plupload.each(files, function(file) {
                        loc_ossfile.innerHTML += '<div id="' + file.id + '">' + file.name + ' (' + plupload.formatSize(file.size) + ')<b></b>'
                        +'<div class="progress"><div class="progress-bar" style="width: 0%"></div></div>'
                        +'</div>';
                        set_upload_param(uploader, file.name, false);
                    });
                },
        
                BeforeUpload: function(up, file) {
                    
                    check_object_radio();
                    set_upload_param(up, file.name, true);
                },
        
                UploadProgress: function(up, file) {
                    var d = document.getElementById(file.id);
                    d.getElementsByTagName('b')[0].innerHTML = '<span>' + file.percent + "%</span>";
                    var prog = d.getElementsByTagName('div')[0];
                    var progBar = prog.getElementsByTagName('div')[0]
                    progBar.style.width= 2*file.percent+'px';
                    progBar.setAttribute('aria-valuenow', file.percent);
                },
        
                FileUploaded: function(up, file, info) {
                    // filename = file.name.replace(' ','')
                    console.log(file)
                    console.log(info)
                    console.log(up)
                    res = JSON.parse(info.response)
                    console.log(res.signedurl)
                    console.log(res)

                    if (info.status == 200)
                    {
                        document.getElementById(file.id).getElementsByTagName('b')[0].innerHTML = `<a href="${(res.signedurl)}">${(res.filename)}</a>`     
                        loc_fileurl.value =`${(res.filename)}`//key
                        loc_ossfile.href =`${(res.signedurl)}`//签名url
                        loc_ossfile.innerText  =`${(res.filename)}`

                        if ((document.getElementsByName('title')[0].value||'')==''){
                            var thefn = res.filename.replace(/^.*\//g,'').replace(/\..*$/,'')//这里是为了去掉目录和文件扩展名
                            document.getElementsByName('title')[0].value = (thefn)
                        }
                        // document.getElementsByName('_continue')[0].click()
                    }
                    else if (info.status == 203)
                    {
                        document.getElementById(file.id).getElementsByTagName('b')[0].innerHTML = '上传到OSS成功，但是oss访问用户设置的上传回调服务器失败，失败原因是:' + info.response;
                    }
                    else
                    {
                        document.getElementById(file.id).getElementsByTagName('b')[0].innerHTML = info.response;
                    } 
                },
        
                Error: function(up, err) {
                    if (err.code == -600) {
                        loc_console.appendChild(document.createTextNode(`\n选择的文件太大了,不能超过${max_file_size}`));
                    }
                    else if (err.code == -601) {
                        loc_console.appendChild(document.createTextNode("\n选择的文件后缀不对，必须是jpg,gif,png,bmp,mp4,mp3"));
                    }
                    else if (err.code == -602) {
                        loc_console.appendChild(document.createTextNode("\n这个文件已经上传过一遍了"));
                    }
                    else 
                    {
                        loc_console.appendChild(document.createTextNode("\nError xml:" + err.response));
                    }
                }
            }
        });
        return uploader
    }
    
  }

