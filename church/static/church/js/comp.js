let mediaSele = {
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
                // src :'',
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
        methods: {
            clearo_del:function(){
                console.log('-----clearo-------')
                this.rosrc = '';
                this.rokey = ''
                this.video_tcinfo = {}
                this.typ = ''
            },
            openUrl:function(url){
                newWin= window.open(url,"媒体库","width=900px;height=580px;status=no;help=no;scrollbars=no");
                console.log(newWin)
            },
            popupCenter :function (url, title, w, h)  {
                const dualScreenLeft = window.screenLeft !==  undefined ? window.screenLeft : window.screenX;
                const dualScreenTop = window.screenTop !==  undefined   ? window.screenTop  : window.screenY;

                const width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
                const height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

                const systemZoom = width / window.screen.availWidth;
                const left = (width - w) / 2 / systemZoom + dualScreenLeft
                const top = (height - h) / 2 / systemZoom + dualScreenTop

                // alert(`${title}w${w}h${h}top${top}left${left}`)

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
        },

        template: `
        <div ref="media_select" class="media_select" :id="pname" @click="popupCenter('/media_browse/?type=images&from=page_builder','媒体库',900,600)">
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