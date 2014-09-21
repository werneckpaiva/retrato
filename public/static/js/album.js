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

    this.updatePath = function(){
        var parts = model.path.split("/");
        if (parts[parts.length - 1]===""){
            parts.pop();
        }
        if (model.selectedPictureIndex !== null){
            var p = model.pictures[model.selectedPictureIndex];
            parts.push(p.filename);
        }
        var partial = '/';
        var content = Mustache.render(templateHome, {
            url: StringUtil.sanitizeUrl(Settings.URL_PREFIX + '/')
        });
        for (var i=1; i<parts.length; i++){
            partial += parts[i] + '/';
            params = {};
            if (i < parts.length - 1){
                params.url = StringUtil.sanitizeUrl(Settings.URL_PREFIX + partial);
            }
            params.name = StringUtil.humanizeName(parts[i]);
            content += Mustache.render(template, params);
        }
        $viewList.html(content);
        enableAsynchronous();
    };

    function enableAsynchronous(){
        $viewList.find("a").click(function(){
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
        var currentAlbumPath = location.pathname;
        var newPath = Settings.URL_PREFIX + model.path;
        if (currentAlbumPath == newPath){
            return;
        }
        newPath = StringUtil.sanitizeUrl(newPath);
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