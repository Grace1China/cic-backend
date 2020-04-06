function isAdminPage(){
    var isA=false
    isA = isA || ((document.getElementById('adminForm')||document).querySelector("button[onclick=\"Joomla.submitbutton('article.save')\"]") != null);
    isA =isA || ((document.querySelector("a[title='Edit article']")!==null) && (document.getElementsByClassName('com_content view-category').length !=0));
    isA =isA ||  (document.getElementsByClassName('com_users view-profile').length !=0);
    isA =isA ||  (document.getElementsByClassName('com_users view-login').length !=0);
    return isA
}
function is_user_url(user,url){
    if (user=='diary_editor'){
        arr=['/component/users/profile?Itemid=665','/daily-devotional-category','/component/users/?view=login&Itemid=665','component/users/?view=reset&layout=confirm&Itemid=665']
        for (const element of arr) {
        if(element==url){
            return true
        }
        }
        return false
    }
}


function is_sermon_list(){
    if(this.document.location.pathname.match('^/sermon$|^/sermon\/latest-sermon$|^/cn/sermons$|^/cn/sermons/latest-sermons$')){
        var css = document.createElement('style');
        css.type = 'text/css';
        css.innerText=`img.messageimage{
            width:100px;
            height:100px;
        }`
        document.querySelector("head").appendChild(css)
    }
}
is_sermon_list()

function is_daily_devotional_history(){
    if (document.location.pathname == "/daily-devotional-history-korean" || document.location.pathname == "/daily-devotional-history"){
        (document.getElementById('top')||{}).style="display:none";
        (document.getElementById('breadcrumbs-row')||{}).style="display:none";
        (document.getElementById('footer-wrapper')||{}).style="display:none";
        var css = document.createElement('style');
        css.type = 'text/css';
        css.innerText=`table,thead,th,tbody,tr,td{
                            border:none!important;
                        }
                        thead{
                            display:none;
                        }
                        tr td:nth-child(2),tr td:nth-child(4){
                            display:none;
                        }
                        #limit{
                            display:none;
                        }
                        .btn.btn-primary{
                            display:none;
                        }
                        .btn-group.pull-right{
                            display:none;
                        }`
        document.querySelector("head").appendChild(css)

        var myCollection = document.getElementsByClassName("list-title");
        var i;
        for (i = 0; i < myCollection.length; i++) {
        myCollection[i].getElementsByTagName('a')[0].href=`${myCollection[i].getElementsByTagName('a')[0].href}?v=${new Date().getTime()}` ;
        }
    }
}
is_daily_devotional_history()


function is_daily_devotional(){
    if (document.location.pathname.match(/daily-devotional\d*(a|b)*$/) || document.location.pathname.match(/daily-devotional-(.*)-\d*(a|b)*$/)||document.location.pathname.match(/daily-devotional-(.*)\/(.*)$/)){
        (document.getElementById('top')||{}).style="display:none";
        (document.getElementById('breadcrumbs-row')||{}).style="display:none";
        (document.getElementById('footer-wrapper')||{}).style="display:none";
        ii = document.createElement('i')
        ii.classList='fa fa-play-circle'  
        ii.style.width= 'auto';
        ii.style.height= 'auto';
        ii.style.fontSize= '21px';
        ii.style.marginLeft="20px"

        aa = document.createElement('a')
        m = (document.location.pathname.match(/daily-devotional-(.*)-\d*(a|b)*$/)) 
        if (m && m.length > 1){
                aa.href=`/daily-devotional-history-${m[1]}?v=${(new Date).getTime()}`
        }else{
                aa.href=`/daily-devotional-history?v=${(new Date).getTime()}`
        }

        m = document.location.pathname.match(/daily-devotional-(portuguese|korean)($|\/(.*)$)/)
        //新历史列表
        if (m && m.length == 4 && m[3] == undefined){
            //list
            
        }

        if (m && m.length == 4 && m[3] != undefined){
            //article need add an previous Date
            aa.href=`/daily-devotional-${m[1]}?v=${(new Date).getTime()}`
        }
        
        aa.innerText = "Previous Dates"
        aa.style.float="right"
        aa.style.marginLeft="20px"

        if (document.getElementsByClassName('item_info').length>0){


            document.getElementsByClassName('item_info')[0].getElementsByTagName('dd')[0].appendChild(ii)
            ii.addEventListener('click', function play() {
                if(ii.classList.value.indexOf('fa-play-circle')>=0){
                (document.getElementsByTagName('audio')[0]||document.getElementsByTagName('video')[0]).play()
                ii.classList = 'fa fa-pause' 
                }else{
                    (document.getElementsByTagName('audio')[0]||document.getElementsByTagName('video')[0]).pause()
                ii.classList = 'fa fa-play-circle' 
                }        
            }, false);
        
            document.getElementsByClassName('item_info')[0].getElementsByClassName('item_hits')[0].style.float="right"
            document.getElementsByClassName('item_info')[0].getElementsByClassName('item_hits')[0].style.marginLeft='20px'
            document.getElementsByClassName('item_info')[0].getElementsByTagName('dd')[0].appendChild(aa)
        }


       var css = document.createElement('style');//test inotify  2
        css.type = 'text/css';
        css.innerText=`.item_fulltext p{padding-bottom:0px;}
        iframe p {padding-bottom:0px;}
        `
        document.querySelector("head").appendChild(css)

        // var iframe  = document.getElementsByTagName('iframe')
        var iframe  = document.getElementById('jform_articletext_ifr')
        if(iframe){
            ifcss = iframe.getDocument().createElement('style');//test inotify  2
            ifcss.type = 'text/css';
            ifcss.innerText=`p{padding-bottom:0px;}`
            iframe.getDocument().getElementsByTagName('head').appendChild(ifcss)
        }
        var iframe  = document.getElementById('jform_articletext_editor_preview_iframe')

        if(iframe){
            ifcss = iframe.getDocument().createElement('style');//test inotify  2
            ifcss.type = 'text/css';
            ifcss.innerText=`p{padding-bottom:0px;}`
            iframe.getDocument().getElementsByTagName('head').appendChild(ifcss)
        }
        
        
        
    }
}

is_daily_devotional()

      
function addVue (pubtab){
    app = document.createElement('div')
    app.innerHTML=`
    <el-form :label-position="labelPosition" label-width="80px" ref="ruleForm" :model="formLabelAlign">
    <el-form-item label="菜单标题">
        <el-input v-model="title"></el-input>
    </el-form-item>
    <el-form-item label="菜单别名>
        <el-input v-model="alias"></el-input>
    </el-form-item>
    <el-form-item>
        <el-button type="primary" @click="submitForm('menuForm')">链接菜单</el-button>
    </el-form-item>
    </el-form>`
    app.id="app1"
    console.log(app)
    pubtab.appendChild(app)
    console.log(pubtab)
    var v1 = new Vue({
        el: '#app1',
        data() {
        return {
            labelPosition: 'right',
            title:'',
            alias:''
        };
        },
        methods: {
            submitForm(formName) {
            if(formName=='menuForm'){
                console.log(this.title)
                console.log(this.alias)

            }
            
        },
        resetForm(formName) {
            this.$refs[formName].resetFields();
        }
        }
    })
}
  
if(isAdminPage()){
    menu = document.getElementById('icemegamenu')
    if(menu){
        menu.innerHTML = `<a href='http://bicf.org/component/users/profile?Itemid=665'>admin home</a>`
    }
    profile = document.getElementById('users-profile-custom')
    if(profile){
        profile.innerHTML = ''
        funBtn = document.createElement('div')
        funBtn.style.textAlign="auto"
        funBtn.innerHTML=`<a href='http://www.bicf.org/daily-devotional-category'>从新劝勉文集</a>`
        profile.appendChild(funBtn)
    }
    (document.getElementsByClassName('users-profile-custom-profile')[0]||{}).style="display:none;";
    (document.getElementsByClassName('mod-languages')[0]||{}).style="display:none;";
    (document.getElementById('copyright')||{}).style="display:none;";
    (document.getElementsByClassName('btn-toolbar pull-right')[0]||{}).style="display:none;";
    // (document.getElementsByClassName('page-login page-login__')[0].nextElementSibling||{}).style="display:none;"
    publishing = document.getElementById('publishing')
    if(publishing){
        addVue(publishing)
    }
}

