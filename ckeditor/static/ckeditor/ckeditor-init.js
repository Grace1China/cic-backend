/* global CKEDITOR */
document.write("<script type='text/javascript' src='/static/church/js/mediabase.js'></script>");
;(function() {
  var el = document.getElementById('ckeditor-init-script');
  if (el && !window.CKEDITOR_BASEPATH) {
    window.CKEDITOR_BASEPATH = el.getAttribute('data-ckeditor-basepath');
  }

  // Polyfill from https://developer.mozilla.org/en/docs/Web/API/Element/matches
  if (!Element.prototype.matches) {
    Element.prototype.matches =
        Element.prototype.matchesSelector ||
        Element.prototype.mozMatchesSelector ||
        Element.prototype.msMatchesSelector ||
        Element.prototype.oMatchesSelector ||
        Element.prototype.webkitMatchesSelector ||
        function(s) {
            var matches = (this.document || this.ownerDocument).querySelectorAll(s),
                i = matches.length;
            while (--i >= 0 && matches.item(i) !== this) {}
            return i > -1;
        };
  }

  function dataURLtoFile(dataurl, filename) {
    var arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
  }

  function toDataURL(url, callback){
      var xhr = new XMLHttpRequest();
      xhr.open('get', url);
      xhr.responseType = 'blob';
      xhr.onload = function(){
      var fr = new FileReader();
          fr.onload = function(){
              callback(this.result);
          };
          fr.readAsDataURL(xhr.response); // async call
      };
      xhr.send();
  }

  function runInitialisers() {
    if (!window.CKEDITOR) {
      setTimeout(runInitialisers, 100);
      return;
    }
    

    initialiseCKEditor();
    initialiseCKEditorInInlinedForms();
    CKEDITOR.on('instanceReady', function (ev) {
      ev.editor.on('paste', async function (ev) {
          // ev.data.html = ev.data.html.replace(/<img( [^>]*)?>/gi, '');
          console.log('---------------instanceReady---------------------')
          console.log(ev)
          // ev.data.html = ev.data.html.replace(/<img( [^>]*)?>/gi, '');
          ev.stop()
          // show loader that blocks editor changes


          formVue.openFullScreen2() 
          var s = ev.data.dataValue;
          var temp = document.createElement('div');
          temp.innerHTML = s;
          var htmlObject = temp;
          imgs = htmlObject.getElementsByTagName('img')
          mb = MediaBase.createNew()
          reponses =  await mb.fetchAndUpload(imgs)
          console.log(reponses)
          if(imgs.length != reponses.length){
            throw '同步的图片数量与原文档不一致'
          }
          for(var i=0; i <= imgs.length -1 ; i++){
            if(imgs[i].src != reponses[i].origin_url){
              throw `第${i}个对像的url不一致`
            }
            console.log(`https://${reponses[i].redirect_url}/${reponses[i].data.data.filename}`)
            imgs[i].src=`https://${reponses[i].redirect_url}/${reponses[i].data.data.filename}`
          }
          console.log(temp.innerHTML)
          ev.editor.insertHtml(temp.innerHTML)
          formVue.closeFullScreen2()

          // editor.insertHtml

          
          // theguid = mb.guid()
          // for(var i = 0 ; i <　imgs.length -1 ; i++){
          //   console.log(imgs[i].src);
          //   toDataURL(imgs[i].src , function(dataURL){
          //     // result.src = dataURL;
          //     // console.log(dataURLtoFile(dataURL,imgs[i].src))
          //     tm = new Date()
              
          //     file = dataURLtoFile(dataURL,`${'ckeditorpasted'}_${tm.getFullYear()}/${tm.getMonth()+1}/${tm.getDate()}_${theguid}`)
          //     mb = MediaBase.createNew()
          //     mb.diyUpload(file)
          //   });
          // }
          // ev.stop();
      });
    });
  }

  if (document.readyState != 'loading' && document.body) {
    document.addEventListener('DOMContentLoaded', initialiseCKEditor);
    runInitialisers();
  } else {
    document.addEventListener('DOMContentLoaded', runInitialisers);
  }

  function initialiseCKEditor() {
    var textareas = Array.prototype.slice.call(document.querySelectorAll('textarea[data-type=ckeditortype]'));
    for (var i=0; i<textareas.length; ++i) {
      var t = textareas[i];
      if (t.getAttribute('data-processed') == '0' && t.id.indexOf('__prefix__') == -1) {
        t.setAttribute('data-processed', '1');
        var ext = JSON.parse(t.getAttribute('data-external-plugin-resources'));
        for (var j=0; j<ext.length; ++j) {
          CKEDITOR.plugins.addExternal(ext[j][0], ext[j][1], ext[j][2]);
        }
        CKEDITOR.replace(t.id, JSON.parse(t.getAttribute('data-config')));
      }
    }
  }

  function initialiseCKEditorInInlinedForms() {
    document.body.addEventListener('click', function(e) {
      
      if (e.target && (e.target.matches('span.cke_button_icon.cke_button__image_icon') || e.target.matches('a#cke_74'))){
        e.stopPropagation()
        console.log('initialiseCKEditorInInlinedForms')

        if(e.preventDefault){
          e.preventDefault();
        }else{
          window.event.returnValue == false;
        }
        return false
      }
      if (e.target && (
        e.target.matches('.add-row a') ||
        e.target.matches('.grp-add-handler')
      )) {
        initialiseCKEditor();

      }
    });
  }

}());
