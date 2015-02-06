function Loading(model, conf){

    var $view = null;

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
        if(!model.albuns || model.albuns.length === 0){
            $view.removeClass("visible");
            return;
        }
        $view.addClass("visible");
        content = "";
        for (var i=0; i<model.albuns.length; i++){
            var albumName = model.albuns[i];
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
            model.loadAlbum($(this).attr("href"));
        });
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
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view;
        templateHome = conf.templateHome;
        template = conf.template;
        
        watch(model, "path", function(){
            self.updatePath();
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

    this.getCurrentContext = function(){
        var parts = [];
        if (model.path) {
            parts = model.path.split("/");
        }
        if (parts[parts.length - 1]===""){
            parts.pop();
        }
        if (model.selectedPictureIndex !== null){
            var p = model.pictures[model.selectedPictureIndex];
            parts.push(p.filename);
        }
        var partial = '/';
        var context = {};
        context.url = StringUtil.sanitizeUrl(Settings.URL_PREFIX + '/');
        context.parts = []
        for (var i=1; i<parts.length; i++){
            partial += parts[i] + '/';
            params = {};
            if (i < parts.length - 1){
                params.url = StringUtil.sanitizeUrl(Settings.URL_PREFIX + partial);
            }
            params.name = StringUtil.humanizeName(parts[i]);
            context.parts.push(params)
        }
        return context;
    }
    
    this.render = function(context){
        var content = Mustache.render(templateHome, {
            url: context.url
        });
        for (var i=0; i<context.parts.length; i++){
            var params = context.parts[i];
            content += Mustache.render(template, params);
        }
        $viewList.html(content);
    }
    this.updatePath = function(){
        var context = this.getCurrentContext();
        this.render(context);
        enableAsynchronous();
    };

    function enableAsynchronous(){
        $viewList.find("a[target!='_blank']").click(function(){
            model.loadAlbum($(this).attr("href"));
            return false;
        });
    }

    init();
}

function AlbumDeepLinking(model){

    var self = this;

    function init(){
        watch(model, "path", function(){
            updateUrl();
        });

        $(window).bind('popstate', function(event){
            changeAlbumFromUrl();
        });

        changeAlbumFromUrl();
    }

    function extractPathFromUrl(){
        var albumPath = location.pathname;
        albumPath = albumPath.replace(Settings.URL_PREFIX, "");
        if (!albumPath){
            albumPath = "/";
        }
        return albumPath;
    }

    function updateUrl(){
        var currentAlbumPath = StringUtil.sanitizeUrl(location.pathname);
        var newPath = StringUtil.sanitizeUrl(Settings.URL_PREFIX + model.path);
        if (currentAlbumPath == newPath){
            return;
        }
        newPath = StringUtil.sanitizeUrl(newPath);
        newPath = newPath + location.search
        history.pushState(null, null, newPath);
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

function AlbumPageTitle(model, conf){

    var template = 'Album {{title}}';
    var templateEmpty = '';
    var separator = ' | ';

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
            self.updateTitle();
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
        var newTitle = '';
        if (path){
            newTitle = Mustache.render(template, {title: path});
        } else {
            newTitle = Mustache.render(templateEmpty);
        }
        document.title = newTitle;
    };
    
    init();
}

function AlbumAjaxDelegateWithAuth(){

    var delegate = new AlbumAjaxDelegate();

    this.get = function(albumPath, resultHandler, failHandler){
        var pathWithToken=albumPath+location.search;
        delegate.get(pathWithToken, resultHandler, failHandler);
    }

}


function AlbumMenu(model, conf){

    var self = this;

    var $view = null;
    var $detailsButton = null;
    var $fullscreenButton = null;
    var downloadButton = null;
    var $adminButton = null;

    function init(){
        $view = conf.view;
        $detailsButton = conf.detailsButton;
        $fullscreenButton = conf.fullscreenButton;
        $downloadButton = conf.downloadButton;
        $adminButton = conf.adminButton || null;

        watch(model, "selectedPictureIndex", function(){
            showHideMenu();
            showHideButtons();
        });

        $detailsButton.click(function(event){
            event.preventDefault();
            showHideDetails();
        });

        $fullscreenButton.click(function(event){
            event.preventDefault();
            openCloseFullscreen();
        });

        Fullscreen.onchange(function(event){
            $fullscreenButton.toggleClass("selected", Fullscreen.isActive());
        });

        if ($downloadButton) $downloadButton.click(function(event){
            event.preventDefault();
            downloadPhoto();
        });

        if ($adminButton) $adminButton.click(function(){
                openAdmin();
        })
        showHideButtons();
        controlMenuBasedOnMouseMovement();
    }

    function showHideMenu(){
        var show = (model.selectedPictureIndex !== null);
        toggleMenu(show);
    }

    function toggleMenu(show){
        $view.toggleClass("headroom--pinned", !show)
            .toggleClass("headroom--top", !show)
            .toggleClass("headroom--not-top", show)
            .toggleClass("headroom--unpinned", show);
    }

    function showHideButtons(){
        var pictureSelected = (model.selectedPictureIndex !== null);
        if ($fullscreenButton) $fullscreenButton.toggle(pictureSelected);
        if ($detailsButton) $detailsButton.toggle(pictureSelected);
        if ($downloadButton) $downloadButton.toggle(pictureSelected);
        if ($adminButton) $adminButton.toggle(pictureSelected);
        if (!pictureSelected) model.detailsOn = false;
    }

    function showHideDetails(){
        model.detailsOn = !model.detailsOn;
        $detailsButton.toggleClass("selected", model.detailsOn);
    }

    function openCloseFullscreen(){
        if (Fullscreen.isActive()){
            Fullscreen.close();
        } else {
            Fullscreen.open(document.getElementById("content"));
        }
    }

    function controlMenuBasedOnMouseMovement(){
        var timer = null;
        function mouseStoppedCallback(){
            timer = setTimeout(function(){
                if (model.selectedPictureIndex !== null) toggleMenu(true);
            }, 1500);
        }
        $(document).mousemove(function( event ) {
            clearTimeout(timer);
            if (model.selectedPictureIndex !== null) toggleMenu(false);
            mouseStoppedCallback();
        });
        mouseStoppedCallback();
    }

    function downloadPhoto(){
        if (model.selectedPictureIndex == null) return;
        location.href=model.pictures[model.selectedPictureIndex].url+"?download";
    }

    function openAdmin(){
        location.href="/admin/album" + model.path
    }

    init();
}