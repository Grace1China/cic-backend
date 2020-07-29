document.write("<script type='text/javascript' src='/static/church/js/axios.min.js'></script>");
document.write("<script type='text/javascript' src='/static/church/js/videojs-ie8.min.js'></script>");

async function getImages (context,par) {
  /*
  取各种媒体对象  type 是种类，page是第几页面1-based page number，series是系列的路径
  */
    host = document.location.host
    if (par.runtime =='sandbox'){
      host = par.MEDIA_BROWSE_API_SERVER
    }
    console.log(`getImages==============path==${par.series}=`)
    await axios.get(`http://${host}/alioss_list${par.series=='/'?'/':'/'+par.series}`,{params: { 'type': par.type,'page':par.page ,'series':par.series,'dkey':par.delfilekey,'skey':par.searchkey}})
    .then(function (res) {
        console.log(res)
        if (res.data.errCode == '0'){
          if(par.type == 'videos'){
            for(i=0;i<res.data.data.medias.length;i++){
              e = res.data.data.medias[i]
              console.log(e)
            }
            // for(int i= 0; i < res.data.data.length; i++){
            //   console.log(`${index}${currentValue}`)
            //   if(currentValue.video_status != 3){
            //     // ret = await dispatch('check_url',currentValue.video_tcinfo.sd) 
            //     console.log('ret')
            //   }
            // }
          }
          context.commit('setImages',res.data.data)
        }

    })
    .catch(function (err) {
      console.log(err)
    });
}

async function upload2oss (context,options) {
  
  console.log(`upload2oss=============`)
  console.log(options)
  var config = {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: function (e) {
          // console.log("进度：");
          // console.log(e);
          percent = (e.loaded / e.total)*100
          options.uploader.onProgress({percent:percent})
      }
  };
  await axios.post(options.host,options.form,config).then(function (res) {//'https://bicf-media-destination.oss-accelerate.aliyuncs.com'
      console.log(res)
      options.uploader.onSuccess()
  })
  .catch(function (err) {
    console.log(err)
    options.uploader.onError()
  });
}

// async function check_url(context,options){
//   return new Promise(function(resolve){
//     axios.get(`https://api.bicf.org/mediabase/citychurch/default/052e4d2a-7b41-5078-3043-e63b85c6d4b0/sd.mp4`)
//     .then(function (res) {
//       resolve(true)
//     })
//     .catch(function (err) {
//       resolve(false)
//     });
//   });
// }

// async function check_url(url){
//   return new Promise(function(resolve){
//       axios.get(`https://api.bicf.org/mediabase/citychurch/default/052e4d2a-7b41-5078-3043-e63b85c6d4b0/sd.mp4`)
//           .then(function(){
//               resolve(true);   
//           })
//           .catch(function(){
//               resolve(false);
//           });
//   });
// }

function getOssToken (context,options) {
  return new Promise((resolve, reject) =>{        
    console.log(`getOssToken=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.get(`http://${host}/rapi/alioss_directup_signature_v2`,{params: { 'type': options.type,'object_prefix':options.object_prefix}}).then(function (res) {//'https://bicf-media-destination.oss-accelerate.aliyuncs.com'
        console.log(res)
        resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
  });
}

function getObjByKey(context,options) {
  return new Promise((resolve, reject) =>{        
    console.log(`getObjByKey=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.get(`http://${host}/rapi/get_media_by_key`,{params: { 'typ':options.typ ,'key':options.key}}).then(function (res) {
        console.log(res)
        resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
  });
}

function deleteContent(context,options){
  return new Promise((resolve, reject) =>{        
    console.log(`deleteContent=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.get(`http://${host}/rapi/delete_content`,{params: { 'columnid':options.columnid ,'contentid':options.contentid}}).then(function (res) {
        console.log(res)
        resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
  }); 
}

function deleteParts(context,options){
  return new Promise((resolve, reject) =>{        
    console.log(`deleteParts=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.post(`http://${host}/rapi/comp_delete_parts`,{params: { 'partid':options.partid}}).then(function (res) {
        console.log(res)
        resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
  }); 
}

function getCookie (name) {
  var value = '; ' + document.cookie
  var parts = value.split('; ' + name + '=')
  if (parts.length === 2) return parts.pop().split(';').shift()
}

function addParts(context,options){
  return new Promise((resolve, reject) =>{        
    console.log(`addParts=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.request({
      url:`http://${host}/rapi/comp_add_parts`,
      method:'post',
      data:{"compid":options.compid ,"linkjsons":JSON.stringify(options.linkjsons)},
      headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json',
      },
    }).then(function (res) {
      console.log(res)
      resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
    // axios.post(`http://${host}/rapi/comp_add_parts`,{params: { 'compid':options.compid ,'linkjsons':options.linkjsons}},{headers: {'X-CSRFToken': getCookie('csrftoken')}})
  }); 
}

function ccolList(context,options){
  return new Promise((resolve, reject) =>{        
    console.log(`ccolList=============`)
    console.log(options)
    host = store.getters.getHost()
    axios.get(`http://${host}/rapi/ccolList`,{params: { }}).then(function (res) {
        console.log(res)
        resolve(res)
    })
    .catch(function (err) {
      console.log(err)
      reject(err)
    });
  }); 
}

const store = new Vuex.Store({
    state: {
      count: 0,
      images:[],
      totalmedia:0,

    },
    mutations: {
      increment (state) {
        state.count++
      },
      setImages(state, data){
        state.images = data.medias
        state.totalmedia = data.total
      },
    },
    getters: {
      // ...
      getTodoById: (state) => (id) => {
        return state.todos.find(todo => todo.id === id)
      },
      getHost: (state) => (par={}) => {
        host = document.location.host
        if (par.runtime =='sandbox'){
          host = par.MEDIA_BROWSE_API_SERVER
        }
        return host
      }
    },
    actions: {
      increment (context) {
        context.commit('increment')
      },
      
      getImages,
      upload2oss,
      getOssToken,
      getObjByKey,
      deleteContent,
      ccolList,
      deleteParts,
      addParts,
      
    }
  })