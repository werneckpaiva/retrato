function AlbumController(prefix, dataPrefix){

    this.URL_PREFIX = prefix
    this.URL_DATA_PREFIX = dataPrefix

    var currentAlbumPath = null
    this.currentAlbum = null

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
        if (currentAlbumPath == album){
            return;
        }
        changeUrl(album)
        loadAlbum(album)
    }

    this.changeCurrentAlbum = function(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(self.URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        loadAlbum(albumPath)
    }

    function changeUrl(album){
        history.pushState(null, null, self.URL_PREFIX+album)
    }

    function loadAlbum(album){
        if (currentAlbumPath == album){
            return;
        }
        self.$eventManager.trigger("before");
        currentAlbumPath = album
        url = self.URL_DATA_PREFIX + album

        $.get(url, function(content) {
            self.currentAlbum = content
            self.$eventManager.trigger("result", content);
        }).fail(function(status){
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

    this.getCurrentAlbumPath = function(){
        return currentAlbumPath;
    }

    init()
}


function AlbumView(albumController, highlight, $albuns, $photos, $loading){

    var pictures = null
    var self = this

    this.run = 0

    function init(){
        addEventListener()
        albumController.changeCurrentAlbum()
    }

    function addEventListener(){
        $(window).resize(function(){
            self.resizePictures(pictures)
        })
        albumController
            .before(function(){
                self.cleanContent()
                $loading.show();
            })
            .result(function(content){
                onLoadAlbum(content)
            })
            .fail(function(status){
                self.displayInvalidAlbum()
            })
        
    }

    function onLoadAlbum(content){
        $loading.hide();
        if (!content){
            self.displayInvalidAlbum()
        } else {
            pictures = content.pictures
            self.displayAlbuns(content.albuns)
            self.displayPictures(content.pictures)
        }
    }

    this.cleanContent = function(){
        highlight.closePicture()
        $photos.html("")
        $loading.hide();
    }

    this.displayAlbuns = function(albuns){
        if (!albuns || albuns.length == 0){
            $("#albuns").html("").hide();
            return;
        }
        html = "<ul>"
        for (i in albuns){
            fullAlbum = albumController.getCurrentAlbumPath() + albuns[i] + "/"
            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+albumController.URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
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

    this.displayInvalidAlbum = function (){
        cleanContent()
    }

    this.displayPictures = function(pictures){
        var resize = new Resize(pictures)
        resize.doResize($photos.width(), $(window).height())

        html = ""
        for (i in pictures){
            var p = pictures[i]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            html += "<div class=\"photo-container\" style=\"width: "+width+"px; height: "+height+"px;\">"
            html += "<img class=\"photo\" width=\""+width+"\" height=\""+height+"\" /></div>"
        }
        $photos.html(html)
        self.lazyLoadPictures(pictures)
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
                    highlight.displayPicture($(this).parent().data("picture"))
                })
            index++
            loadNextPicture()
        }
        function loadNextPicture(){
            if (run != self.run || index >= pictures.length){
                return
            }
            $photos.find(".photo-container:eq("+index+")").data("picture", pictures[index])
            image.src = pictures[index].thumb
        }
        loadNextPicture()
    }

    this.resizePictures = function(pictures){
        if (!pictures){
            return;
        }
        var resize = new Resize(pictures)
        resize.HEIGHT_PROPORTION = self.HEIGHT_PROPORTION
        resize.doResize($photos.width(), $(window).height())
        $photos.find(".photo-container").each(function(index, item){
            p = pictures[index]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            $(this).css("width", width).css("height", height)
            $(this).find(".photo").attr("width", width).attr("height", height)
        })
    }

    this.changeProportion = function(proportion){
        self.HEIGHT_PROPORTION = proportion
        self.resizePictures(pictures)
    }
    
    init()
}