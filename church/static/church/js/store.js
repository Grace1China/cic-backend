async function getImages (context,par) {
    host = document.location.host
    if (par.runtime =='sandbox'){
      host = par.MEDIA_BROWSE_API_SERVER
    }
    console.log(`getImages==============path==${par.series}=`)
    await axios.get(`http://${host}/alioss_list${par.series=='/'?'/':'/'+par.series}`,{params: { 'type': par.type,'page':par.page ,'series':par.series}})
    .then(function (res) {
        console.log(res)
        if (res.data.errCode == '0'){
            context.commit('setImages', res.data.data)
            // console.log(context.state.menues)
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
          console.log(e);
          percent = (e.loaded / e.total)*100
          options.uploader.onProgress({percent:percent})
      }
  };
  await axios.post('https://bicf-media-destination.oss-accelerate.aliyuncs.com',options.f,config).then(function (res) {
      console.log(res)
      options.uploader.onSuccess()
  })
  .catch(function (err) {
    console.log(err)
    options.uploader.onError()
  });
}

const store = new Vuex.Store({
    state: {
      count: 0,
      images:[],

    },
    mutations: {
      increment (state) {
        state.count++
      },
      setImages(state, pimages){
        state.images = pimages
      }
    },
    actions: {
      increment (context) {
        context.commit('increment')
      },
     
      getImages,
      upload2oss,
      
    }
  })