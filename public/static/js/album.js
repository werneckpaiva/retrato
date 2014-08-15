var Settings = {
    URL_PREFIX: "/",
    URL_DATA_PREFIX: "/api/"
}

var StringUtil = {
    sanitizeUrl: function(url){
        url = url.replace(/([^:])[\/]+/g, '$1/');
        return url
    },
    humanizeName: function(name){
        name = name.replace(/_/g, " ");
        name = name.replace(/\.jpe?g/i, "");
        return name
    }
}


var Fullscreen = {
    open: function(element){
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    },

    close: function close() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    },

    onchange: function(handler){
        document.addEventListener("fullscreenchange", handler);
        document.addEventListener("webkitfullscreenchange", handler);
        document.addEventListener("mozfullscreenchange", handler);
        document.addEventListener("MSFullscreenChange", handler);
    },

    isActive: function(){
       return document.fullScreenElement != null 
                    || document.webkitCurrentFullScreenElement != null
                    || document.mozFullScreenElement != null
                    || document.msFullscreenElement != null
    }
}

function AlbumModel(albumDelegate){

    var delegate = albumDelegate
    var self = this

    this.path = null;
    this.albuns = null;
    this.pictures = null;
    this.visibility = null;

    this.loading = false;

    this.selectedPictureIndex = null;
    this.highlightOn = false;
    this.detailsOn = false;

    this.loadAlbum = function(albumPath){
        albumPath = albumPath.replace(Settings.URL_PREFIX, '')
        console.log("loading: "+albumPath);
        self.loading = true
        delegate.get(albumPath, loadAlbumResultHandler, loadAlbumFailHandler);
    }

    function loadAlbumResultHandler(result){
        for (var prop in result){
            if (self.hasOwnProperty(prop)){
                self[prop] = result[prop];
            }
        }
        console.log(self)
        self.loading = false
        self.selectedPictureIndex = null;
    }

    function loadAlbumFailHandler(error){
        self.loading = false
        alert("Album does not exist")
    }

    return this;
}

function AlbumDelegate(){

    this.get = function(albumPath, resultHandler, failHandler){
        var url = Settings.URL_DATA_PREFIX + albumPath;
        url = StringUtil.sanitizeUrl(url);
        console.log("URL: "+url)
        $.get(url, function(result) {
            resultHandler(result)
        }).fail(function(status){
            failHandler(status)
        });
    }
}

function Loading(model, conf){

    var $view = null

    function init(){
        $view = conf.view;
        watch(model, "loading", function(){
            $view.toggle(model.loading);
        });
        $view.hide();
    }

    init();
}

function AlbumNavigator(model, conf){

    var template = null;
    var $view = null;
    var $viewList = null;
    
    var animate = true;

    function init(){
        $view = conf.view;
        template = conf.template;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view;
        animate = (conf.listClass)? conf.listClass : true;

        watch(model, "albuns", function(){
            displayAlbuns();
        });
        
    }

    function getAlbumUrl(albumName){
        var url = Settings.URL_PREFIX + model.path + '/' + albumName;
        url = StringUtil.sanitizeUrl(url);
        return url;
    }
    
    function displayAlbuns(){
        if(!model.albuns || model.albuns.length == 0){
            $view.removeClass("visible");
            return;
        }
        $view.addClass("visible");
        content = "";
        for (var i=0; i<model.albuns.length; i++){
            var albumName = model.albuns[i]
            content += Mustache.render(template, {
                url: getAlbumUrl(albumName), 
                name: StringUtil.humanizeName(albumName)});
        }
        $viewList.html(content);
        enableAsynchronous();
    }

    function enableAsynchronous(){
        $view.find("a").click(function(event){
            event.preventDefault();
            $('html,body').animate({scrollTop:0}, 500);
            model.loadAlbum($(this).attr("href"))
        })
    }

    init();
}

function AlbumBreadcrumb(model, conf){

    var self = this;

    var $view = null;
    var $viewList = null;
    var templateHome = null;
    var template = null;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view
        templateHome = conf.templateHome
        template = conf.template
        
        watch(model, "path", function(){
            self.updatePath()
        });

        watch(model, "selectedPictureIndex", function(){
            self.updatePath();
        });
    }

    function getAlbumUrl(albumName){
        var url = Settings.URL_PREFIX + model.path + '/' + albumName;
        url = StringUtil.sanitizeUrl(url);
        return url;
    }

    this.updatePath = function(){
        var parts = model.path.split("/");
        if (parts[parts.length - 1]==""){
            parts.pop();
        }
        if (model.selectedPictureIndex != null){
            var p = model.pictures[model.selectedPictureIndex];
            parts.push(p.filename);
        }
        var partial = '/'
        var content = Mustache.render(templateHome, {
            url: StringUtil.sanitizeUrl(Settings.URL_PREFIX + '/')
        });
        for (var i=1; i<parts.length; i++){
            partial += parts[i] + '/';
            params = {}
            if (i < parts.length - 1){
                params.url = StringUtil.sanitizeUrl(Settings.URL_PREFIX + partial);
            }
            params.name = StringUtil.humanizeName(parts[i])
            content += Mustache.render(template, params);
        }
        $viewList.html(content)
        enableAsynchronous();
    }

    function enableAsynchronous(){
        $viewList.find("a").click(function(){
            model.loadAlbum($(this).attr("href"));
            return false;
        })
    }

    init()
}


function AlbumMenu(model, conf){

    var self = this;

    var $view = null;
    var $detailsButton = null;
    var $fullscreenButton = null;

    function init(){
        $view = conf.view;
        $detailsButton = conf.detailsButton;
        $fullscreenButton = conf.fullscreenButton

        watch(model, "selectedPictureIndex", function(){
            pinMenu();
            showHideDetailsButton();
            showHideFullscreenButton();
        });

        $detailsButton.click(function(event){
            event.preventDefault();
            showHideDetails();
        });

        $fullscreenButton.click(function(event){
            event.preventDefault();
            openCloseFullscreen();
        })

        Fullscreen.onchange(function(event){
            $fullscreenButton.toggleClass("selected", Fullscreen.isActive());
        });
        
        showHideDetailsButton();
        showHideFullscreenButton();
    }

    function pinMenu(){
        if (model.selectedPictureIndex != null){
            $view.addClass("headroom--pinned").addClass("headroom--top")
            $view.removeClass("headroom--not-top").removeClass("headroom--unpinned")
        }
    }

    function showHideDetailsButton(){
        if (model.selectedPictureIndex == null){
            model.detailsOn = false;
            $detailsButton.hide();
        } else {
            $detailsButton.show();
        }
    }

    function showHideDetails(){
        model.detailsOn = !model.detailsOn;
        $detailsButton.toggleClass("selected", model.detailsOn);
    }

    function showHideFullscreenButton(){
        if (model.selectedPictureIndex == null){
            model.detailsOn = false;
            $fullscreenButton.hide();
        } else {
            $fullscreenButton.show();
        }
    }

    function openCloseFullscreen(){
        if (Fullscreen.isActive()){
            Fullscreen.close();
        } else {
            Fullscreen.open(document.getElementById("content"));
        }
    }

    init()
}


function AlbumDeepLinking(model){

    var self = this;

    function init(){
        watch(model, "path", function(){
            updateUrl()
        });

        $(window).bind('popstate', function(event){
            changeAlbumFromUrl()
        })

        changeAlbumFromUrl()
    }

    function extractPathFromUrl(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(Settings.URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        return albumPath;
    }

    function updateUrl(){
        var currentAlbumPath = location.pathname
        var newPath = Settings.URL_PREFIX + model.path
        if (currentAlbumPath == newPath){
            return;
        }
        newPath = StringUtil.sanitizeUrl(newPath)
        history.pushState(null, null, newPath)
    }

    function changeAlbumFromUrl(){
        var albumPath = extractPathFromUrl();
        if (albumPath == model.path){
            return;
        }
        model.loadAlbum(albumPath);
    }

    init();
}

function AlbumPhotos(model, conf){

    var self = this;
    var $view = null;
    var $viewList = null;
    var template = null;
    var currentWidth = 0;
    var heightProportion = 0.45;

    var margin = 2;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view
        template = conf.template
        if (conf.heightProportion){
            heightProportion = conf.heightProportion
        }

        watch(model, "pictures", function(prop, action, newvalue, oldvalue){
            var picturesChanged = Array.isArray(newvalue)
            self.displayPictures(picturesChanged);
        });

        $(window).resize(function(){
            self.resizePictures();
        })
    }

//    this.picturesChanged = function(){
//        var imgs = $viewList.find("img")
//        if (imgs.length == 0 || model.pictures.length == 0){
//            return true;
//        }
//        var changed = false
//        for (var i=0; i<imgs.length; i++){
//            if (model.pictures[i] && imgs[i].src.indexOf(model.pictures[i].thumb) == -1){
//                changed = true
//            }
//        }
//        return changed;
//    }
    
    this.displayPictures = function(picturesChanged){
        if (picturesChanged===false){
            return;
        }
        
        $viewList.empty();
        if(!model.pictures || model.pictures.length == 0){
            $view.hide();
            return;
        }
        $view.show();

        var resize = new Resize(model.pictures, heightProportion);
        currentWidth = $view.width()
        console.log("currentWidth: "+currentWidth)
        var newPictures = resize.doResize(currentWidth, $(window).height());

        content = "";
        for (var i=0; i<newPictures.length; i++){
            var p = newPictures[i]
            var params = {
                    width: p.newWidth-margin,
                    height: p.newHeight-margin
            }
            if (!conf.lazyLoad){
                params.src = p.thumb 
            }
            content += Mustache.render(template, params);
        }
        $viewList.html(content);
        $viewList.find("img").click(function(){
            model.selectedPictureIndex = $(this).data("index");
        })
        if (conf.lazyLoad){
            lazyLoad();
        }
    }

    this.resizePictures = function(){
        var newWidth = $view.width()
        if (newWidth == currentWidth) return;
        currentWidth = $view.width()
        var resize = new Resize(model.pictures, heightProportion);
        var newPictures = resize.doResize(currentWidth, $(window).height());
        $viewList.children().each(function(index, item){
            var p = newPictures[index]
            var width = (p.newWidth-margin);
            var height = (p.newHeight-margin);
            $(this).css("width", width).css("height", height)
            $(this).find("img").attr("width", width).attr("height", height)
        })
    }
    
    function lazyLoad(){

        function loadNextPicture(){
            if (index >= model.pictures.length){
                return
            }
            $viewList.find("img:eq("+index+")").data("index", index)
            if (image.src == model.pictures[index].thumb){
                index++;
                loadNextPicture();
            } else {
                image.src = model.pictures[index].thumb
            }
        }

        var index = 0;
        var image = new Image()
        image.onload = function(){
            $viewList.find("img:eq("+index+")")
                .attr("src", this.src)
                .show()
            index++
            loadNextPicture()
        }
        
        loadNextPicture()
    }

    init();
}

function AlbumPageTitle(model, conf){

    var template = 'Album {{title}}';
    var templateEmpty = '';
    var separator = ' | '

    function init(){
        if (conf && conf.template) {
            template = conf.template;
        }
        if (conf && conf.templateEmpty) {
            templateEmpty = conf.templateEmpty;
        } else {
            templateEmpty = template;
        }
        watch(model, "path", function(){
            self.updateTitle()
        });
        watch(model, "selectedPictureIndex", function(){
            self.updateTitle();
        });
    }

    this.updateTitle = function(){
        var path = model.path;
        path = path.replace(/^\//, '');
        path = path.replace(/\/$/, '');
        path = path.replace(/[\/]+/g,  separator);
        var newTitle = ''
        if (path){
            newTitle = Mustache.render(template, {title: path});
        } else {
            newTitle = Mustache.render(templateEmpty);
        }
        document.title = newTitle
    }
    
    init();
}