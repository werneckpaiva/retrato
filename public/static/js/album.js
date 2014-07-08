function AlbumPresentationModel(){

    this.URL_PREFIX = null;
    this.URL_DATA_PREFIX = null;

    this.album = null;
    this.albuns = [];
    this.pictures = [];

    this.currentAlbumPath = null;
    this.currentAlbum = null;
    this.currentPictureIndex = 0;

    this.loading = false;

    this.highlightOpened = false;
    this.highlightIndex = null;
}

var Loading = {
    view: null,

    setView: function(view){
        this.view = view;
    },

    show: function (){
        if (this.view) this.view.show()
    },

    hide: function (){
        if (this.view) this.view.hide()
    }
}

function AlbumController(albumPresentationModel){

    this.model = albumPresentationModel;

    var self = this

    this.$eventManager = $({});

    function init(){
        addEventListener()
    }

    function addEventListener(){
        $(window).bind('popstate', function(event){
            self.changeCurrentAlbum()
        })
    }

    this.changeAlbum = function(album){
        if (self.model.currentAlbumPath == album){
            return;
        }
        changeUrl(album)
        loadAlbum(album)
    }

    this.changeCurrentAlbum = function(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(self.model.URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        loadAlbum(albumPath)
    }

    function changeUrl(album){
        history.pushState(null, null, self.model.URL_PREFIX+album)
    }

    function loadAlbum(album){
        if (self.model.currentAlbumPath == album){
            return;
        }

        Loading.show();
        self.$eventManager.trigger("before");
        self.model.currentAlbumPath = album
        url = self.model.URL_DATA_PREFIX + album

        $.get(url, function(content) {

            self.model.currentAlbum = content
            self.model.pictures = content.pictures

            Loading.hide();
            self.$eventManager.trigger("result", content);
        }).fail(function(status){
            Loading.hide();
            self.$eventManager.trigger("fail");
        });
    }

    this.before = function(handler){
        self.$eventManager.bind("before", handler)
        return this
    }

    this.result = function(handler){
        self.$eventManager.bind("result", function(evt, content){
            handler(content)
        });
        return this;
    }

    this.fail = function(handler){
        self.$eventManager.bind("fail", handler)
        return this;
    }

    init()
}


function AlbumView(albumPresentationModel, albumController, highlight, $albuns, $photos){

    this.model = albumPresentationModel;
    
    var self = this

    this.run = 0

    this.HEIGHT_PROPORTION = 0.45

    function init(){
        addEventListener()
        albumController.changeCurrentAlbum()
    }

    function addEventListener(){
        $(window).resize(function(){
            self.resizePictures()
        })
        watch(self.this.model, "pictures", function(){
            onLoadAlbum()
        });
        
        albumController.before(function(){
                self.cleanContent()
            })
            .fail(function(status){
                self.displayInvalidAlbum()
            })
    }

    function onLoadAlbum(){
        Loading.hide();
        if (!self.model.album){
            self.displayInvalidAlbum()
        } else {
            self.displayAlbuns()
            self.displayPictures()
        }
    }

    this.cleanContent = function(){
        highlight.closePicture()
        $photos.html("")
        Loading.hide();
    }

    this.displayAlbuns = function(){
        var albuns = self.model.albuns;
        if (!albuns || albuns.length == 0){
            $("#albuns").html("").hide();
            return;
        }
        html = "<ul>"
        for (i in albuns){
            fullAlbum = self.model.currentAlbumPath + albuns[i] + "/"
            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+self.model.URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
        }
        html += "</ul>"
        $("#albuns")
            .html(html)
            .show()
            .find("a").click(function(event){
                albumController.changeAlbum($(this).attr("data-album"))
                event.preventDefault();
            })
    }

    this.displayPicture = function(index){
        self.model.currentPictureIndex = index
        highlight.displayPicture(index)
    }

    this.displayInvalidAlbum = function (){
        cleanContent()
    }

    this.displayPictures = function(pictures){
        var resize = new Resize(self.model.pictures)
        resize.doResize($photos.width(), $(window).height())

        highlight.setPictures(self.model.pictures);

        html = ""
        for (i in self.model.pictures){
            var p = self.model.pictures[i]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            html += "<div class=\"photo-container\" style=\"width: "+width+"px; height: "+height+"px;\">"
            html += "<img class=\"photo\" width=\""+width+"\" height=\""+height+"\" /></div>"
        }
        $photos.html(html)
        $photos.attr("data-album-name", self.model.currentAlbum.album.substring(1, self.model.currentAlbum.album.length-1).split("/").join(" / ") )

        self.lazyLoadPictures(self.model.pictures)
    }

    this.lazyLoadPictures = function(pictures){
        var index = 0;
        self.run++
        var run = self.run
        var image = new Image()
        image.onload = function(){
            var url =
            $photos.find(".photo-container:eq("+index+") .photo")
                .attr("src", this.src)
                .show()
                .click(function(){
                    self.displayPicture($(this).parent().data("index"))
                })
            index++
            loadNextPicture()
        }
        function loadNextPicture(){
            if (run != self.run || index >= pictures.length){
                return
            }
            $photos.find(".photo-container:eq("+index+")").data("index", index)
            image.src = pictures[index].thumb
        }
        loadNextPicture()
    }

    this.resizePictures = function(){
        if (!self.model.pictures){
            return;
        }
        var resize = new Resize(self.model.pictures)
        resize.HEIGHT_PROPORTION = self.HEIGHT_PROPORTION
        resize.doResize($photos.width(), $(window).height())
        $photos.find(".photo-container").each(function(index, item){
            p = self.model.pictures[index]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            $(this).css("width", width).css("height", height)
            $(this).find(".photo").attr("width", width).attr("height", height)
        })
    }

    this.changeProportion = function(proportion){
        self.HEIGHT_PROPORTION = proportion
        self.resizePictures()
    }
    
    init()
}