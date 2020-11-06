(function () {
    if (window.frameElement) {
        window.frameElement.contentWindow.parent.callback()
        console.log(window.frameElement.contentDocument)
        ck_imageBtn = window.frameElement.contentDocument.getElementById('cke_74')
        if (ck_imageBtn){
            window.frameElement.contentDocument.addEventListener('click',invokeMediaBrowse,{capture:true},true)
        }
    }

    function invokeMediaBrowse(e) {
        console.log(e)
        console.log(e.target)
        console.log('invokeMediaBrowse')
        return false;
    }

    window.addEventListener('hashchange', function (e) {
        if (e.newURL != e.oldURL) {
            openByHash()
        }
    });

    function openByHash() {
        var hash = location.hash;
        hash = hash.substring(1)

        for (var i = 0; i < app.menuData.length; i++) {
            var item = app.menuData[i]
            if ((item.url || '/') == hash) {
                app.openTab(item, item.eid, true);
                break;
            }
        }
    }

    function changeUrl(data) {
        if (data.url && data.url.indexOf('http') != 0) {
            location.hash = '#' + (data.url || '/')
        }
    }

    window.callback = function () {
        window.location.reload()
    }

//    var fontConfig = new Vue({
//        el: '#dynamicCss',
//        data: {
//            fontSize: 14
//        },
//        created: function () {
//            var val = getCookie('fontSize');
//            if (val) {
//                this.fontSize = parseInt(val);
//            } else {
//                this.fontSize = 0;
//            }
//        },
//        methods: {}
//    });

    // Waves.init();

    //为元素注册水波纹效果
    Vue.directive('waves', {
        // 当被绑定的元素插入到 DOM 中时……
        inserted: function (el) {
            // 聚焦元素
            Waves.attach(el);
            Waves.init();
        }
    });


    window.getLanuage = function (key) {
        if (!window.Lanuages) {
            return "";
        }
        var val = Lanuages[key];
        if (!val || val == "") {
            val = key;
        }
        return val
    }
    window.simple_call = function (data) {
        var oldVersion = parseInt(__simpleui_version.replace(/\./g, ''))
        var newVersion = parseInt(data.data.name.replace(/\./g, ''))
        var body = data.data.body;
        // console.log(oldVersion)
        // console.log(newVersion)
        if (oldVersion < newVersion) {
            app.upgrade.isUpdate = true;
            app.upgrade.body = body;
            app.upgrade.version = data.data.name;

        }
    }
    new Vue({
        el: '#main',
        data: {
            upgrade: {
                isUpdate: false,
                body: '',
                version: '',
                dialogVisible: false
            },
            isResize: false,
            searchInput: '',
            height: 1000,
            fold: false,
            zoom: false,
            timeline: true,
            tabs: [home],
            tabModel: 0,
            tabIndex: 0,
            menus: [],
            menuActive: '0',
            breadcrumbs: [],
            language: window.language,
            pwdDialog: {},
            themeDialogVisible: false,
            small: false,
            themes: SimpleuiThemes,
            theme: "",
            themeName: "",
            // church:'',
            managedChurch:'',
            popup: {
                left: 0,
                top: 0,
                show: false,
                tab: null,
                menus: [{
                    text: getLanuage('Refresh'),
                    icon: 'el-icon-refresh',
                    handler: function (tab, item) {
                        try {
                            document.getElementById(tab.id).contentWindow.location.reload(true);
                        } catch (e) {
                            console.log(e)
                            var url = tab.url.split('?')[0];
                            tab.url = url + '?_=' + new Date().getTime()
                        }
                    }
                }, {
                    text: getLanuage('Close current'),
                    icon: 'el-icon-circle-close',
                    handler: function (tab, item) {
                        app.handleTabsEdit(tab.id, 'remove');
                    }
                }, {
                    text: getLanuage('Close other'),
                    icon: 'far fa-copy',
                    handler: function (tab) {
                        app.tabs.forEach(item => {
                            if (item.id != tab.id) {
                                app.handleTabsEdit(item.id, 'remove');
                            }
                        })
                    }
                }, {
                    text: getLanuage('Close all'),
                    icon: 'el-icon-close',
                    handler: function (tab, item) {

                        app.$confirm(Lanuages["Are you sure you want them all closed"], Lanuages.Tips, {
                            confirmButtonText: Lanuages.ConfirmYes,
                            cancelButtonText: Lanuages.ConfirmNo,
                            type: 'warning'
                        }).then(function () {
                            app.tabs.forEach((tab, index) => {
                                if (index != 0) {
                                    app.handleTabsEdit(tab.id, 'remove');
                                }
                            });
                            app.menuActive = '1';
                        }).catch(function () {

                        });

                    }
                }, {
                    text: getLanuage('Open in a new page'),
                    icon: 'el-icon-news',
                    handler: function (tab, item) {
                        window.open(tab.newUrl);
                    }
                }]
            },
            //菜单里面的模块
            models: [],
            fontDialogVisible: false,
            fontSlider: 12,
            loading: false,
            menuTextShow: true,
            menuData: []
        },
        watch: {
            fold: function (newValue, oldValue) {
                // console.log(newValue)
            },
            menus: function (newValue, oldValue) {
                var self = this;

                newValue.forEach(item => {
                    if (item.id == '0') {
                        return;
                    }

                    if (item.models) {
                        item.models.forEach(child => {
                            self.models.push(child);
                        });
                    } else {
                        self.models.push(item);
                    }
                });
            }
            /*,
            tabs: function (newValue, oldValue) {

                //改变tab时把状态储存到sessionStorage
                console.log(newValue)
            }*/
        },
        created: function () {


            var val = getCookie('fold') == 'true';
            this.small = this.fold = val;
            this.menuTextShow = !this.fold;

            var self = this;
            window.onresize = function () {

                self.height = document.documentElement.clientHeight || document.body.clientHeight
                var width = document.documentElement.clientWidth || document.body.clientWidth;

                if (!self.small) {

                    self.menuTextShow = !(width < 800);
                    self.$nextTick(() => {
                        self.fold = width < 800;
                    })
                }
                self.isResize = true

                //判断全屏状态
                try {
                    self.zoom = document.webkitIsFullScreen;
                } catch (e) {
                    //不是非webkit内核下，无能为力
                }
            }
            window.app = this;


            window.menus.forEach(item => {
                item.icon = getIcon(item.name, item.icon);

                if (item.models) {
                    item.models.forEach(mItem => {
                        mItem.icon = getIcon(mItem.name, mItem.icon);
                        self.menuData.push(mItem)
                    });
                } else {
                    self.menuData.push(item)
                }
            });

            this.menus = window.menus
            this.managedChurch = window.managed_church

            this.theme = getCookie('theme');
            this.themeName = getCookie('theme_name');

            //接收子页面的事件注册
            window.themeEvents = [];
            window.fontEvents = [];
            window.addEvent = function (name, handler) {
                if (name == 'theme') {
                    themeEvents.push(handler);
                } else if (name == 'font') {
                    fontEvents.push(handler);
                }
            }
            var temp_tabs = sessionStorage['tabs'];

            if (temp_tabs && temp_tabs != '') {
                this.tabs = JSON.parse(temp_tabs);
            }
            if (location.hash != '') {
                openByHash();
            }

            //elementui布局问题，导致页面不能正常撑开，调用resize使其重新计算
            if (window.onresize) {
                window.onresize();
            }
        },
        methods: {
            syncTabs: function () {
                if (window.sessionStorage) {
                    sessionStorage['tabs'] = JSON.stringify(this.tabs);
                }
            },
            reset: function () {
                this.fontSlider = 14;
                fontConfig.fontSize = 0;

                setCookie('fontSize', 0);

                this.fontDialogVisible = false;
                fontEvents.forEach(handler => {
                    handler(0);
                });
            },
            fontClick: function () {
                this.fontSlider = fontConfig.fontSize;
                this.fontDialogVisible = !this.fontDialogVisible;
            },
            fontSlideChange: function (value) {
                fontConfig.fontSize = value;
                //写入cookie
                setCookie('fontSize', value);
                fontEvents.forEach(handler => {
                    handler(value);
                });

            },
            add_content:function(command){
                console.log(command)
                //window.location.href = url;
                //console.log(window.location.href)
                return;
            },
            iframeLoad: function (tab, e) {
                url = e.target.contentWindow.location.href
                console.log('--------iframeLoad-------')
                console.log(tab)
                console.log(e)
                tab.newUrl = url;
                tab.loading = false;
                this.$forceUpdate();
                var self = this;
                e.target.contentWindow.beforeLoad = function () {
                    tab.loading = true;
                    self.$forceUpdate();
                }
                this.loading = false;
            },
            setTheme: function (item) {
                var url = window.themeUrl;
                if (item.file && item.file != '') {
                    this.theme = url + item.file;
                } else {
                    this.theme = '';
                }
                this.themeName = item.text;
                setCookie('theme', this.theme);
                setCookie('theme_name', item.text);

                var self = this;
                //通知子页面
                window.themeEvents.forEach(handler => {
                    handler(self.theme)
                });
            },
            openUrl: function (url) {
                window.open(url);
            },
            contextmenu: function (item, e) {

                //home没有popup menu
                if (item.id == '0') {
                    return;
                }
                this.popup.tab = item;
                this.popup.left = e.clientX;
                this.popup.top = e.clientY;
                this.popup.show = true;
            },
            mainClick: function (e) {
                this.popup.show = false;
            },
            tabClick: function (tab) {
                console.log('---------tabClick---------')
                var item = this.tabs[tab.index];
                var index = item.index;
                console.log(item)
                this.menuActive = String(index);
                this.breadcrumbs = item.breadcrumbs;
                if (index == '1') {
                    item.url = '/'
                }
                changeUrl(item);
            },
            handleTabsEdit: function (targetName, action) {
                console.log('---------handleTabsEdit---------')
                var self = this;
                if (action === 'remove') {
                    var next = '0';
                    this.tabs.forEach((tab, index) => {
                        if (tab.id == targetName) {
                            var temp = self.tabs[index + 1] || self.tabs[index - 1];
                            if (temp) {
                                next = temp.id;
                                self.menuActive = temp.index;
                                self.breadcrumbs = temp.breadcrumbs;
                                changeUrl(temp)
                            }
                        }
                    });
                    this.tabModel = next;

                    if (targetName != 0) {
                        this.tabs = this.tabs.filter(tab => tab.id !== targetName);
                    }
                    this.syncTabs();
                }
            }
            ,
            openTab: function (data, index, selected) {
                if (data.breadcrumbs) {
                    this.breadcrumbs = data.breadcrumbs;
                }

                //如果data没有eid，就直接打开或者添加，根据url
                if (!data.eid) {
                    data.eid = new Date().getTime() + "" + Math.random();
                }

                if (index) {
                    this.menuActive = String(index);
                }
                if (selected) {
                    //找到name，打开
                    // console.log(data)
                    for (var i = 0; i < this.tabs.length; i++) {
                        if (this.tabs[i].url == data.url) {
                            this.tabModel = this.tabs[i].id;
                            break;
                        }
                    }
                    return;
                }

                this.breadcrumbs = data.breadcrumbs;
                var exists = null;
                //判断是否存在，存在就直接打开
                for (var i = 0; i < this.tabs.length; i++) {
                    var tab = this.tabs[i];
                    if (tab.id == data.eid) {
                        exists = tab;
                        continue;
                    }
                }

                if (exists) {
                    this.tabModel = exists.id;
                } else {
                    //其他的网址loading会一直转
                    if (data.url && data.url.indexOf('http') != 0) {
                        data.loading = true;
                        this.loading = true;
                    }
                    // data.id = new Date().getTime() + "" + Math.random();
                    data.id = data.eid;
                    data.index = index;
                    this.tabs.push(data);
                    this.tabModel = data.id;
                }
                changeUrl(data)
                this.syncTabs();
            }
            ,
            foldClick: function () {

                this.menuTextShow = !this.menuTextShow;
                this.$nextTick(() => {
                    this.fold = !this.fold;

                    this.small = this.fold;
                    //设置进cookie
                    setCookie('fold', this.fold);
                });


            }
            ,
            changePassword: function () {
                var width = document.documentElement.clientWidth || document.body.clientWidth;
                if (width > 800) {
                    this.pwdDialog = {
                        url: window.urls.changePassword + '?dialog=1',
                        name: language.change_password,
                        show: true
                    };
                } else {
                    this.openTab({
                        url: window.urls.changePassword,
                        icon: 'far fa-edit',
                        name: language.change_password,
                        breadcrumbs: [{
                            name: language.change_password,
                            icon: 'far fa-edit'
                        }]
                    })
                    app.breadcrumbs = [language.change_password];
                }
            }
            ,
            logout: function () {
                this.$confirm(language.confirm, Lanuages.Tips, {
                    confirmButtonText: language.yes,
                    cancelButtonText: language.no,
                    type: 'warning'
                }).then(function () {
                    //清除cookie主题设置和sessionStore数据
                    delete sessionStorage['tabs'];
                    setCookie('theme', '');
                    setCookie('theme_name', '');
                    window.location.href = window.urls.logout;
                }).catch(function () {

                });
            }
            ,
            goIndex: function (url) {
                if (!url || url == 'None') {
                    url = '/';
                }
                window.open(url);
            }
            ,
            getLanuage: getLanuage,
            getIcon: getIcon,
            goZoom: function () {
                var el = window.document.body;
                if (!this.zoom) {

                    var isFullscreen = document.fullScreen || document.mozFullScreen || document.webkitIsFullScreen;
                    if (!isFullscreen) {//进入全屏,多重短路表达式
                        (el.requestFullscreen && el.requestFullscreen()) ||
                        (el.mozRequestFullScreen && el.mozRequestFullScreen()) ||
                        (el.webkitRequestFullscreen && el.webkitRequestFullscreen()) || (el.msRequestFullscreen && el.msRequestFullscreen());
                    }
                    this.zoom = true;
                } else {

                    document.exitFullscreen ? document.exitFullscreen() :
                        document.mozCancelFullScreen ? document.mozCancelFullScreen() :
                            document.webkitExitFullscreen ? document.webkitExitFullscreen() : '';
                    this.zoom = false;
                }
            }
            ,
            displayTimeline: function () {
                this.timeline = !this.timeline;
            },
            report: function () {
                window.open('https://github.com/newpanjing/simpleui/issues')
            }
        }
    })


})();