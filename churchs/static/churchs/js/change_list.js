formVue = new Vue({
            el: "#changelist-form",
            components: {
                'media-sele':{
                    components:{
                        'hovercard':{
                            data: function () {
                                return {
                                    hover: false,
                                    nstyle:{ position: 'absolute',
                                    width: '100%',
                                    height: '100%',
                                    left: '0',
                                    top: '0',
                                    cursor: 'default',
                                    textAlign: 'center',
                                    color: '#fff',
                                    opacity: '0',
                                    fontSize: '20px',
                                    backgroundColor: 'rgba(0,0,0,.5)',
                                    transition: 'opacity .3s' 
                                    },
                                    hstyle:{
                                        opacity:'1 !important'
                                    }
                                }
                            },
                            template: `
                                    <div class='extra-bar hovercard'
                                        @mouseover="hover = true"
                                        @mouseleave="hover = false"
                                        :style="[nstyle,hover ? hstyle : {}]"
                                    >
                                    <slot/>
                                    </div>
                            `
                        }
                    },
                    props: ['name','value','src','ro','ptyp'],
                    //value是key, name是控件字段 src是对像url,ro好像没有用，因为是通过setRo处理的选择媒体
   
                    data: function () {
                        return {
                            hover: false,
                            status :1,
                            src :'',
                            tcinfo :{},
                            pname: this.name,
                            pvalue: this.value,
                            pro:this.ro,
                            rosrc:undefined,
                            rokey:undefined,
                            thumb:undefined,
                            video_tcinfo:{},
                            typ:undefined,//加载后preview的时候，根据类型,默认为undefined后可取ptyp
                        }
                    },
                    computed: {
                        inputListeners: function () {
                        var vm = this
                        // `Object.assign` 将所有的对象合并为一个新对象
                        return Object.assign({},
                            // 我们从父级添加所有的监听器
                            this.$listeners,
                            // 然后我们添加自定义监听器，
                            // 或覆写一些监听器的行为
                            {
                            // 这里确保组件配合 `v-model` 的工作
                                click: function (event) {
                                    console.log(1)
                                    vm.$emit('click', event.target.value)
                                }
                            }
                        )
                        },

                        selectsrc:function(){
                            return this.ro.src
                        },
                        thevalue:function(){
                            if ((this.ro||{}).key){
                                return this.ro.key
                            }else{
                                return this.pvalue
                            }
                        }
                    },
                    watch: {
                        ro_del: {//当对像被删除时处理
                            immediate: true,    // 这句重要
                            handler (val) {
                                console.log('action Value:' )
                                console.log(val)
                                if ((val||'')==''){
                                    this.rosrc = '';
                                    this.rokey = ''
                                    this.video_tcinfo = {}
                                    this.typ = ''
                                }else{
                                    /*roo = JSON.parse(val)
                                    this.rosrc = roo.src
                                    this.rokey = roo.key
                                    this.video_tcinfo = o
                                    this.typ = o.type*/
                                }
                            }
                        }
                    },
                    mounted: function (){
                        console.log('-------mounted---media-sele')
                        console.log(this)
                        //对于以key加载的控件，重新加载一次，对于图像自动扩展url,对于video要执行一次回调
                        if (this.value == '__empty__' || this.value == ''){
                            console.log('--------return------------')
                            return
                        }

                        this.typ = this.ptyp
                        if (this.ptyp == 'images'){
                            //只需要对src进行设置
                            this.rosrc = `https://api.bicf.org/mediabase/${this.value}`
                        }else if(this.ptyp == 'videos'){
                            this.rosrc = `https://api.bicf.org/mediabase/${this.value}/00003.jpg`
                            this.video_tcinfo = {
                                audio: `https://api.bicf.org/mediabase/${this.value}/ld.mp4`,
                                hd: `https://api.bicf.org/mediabase/L3/${this.value}/hd.mp4`,
                                image1: `https://api.bicf.org/mediabase/${this.value}/00001.jpg`,
                                image2: `https://api.bicf.org/mediabase/${this.value}/00002.jpg`,
                                image3: `https://api.bicf.org/mediabase/${this.value}/00003.jpg`,
                                ld: `https://api.bicf.org/mediabase/${this.value}/ld.mp4`,
                                sd: `https://api.bicf.org/mediabase/${this.value}/sd.mp4`
                            }
                        }else if(this.ptyp == 'audios'){
                            this.rosrc = `https://api.bicf.org/mediabase/${this.value}`
                            this.thumb = '/static/church/img/audio.jpg'
                        }else if(this.ptyp == 'pdfs'){
                            this.rosrc = `https://api.bicf.org/mediabase/${this.value}`
                            this.thumb = '/static/church/img/pdf.png'
                        }
                    },
                    method:{
                        clearo_del:function(){
                            console.log('-----clearo-------')
                            this.rosrc = '';
                            this.rokey = ''
                            this.video_tcinfo = {}
                            this.typ = ''
                        }
                    },

                    template: `
                    <div ref="media_select" class="media_select" :id="pname" @click="$emit('click', $event.target)">
                        <input class="" :name="name" type="hidden" :value="rokey||value" />
                        <!--信息来自，对话框，然后应该有一个局部加载，共享对话框中的加载逻辑-->
                        <el-card 
                            :body-style="{ padding: '2px' , position: 'relative' , width: '124px' ,height: '124px' ,display: 'flex',
                            'justifyContent': 'center',
                            alignItems: 'center' }"
                            class='mediacard'
                        >
                            <hovercard v-show="(rosrc||thumb||'') != ''">
                                <span
                                    @click.stop.prevent="$emit('clickp', { 'type':( ((typ||ptyp)||'')=='' ) ? 'images' : (typ||ptyp) ,'src':(typ||ptyp)=='videos'? video_tcinfo.sd:rosrc||thumb} )"
                                >
                                    <i class="el-icon-zoom-in"></i>
                                </span>
                                <span
                                    @click.stop.prevent="$emit('clickd',name)" 
                                >
                                    <i class="el-icon-delete"></i>
                                </span>
                            </hovercard>
                            <img v-if="((typ == 'images') && (rosrc||src||'') != '') " :src="rosrc||src" :style="{ width: '100%', height: '100px' }"/>
                            <img v-if="((typ == 'videos') && (rosrc||src||'') != '') " :src="rosrc||src" :style="{ width: '100%', height: '100px' }"/>
                            <img v-if="((typ == 'audios') && thumb != '') " :src="thumb" :style="{ width: '100%', height: '100px' }"/>
                            <img v-if="((typ == 'pdfs') && thumb != '') " :src="thumb" :style="{ width: '100%', height: '100px' }"/>
                            <i v-show="(rosrc||thumb||'') == ''" class="el-icon-plus" :style="{ fontSize: '3em' }"></i>
                        </el-card>
                    </div>
                    `,
                    delimiters: ["[[","]]"],
                }
            },
            data:{
                ro:undefined,
                loading:undefined,
            },
            store,
            mounted: function (){
                /*
                定时对服务器查找，是否已经转码成功。
                要求：通过可设定查寻对象的api来处理查寻请求
                */
                console.log(window.location.href)
                gb = document.getElementById('goback_bt')
                if (gb){
                    gb.removeEventListener('click',this.goBack1)
                    gb.addEventListener('click',this.goBack1)
                }
          

                dl = document.getElementById('delete_bt')
                if(dl){
                    dl.removeEventListener('click',this.del)
                    dl.addEventListener('click',this.del)
                }
                //this.$nexttrick()
                /*
                ck_imageBtn = document.getElementById('cke_74')
                if (ck_imageBtn){
                    document.removeEventListener('click',invokeMediaBrowse,{capture:true},true)
                    document.addEventListener('click',invokeMediaBrowse,{capture:true},true)
                }*/

            },
            methods:{
                delSelected: function (name) {
                    console.log(name);
                    return;
                    $("#changelist-form input[name='action']").val(name);
    
                    $("#changelist-form [name='_save']").removeAttr('name');
    
                    $("#changelist-form [name!='']").each(function () {
                        var obj = $(this);
                        if (obj.attr('name') && obj.attr('name').indexOf('form-') == 0) {
                            obj.removeAttr('name');
                        }
                    });
    
    
                    var self = this;
    
                    function showMessage(msgs) {
                        msgs.forEach(item => {
                            this.$notify({
                                title: getLanuage('Tips'),
                                message: item.msg,
                                type: item.tag,
                                dangerouslyUseHTMLString: true
                            });
                        });
                    }
    
    
                    //#67 #66 修复删除问题，改为弹出确认
    
                    this.$confirm(getLanuage('Are you sure you want to delete the selected?'))
                        .then(_ => {
                            $.ajax({
                                type: "POST",//方法类型
                                url: "",//url
                                data: $("#changelist-form").serialize() + '&post=yes',
                                success: function (result) {
                                    var msgs = $(result).find('#out_message').html().replace('var messages=', '');
                                    showMessage.call(self, JSON.parse(msgs));
                                    setTimeout(() => {
                                        window.location.reload();
                                    }, 1000);
                                },
                                error: function () {
                                    this.$notify({
                                        title: getLanuage('Tips'),
                                        message: 'Network error',
                                        type: 'error',
                                        dangerouslyUseHTMLString: true
                                    });
                                }
                            });
                        }).catch(_ => {
    
                    });
                },
            
                
                deleteContent:function(columnid,contentid){
                    //this function is for changeform inlinemodel
                    vm = this
                    this.$store.dispatch('deleteContent',{'columnid':columnid,'contentid':contentid}).then(function(rsp){
                        console.log(rsp)
                        vm.loadForm()
                    }).catch(function(err){
                        console.log(err)
                    })
                },
                invokeMediaBrowse:function(e) {
                    console.log(e)
                    console.log(e.target)
                    console.log('invokeMediaBrowse')
                    return false;
                },
                openMsg:function(value){
                    this.$alert(`<a href='${value}' target="_blank">${value}</a>`, '公共链接(Public Link)', {
                        dangerouslyUseHTMLString: true
                    });
                },
                preview:function(media){
                    console.log('-----------preview-------------')
                    console.log(media)

                    if (media.type == "images"){
                        this.$alert(`<img style="width:100%;height:auto;" src="${media.src}">`, {
                            dangerouslyUseHTMLString: true,
                            customClass:"image-preview"
                        });
                        return
                    }else if (media.type == 'videos'){
                        this.$alert(`<video style="width:100%;height:auto;" controls src="${media.src}">`, {
                            dangerouslyUseHTMLString: true,
                            customClass:"image-preview",
                            callback:function(action, instance){
                                console.log(instance)
                                instance.$el.getElementsByTagName('video')[0].pause()
                            }
                        });
                        return
                    }else if(media.type=='audios'){

                        this.$alert(`<div style="display:flex;flex-direction:column;"><video controls="" autoplay="" id="media-preview" name="media"><source src="${media.src}" type="audio/mpeg"></video></div>`, {
                            dangerouslyUseHTMLString: true,
                            customClass:"image-preview",
                            beforeClose:(action,instance,done)=>{
                                //console.log(instance)
                                (instance.$el.querySelector('video#media-preview')||this.document.createElement('audio')).pause()
                                done()
                            }
                        });
                    }else if(media.type=='pdfs'){
                            this.$alert(`<div style="display:flex;flex-direction:column;"><iframe id="media-preview" name="media" src="${media.src}" ></iframe></div>`, {
                                dangerouslyUseHTMLString: true,
                                customClass:"image-preview",
                                beforeClose:(action,instance,done)=>{
                                    //console.log(instance)
                                    done()
                                }
                            });
                        }
                },
                deletep:function(name){
                    for (i = 0 ; i < this.$children.length ; i++){
                        //从媒体选择对话框处理不同的控件
                        if (this.$children[i].$el.id == name){
                            
                            this.$children[i].rosrc = ""
                            this.$children[i].rokey = ""
                            this.$children[i].thumb = ""
                            this.$children[i].video_tcinfo = {}
                            this.$children[i].typ = ""
                        }
                    }
                },
                openUrl(url){
                    newWin= window.open(url,"","dialogWidth=900px;dialogHeight=500px;status=no;help=no;scrollbars=no");
                    console.log(this.ro)
                },
                setRo:function(o){
                    console.log('--------------setRo---------------')
                    console.log(o)
                    //o = JSON.parse(o)
                    //this.ro = o 这里是没有意义的，因为会改变所有的media-sele的内容
                    for (i = 0 ; i < this.$children.length ; i++){
                        //从媒体选择对话框处理不同的控件
                        if (this.$children[i].$el.id == o.from){
                            if ((o||'')==''){
                                this.$children[i].rosrc = '';
                            }else{
                                this.$children[i].rosrc = o.obj.src// image to show
                                this.$children[i].rokey = o.obj.key// bucket key
                                this.$children[i].typ = o.obj.typ
                                this.$children[i].thumb = o.obj.thumb

                                if(o.obj.typ == 'videos'){
                                    this.$children[i].video_tcinfo = o.obj.video_tcinfo
                                    this.$children[i].rosrc = o.obj.video_tcinfo.image3//
                                }
                            }
                        }
                    }
                },
                loadForm:function(){
                    window.location.reload();
                },
                goBack1:function () {
                    //找到上级
                    console.log('-------------goBackform------------')
                    console.log(location.pathname)
                    var array = location.pathname.split(/\/(\d+)|(add)\//g)
                    window.location.href = array[0];
                   
                },
                popupCenter :function (url, title, w, h)  {
                    console.log(`popupCenter(url,title,w,h):(${url},${title},${w},${h})`);
                    const dualScreenLeft = window.screenLeft !==  undefined ? window.screenLeft : window.screenX;
                    const dualScreenTop = window.screenTop !==  undefined   ? window.screenTop  : window.screenY;

                    const width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
                    const height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

                    const systemZoom = width / window.screen.availWidth;
                    const left = (width - w) / 2 / systemZoom + dualScreenLeft
                    const top = (height - h) / 2 / systemZoom + dualScreenTop
                    const newWindow = window.open(url, title, 
                    `
                    scrollbars=yes,
                    width=${w / systemZoom}, 
                    height=${h / systemZoom}, 
                    top=${top}, 
                    left=${left}
                    `
                    )

                    if (window.focus) newWindow.focus();
                },
                del: function () {
                    console.log('-----------del--------')
                    dl = document.getElementById('delete_bt')
                    url = dl.getAttribute('data-url')
                    console.log(url)
                    window.location.href = url;
                },
                formSubmit: function (name, v, e) {
                    console.log(`-----------formSubmit----name:${name}-v:${v}-e:${e}--`)
                    $("#actionName").attr('name', name).val(v);
                    $("form").submit();
                },
                on_mounted:function(e){
                    console.log(e)
                },
                openFullScreen() {
                    this.fullscreenLoading = true;
                    setTimeout(() => {
                    this.fullscreenLoading = false;
                    }, 2000);
                },
                openFullScreen2() {
                    this.loading = this.$loading({
                    lock: true,
                    text: 'Loading',
                    spinner: 'el-icon-loading',
                    background: 'rgba(0, 0, 0, 0.7)'
                    });
                    
                },
                closeFullScreen2(){
                    this.loading.close();
                }


            }
        })