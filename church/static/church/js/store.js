async function getImages (context,par) {
    console.log(`getImages==============path==${par.path}=`)
    await axios.get(`http://${par.MEDIA_BROWSE_API_SERVER}/alioss_list${par.path=='/'?'/':'/'+par.path}`,{params: { 'type': 'images','marker':par.marker }})
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
          //属性lengthComputable主要表明总共需要完成的工作量和已经完成的工作是否可以被测量
          //如果lengthComputable为false，就获取不到e.total和e.loaded
          //if (e.lengthComputable) {
          //    var rate = e.loaded / e.total;  //已上传的比例= vm.uploadRate 
          percent = (e.loaded / e.total)*100
          options.uploader.onProgress({percent:percent})
          // console.log(data.vm)
          //    if (rate < 1) {
                  //这里的进度只能表明文件已经上传到后台，但是后台有没有处理完还不知道
                  //因此不能直接显示为100%，不然用户会误以为已经上传完毕，关掉浏览器的话就可能导致上传失败
                  //等响应回来时，再将进度设为100%
          //        console.log(rate)
                  // vm.uploadRate = rate;
                  // vm.uploadStyle.width = (rate *100).toFixed(2)+ '%';
          //    }
          //}
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