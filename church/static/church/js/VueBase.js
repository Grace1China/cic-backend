
Vue.component('hovercard', {
    //props: ['value'],
   
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
            <div class='extra-bar'
                @mouseover="hover = true"
                @mouseleave="hover = false"
                :style="[nstyle,hover ? hstyle : {}]"
            >
            <slot/>
            </div>
    `
})
Vue.component('media-base-selctl', {
    props: ['name','value','src','ro'],
   
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
            rokey:undefined
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
        ro: {
            immediate: true,    // 这句重要
            handler (val) {
                console.log('action Value:' )
                console.log(val)
                if ((val||'')==''){
                    this.rosrc = '';
                }else{
                    roo = JSON.parse(val)
                    //if (roo.hasOwnProperty('src')){
                    this.rosrc = roo.src
                    //}
                    this.rokey = roo.key
                }
            }
        }
    },
    method:{
        openUrl:function(url){
            console.log(url)
        }
    },
    //ro = {'type':'images','src':'https://',key:'ims/...'} key是存储在media的字段中的，这样+上平台存储桶的配置，可以算出src
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
            <hovercard v-show="(rosrc||src||'') != ''">
                <span
                    @click.stop.prevent="$emit('clickp', {'type':'images','src':rosrc} )"
                >
                    <i class="el-icon-zoom-in"></i>
                </span>
                <span
                    @click.stop.prevent="$emit('clickd')"
                >
                    <i class="el-icon-delete"></i>
                </span>
            </hovercard>
            <img v-show="(rosrc||src||'') != ''" :src="rosrc||src" :style="{ width: '100%', height: '100px' }"/>
            <i v-show="(rosrc||src||'') == ''" class="el-icon-plus" :style="{ fontSize: '3em' }"></i>
        </el-card>
    </div>
    `,
    delimiters: ["[[","]]"],
})

Vue.component('button-counter', {
    delimiters: ["[[","]]"],
    data: function () {
      return {
        count: 0
      }
    },
    template: '<button v-on:click="alert(1)">You clicked me [[ count ]]  times.</button>'
  }
)

// ro=window.showModalDialog("/media_browse/?type=videos&from=admin","","dialogWidth=900px;dialogHeight=500px;status=no;help=no;scrollbars=no");

function put_vue(
    key,vu
){
    var vue_dict = {}
    if (!vue_dict.hasOwnProperty(key)){
        vue_dict['key'] = vu
    }
    return vue_dict[key]
}

//v-on:click='$emit('click', $event.target)'
