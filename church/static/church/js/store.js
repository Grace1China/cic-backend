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
      
    }
  })