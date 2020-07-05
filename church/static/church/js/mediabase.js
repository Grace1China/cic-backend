document.write("<script type='text/javascript' src='/static/church/js/axios.min.js'></script>");
var MediaBase = {
    createNew: function(pchurch='',pcurdir=''){
    　　var mediabase = {};
        mediabase.name = "MediaBase";
        mediabase.typ='images'
        // mediabase.ALIOSS_DESTINATIONS = pALIOSS_DESTINATIONS;
        mediabase.church = pchurch;
        mediabase.curdir = pcurdir;

        mediabase.S4 = function(){ 
            return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
        };
        mediabase.guid = function(){ 
            return (this.S4()+this.S4()+"-"+this.S4()+"-"+this.S4()+"-"+this.S4()+"-"+this.S4()+this.S4()+this.S4());
        };
        mediabase.getTyp = function(filetype){
            if(filetype.match('image/')){
                return 'images'
                
            }
            if(filetype.match('video/')){
                return 'videos'
            }
            if(filetype.match('audio/')){
                return 'audios'
            }
            if(filetype.match('pdf/')){
                return 'pdfs'
            }
            return 'destination'
        };
        mediabase.onSuccess = function(res){

        };
        mediabase.onProgress = function(percent){

        };
        mediabase.onError = function(err){

        };

        mediabase.upload2oss = function(options) {
            return new Promise((resolve,reject)=>{
                    console.log(`upload2oss=============`)
                    console.log(options)
                    var config = {
                        headers: { 'Content-Type': 'multipart/form-data' },
                        onUploadProgress: function (e) {
                            percent = (e.loaded / e.total)*100
                            options.uploader.onProgress({percent:percent})
                        }
                    };
                    axios.post(options.host,options.form,config).then(function (res) {
                        console.log(res)
                        options.uploader.onSuccess()
                        resolve({'data':res,'origin_url':options.origin_url,'redirect_url':options.redirect_url})
                    })
                    .catch(function (err) {
                        console.log(err)
                        options.uploader.onError()
                        reject(err)
                    });
                }
            )
            
        };

        mediabase.getOssToken = function(options) {
            return new Promise((resolve, reject) =>{        
                console.log(`getOssToken=============`)
                console.log(options)
                host = document.location.host
                axios.get(`http://${host}/rapi/alioss_directup_signature_v3`,{params: { 'type': options.type,'object_prefix':options.object_prefix}}).then(function (res) {//'https://bicf-media-destination.oss-accelerate.aliyuncs.com'
                    console.log(res)
                    resolve(res)
                })
                .catch(function (err) {
                    console.log(err)
                    reject(err)
                });
            });
        };
        mediabase.fetchOne = function(url ){
            return new Promise((resolve, reject) => {
                let xhr = new XMLHttpRequest();
                xhr.open('get', url);
                xhr.responseType = 'blob';
                xhr.onload = () => {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        var fr = new FileReader();
                        fr.onload = function(){
                            resolve({'data':this.result,'url':url});
                        };
                        fr.readAsDataURL(xhr.response); // async call
                    } else {
                        reject(xhr.statusText);
                    }
                };
                xhr.onerror = () => reject(xhr.statusText);
                xhr.send();
            });
        };
        mediabase.dataURL2File= function dataURLtoFile(dataurl, filename) {
            var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
                bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
            while(n--){
                u8arr[n] = bstr.charCodeAt(n);
            }
            return new File([u8arr], filename, {type:mime});
        };
        mediabase.fetchAndUpload = function(imgs){
            thisV = this

            return new Promise((resolve0,reject0)=>{
                console.log(imgs)
                axios.all(Array.apply(null,imgs).map(img=>{return this.fetchOne(img.src)})).then(function(reponses){
                    var files = []
                    theGuid = thisV.guid()
                    tm = new Date()
                    for(var i = 0 ; i<=reponses.length-1; i++){
                        files.push({
                            'filedata':thisV.dataURL2File(reponses[i].data,`${theGuid}_${'pasted'}_${tm.getFullYear()}/${tm.getMonth()+1}/${tm.getDate()}_${i}`),
                            'origin_url':reponses[i].url
                        })
                    }
                    console.log(files)
    
                    tokenParams ={'type':thisV.typ,'object_prefix':`${thisV.church}${(thisV.curdir||''=='')?'':'/'+thisV.curdir+'/'}`}
                    thisV.getOssToken(tokenParams).then((res)=>{
                        let theRes = res
                        console.log(files)
                        axios.all(Array.apply(null,files).map((file)=>{
                                console.log('---------getOssToken----------')
                                console.log(theRes)
                                let fd = new FormData()
                                fd.append('OSSAccessKeyId', theRes.data.token['accessid'])
                                fd.append('policy', theRes.data.token['policy'])
                                fd.append('Signature', theRes.data.token['signature'])
                                fd.append('callback', theRes.data.token['callback'])
                                fd.append('key', `${theRes.data.token['dir']}/${thisV.guid()}`)//这个是oss中的key,随机 不用这个前缀方式了L3${(this.curdir||'').length>1?'/'+this.curdir:''}/
                                fd.append('x:originname', file.filedata.name)//文件原有名称 x是自定义oss回调变量
                                fd.append('x:dest', `${thisV.typ}`)//所属的文件目标桶类型
                                fd.append('x:seriesrespath',  theRes.data.token['curDir'])
                                fd.append('x:church',  theRes.data.token['church'])
                                fd.append('file', file.filedata)
                                option = {
                                    'host':theRes.data.token['desthost'],//this is the upload host
                                    'form':fd,
                                    'uploader':thisV,
                                    'origin_url':file.origin_url,
                                    'typ':`${thisV.typ}`,
                                    'redirect_url':theRes.data.token['redirect_url']
                                }
                                return thisV.upload2oss(option)
                        })).then(function(reponses2){
                            console.log(reponses2)
                            resolve0(reponses2)
                        }).catch(err=>{
                            reject0(err)
                        })
                    })
                    console.log(reponses)
                }).catch(err=>{
                    console.log(err)
                    reject0(err)
                })
            })
        };
        mediabase.diyUpload = function(thefile){ 
            fileType = thefile.type,
            isImage = fileType.indexOf("image") != -1,
            isLt2M = thefile.size / 1024 / 1024 < 2;
            console.log('-----------diyUpload------------')
            console.log(fileType)
            thedest = this.getTyp(fileType)
            // thehost = `https://${this.ALIOSS_DESTINATIONS[thedest=='videos'?`${thedest}.source`:thedest]['bucket']}.${this.ALIOSS_DESTINATIONS[thedest=='videos'?`${thedest}.source`:thedest]['endpoint.acc']}`

            // console.log(`dest:${thedest};host:${thehost}`)
            
            tokenParams ={'type':thedest,'object_prefix':`${this.church}${(this.curdir||''=='')?'':'/'+this.curdir+'/'}`}
            thisV = this
            this.getOssToken(tokenParams).then((res)=>{
                console.log('---------getOssToken----------')
                console.log(res)
                let fd = new FormData()
                fd.append('OSSAccessKeyId', res.data.token['accessid'])
                fd.append('policy', res.data.token['policy'])
                fd.append('Signature', res.data.token['signature'])
                fd.append('callback', res.data.token['callback'])
                fd.append('key', `${res.data.token['dir']}/${thisV.guid()}`)//这个是oss中的key,随机 不用这个前缀方式了L3${(this.curdir||'').length>1?'/'+this.curdir:''}/
                fd.append('x:originname', thefile.name)//文件原有名称 x是自定义oss回调变量
                fd.append('x:dest', `${thedest}`)//所属的文件目标桶类型
                fd.append('x:seriesrespath',  res.data.token['curDir'])
                fd.append('x:church',  res.data.token['church'])
                fd.append('file', thefile)
                option = {
                    'host':res.data.token['desthost'],//this is the upload host
                    'form':fd,
                    'uploader':thisV
                }
                thisV.upload2oss(option)
            })
        }
    　　return mediabase;
    }
};
        
        
        
    //     var MediaBase = {

    // 　　　　name: "MediaBase",
    //        ALIOSS_DESTINATIONS:{},
    //        church:'',
    //        curdir:'',
    
    //         S4: function(){ 
    //             return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
    //         },
    //         guid: function(){ 
    //             return (this.S4()+this.S4()+"-"+this.S4()+"-"+this.S4()+"-"+this.S4()+"-"+this.S4()+this.S4()+this.S4());
    //         },
    //         getTyp(filetype){
    //             if(filetype.match('image/')){
    //                 return 'images'
                    
    //             }
    //             if(filetype.match('video/')){
    //                 return 'videos'
    //             }
    //             if(filetype.match('audio/')){
    //                 return 'audios'
    //             }
    //             if(filetype.match('pdf/')){
    //                 return 'pdfs'
    //             }
    //             return 'destination'
    //         },
    //         diyUpload: function(params){ 
    //             const thefile = params.file,
    //             fileType = thefile.type,
    //             isImage = fileType.indexOf("image") != -1,
    //             isLt2M = thefile.size / 1024 / 1024 < 2;
    //             console.log('-----------diyUpload------------')
    //             console.log(fileType)
    //             thedest = this.getTyp(fileType)
    //             thehost = `https://${ALIOSS_DESTINATIONS[thedest=='videos'?`${thedest}.source`:thedest]['bucket']}.${ALIOSS_DESTINATIONS[thedest=='videos'?`${thedest}.source`:thedest]['endpoint.acc']}`
        
    //             console.log(`dest:${thedest};host:${thehost}`)
                
    //             tokenParams ={'type':thedest,'object_prefix':`${church}${(curdir||''=='')?'':'/'+curdir+'/'}`}
    //             thisC = this
    //             store.dispatch('getOssToken',tokenParams).then((res)=>{
    //                 console.log('---------getOssToken----------')
    //                 console.log(res)
        
    //                 let fd = new FormData()
    //                 fd.append('OSSAccessKeyId', res.data.token['accessid'])
    //                 fd.append('policy', res.data.token['policy'])
    //                 fd.append('Signature', res.data.token['signature'])
    //                 fd.append('callback', res.data.token['callback'])
    //                 fd.append('key', `${church}/${curdir}/${thisC.guid()}`)//这个是oss中的key,随机 不用这个前缀方式了L3${(this.curdir||'').length>1?'/'+this.curdir:''}/
    //                 fd.append('x:originname', thefile.name)//文件原有名称 x是自定义oss回调变量
    //                 fd.append('x:dest', `${thedest}`)//所属的文件目标桶类型
    //                 fd.append('x:seriesrespath', `${ curdir }`)
    //                 fd.append('x:church', `${ church }`)
    //                 fd.append('file', thefile)
    //                 option = {
    //                     'host':thehost,
    //                     'form':fd,
    //                     'uploader':params
    //                 }
    //                 store.dispatch('upload2oss',option)
    //             })
    //         }
    
    // 　　};
    
    
    
    