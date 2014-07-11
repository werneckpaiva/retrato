var Settings = {
    URL_PREFIX: "/album",
    URL_DATA_PREFIX: "/admin/album/api"
}

var StringUtil = {
    sanitizeUrl: function(url){
        url = url.replace(/([^:])[\/]+/g, '$1/');
        return url
    },
    humanizeName: function(name){
        name = name.replace(/_/g, " ");
        return name
    }
}

function AlbumModel(albumDelegate){

    var delegate = albumDelegate
    var self = this

    this.path = null;
    this.albuns = [];
    this.pictures = [];
    this.visibility = null;

    this.loading = false;

    this.selectedPictureIndex = 0;
    this.highlightOn = false;

    this.loadAlbum = function(albumPath){
        albumPath = albumPath.replace(Settings.URL_PREFIX, '')
        console.log(albumPath);
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
    }

    function loadAlbumFailHandler(error){
        self.loading = false
    }

    return this;
}

function AlbumDelegate(){

    this.get = function(albumPath, resultHandler, failHandler){
        var url = Settings.URL_DATA_PREFIX + albumPath;
        $.get(url, function(result) {
            resultHandler(result)
        }).fail(function(status){
            failHandler(status)
        });
    }
}

function Loading(model, $view){

    function init(){
        watch(model, "loading", function(){
            $view.toggle(model.loading);
        });
        $view.hide();
    }

    init();
}

function AlbumNavigator(model, $view, albumTpl){

    var template = null;

    function init(){
        watch(model, "albuns", function(){
            displayAlbuns();
        });

        template = albumTpl;
    }

    function getAlbumUrl(albumName){
        var url = Settings.URL_PREFIX + model.path + '/' + albumName;
        url = StringUtil.sanitizeUrl(url);
        return url;
    }
    
    function displayAlbuns(){
        $viewList = $view.find(".list");
        $viewList.empty();
        if(!model.albuns || model.albuns.length == 0){
            $view.hide();
            return;
        }
        $view.show();
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
        $view.find("a").click(function(){
            model.loadAlbum($(this).attr("href"))
            return false;
        })
    }
    
    init();
}

function AlbumBreadcrumb(model, $view, breadcrumbHomeTpl, breadcrumbTpl){

    var self = this;
    var homeTemplate = null;
    var template = null;

    function init(){
        watch(model, "path", function(){
            self.updatePath()
        });
        homeTemplate = breadcrumbHomeTpl;
        template = breadcrumbTpl;
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
        var partial = '/'
        var content = Mustache.render(homeTemplate, {
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
        $view.html(content)
        enableAsynchronous();
    }

    function enableAsynchronous(){
        $view.find("a").click(function(){
            model.loadAlbum($(this).attr("href"));
            return false;
        })
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

function AlbumPhotos(model, $view, photoTpl){

    var template = null;

    function init(){
        watch(model, "pictures", function(){
            displayPictures();
        });

        template = photoTpl;
    }

    function displayPictures(){
        $view.empty();
        if(!model.pictures || model.pictures.length == 0){
            $view.hide();
            return;
        }
        $view.show();

        var resize = new Resize(model.pictures);
        resize.doResize($view.width(), $(window).height());

        content = "";
        for (var i=0; i<model.pictures.length; i++){
            var p = model.pictures[i]
            content += Mustache.render(template, {
                width: p.newWidth-4, 
                height: p.newHeight-4,
                photoUrl: p.thumb 
            });
        }
        $view.html(content);
    }

    init();
}


//function AlbumController(albumPresentationModel){
//
//    this.model = albumPresentationModel;
//
//    var self = this
//
//    this.$eventManager = $({});
//
//    function init(){
//        addEventListener()
//    }
//
//    function addEventListener(){
//        $(window).bind('popstate', function(event){
//            self.changeCurrentAlbum()
//        })
//    }
//
//    this.changeAlbum = function(album){
//        if (self.model.currentAlbumPath == album){
//            return;
//        }
//        changeUrl(album)
//        loadAlbum(album)
//    }
//
//    this.changeCurrentAlbum = function(){
//        var albumPath = location.pathname
//        albumPath = albumPath.replace(self.model.URL_PREFIX, "")
//        if (!albumPath){
//            albumPath = "/"
//        }
//        loadAlbum(albumPath)
//    }
//
//    function changeUrl(album){
//        history.pushState(null, null, self.model.URL_PREFIX+album)
//    }
//
//    function loadAlbum(album){
//        if (self.model.currentAlbumPath == album){
//            return;
//        }
//
//        Loading.show();
//        self.$eventManager.trigger("before");
//        self.model.currentAlbumPath = album
//        url = self.model.URL_DATA_PREFIX + album
//
//        $.get(url, function(content) {
//
//            self.model.currentAlbum = content
//            self.model.pictures = content.pictures
//
//            Loading.hide();
//            self.$eventManager.trigger("result", content);
//        }).fail(function(status){
//            Loading.hide();
//            self.$eventManager.trigger("fail");
//        });
//    }
//
//    this.before = function(handler){
//        self.$eventManager.bind("before", handler)
//        return this
//    }
//
//    this.result = function(handler){
//        self.$eventManager.bind("result", function(evt, content){
//            handler(content)
//        });
//        return this;
//    }
//
//    this.fail = function(handler){
//        self.$eventManager.bind("fail", handler)
//        return this;
//    }
//
//    init()
//}

//
//function AlbumView(albumPresentationModel, albumController, highlight, $albuns, $photos){
//
//    this.model = albumPresentationModel;
//    
//    var self = this
//
//    this.run = 0
//
//    this.HEIGHT_PROPORTION = 0.45
//
//    function init(){
//        addEventListener()
//        albumController.changeCurrentAlbum()
//    }
//
//    function addEventListener(){
//        $(window).resize(function(){
//            self.resizePictures()
//        })
//        watch(self.this.model, "pictures", function(){
//            onLoadAlbum()
//        });
//        
//        albumController.before(function(){
//                self.cleanContent()
//            })
//            .fail(function(status){
//                self.displayInvalidAlbum()
//            })
//    }
//
//    function onLoadAlbum(){
//        Loading.hide();
//        if (!self.model.album){
//            self.displayInvalidAlbum()
//        } else {
//            self.displayAlbuns()
//            self.displayPictures()
//        }
//    }
//
//    this.cleanContent = function(){
//        highlight.closePicture()
//        $photos.html("")
//        Loading.hide();
//    }
//
//    this.displayAlbuns = function(){
//        var albuns = self.model.albuns;
//        if (!albuns || albuns.length == 0){
//            $("#albuns").html("").hide();
//            return;
//        }
//        html = "<ul>"
//        for (i in albuns){
//            fullAlbum = self.model.currentAlbumPath + albuns[i] + "/"
//            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+self.model.URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
//        }
//        html += "</ul>"
//        $("#albuns")
//            .html(html)
//            .show()
//            .find("a").click(function(event){
//                albumController.changeAlbum($(this).attr("data-album"))
//                event.preventDefault();
//            })
//    }
//
//    this.displayPicture = function(index){
//        self.model.currentPictureIndex = index
//        highlight.displayPicture(index)
//    }
//
//    this.displayInvalidAlbum = function (){
//        cleanContent()
//    }
//
//    this.displayPictures = function(pictures){
//        var resize = new Resize(self.model.pictures)
//        resize.doResize($photos.width(), $(window).height())
//
//        highlight.setPictures(self.model.pictures);
//
//        html = ""
//        for (i in self.model.pictures){
//            var p = self.model.pictures[i]
//            var width = (p.newWidth-4);
//            var height = (p.newHeight-4);
//            html += "<div class=\"photo-container\" style=\"width: "+width+"px; height: "+height+"px;\">"
//            html += "<img class=\"photo\" width=\""+width+"\" height=\""+height+"\" /></div>"
//        }
//        $photos.html(html)
//        $photos.attr("data-album-name", self.model.currentAlbum.album.substring(1, self.model.currentAlbum.album.length-1).split("/").join(" / ") )
//
//        self.lazyLoadPictures(self.model.pictures)
//    }
//
//    this.lazyLoadPictures = function(pictures){
//        var index = 0;
//        self.run++
//        var run = self.run
//        var image = new Image()
//        image.onload = function(){
//            var url =
//            $photos.find(".photo-container:eq("+index+") .photo")
//                .attr("src", this.src)
//                .show()
//                .click(function(){
//                    self.displayPicture($(this).parent().data("index"))
//                })
//            index++
//            loadNextPicture()
//        }
//        function loadNextPicture(){
//            if (run != self.run || index >= pictures.length){
//                return
//            }
//            $photos.find(".photo-container:eq("+index+")").data("index", index)
//            image.src = pictures[index].thumb
//        }
//        loadNextPicture()
//    }
//
//    this.resizePictures = function(){
//        if (!self.model.pictures){
//            return;
//        }
//        var resize = new Resize(self.model.pictures)
//        resize.HEIGHT_PROPORTION = self.HEIGHT_PROPORTION
//        resize.doResize($photos.width(), $(window).height())
//        $photos.find(".photo-container").each(function(index, item){
//            p = self.model.pictures[index]
//            var width = (p.newWidth-4);
//            var height = (p.newHeight-4);
//            $(this).css("width", width).css("height", height)
//            $(this).find(".photo").attr("width", width).attr("height", height)
//        })
//    }
//
//    this.changeProportion = function(proportion){
//        self.HEIGHT_PROPORTION = proportion
//        self.resizePictures()
//    }
//    
//    init()
//}