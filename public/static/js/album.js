function AlbumController(prefix, dataPrefix){

    this.URL_PREFIX = prefix
    this.URL_DATA_PREFIX = dataPrefix

    var currentAlbum = null
    
    var beforeHandler = null
    var resultHandler = null
    var failHandler = null
    
    var self = this

    function init(){
        addEventListener()
    }

    function addEventListener(){
        $(window).bind('popstate', function(event){
            self.changeCurrentAlbum()
        })
    }

    this.changeAlbum = function(album){
        if (currentAlbum == album){
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
        if (currentAlbum == album){
            return;
        }
        beforeHandler()
        currentAlbum = album
        url = self.URL_DATA_PREFIX + album

        $.get(url, function(content) {
            if (resultHandler){
                resultHandler(content)
            }
        }).fail(function(status){
            if (failHandler){
                failHandler(status)
            }
        });
    }

    this.before = function(handler){
        beforeHandler = handler;
        return this
    }
    
    this.result = function(handler){
        resultHandler = handler;
        return this;
    }

    this.fail = function(handler){
        failHandler = handler;
        return this;
    }

    this.getCurrentAlbum = function(){
        return currentAlbum;
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
            fullAlbum = albumController.getCurrentAlbum() + albuns[i] + "/"
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
            style=""
            html += "<div class=\"photo\" style=\"width: "+(p.newWidth-4)+"px; height: "+(p.newHeight-4)+"px;\"></div>"
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
            $photos.find("div:eq("+index+")")
                .css("background-image", "url("+this.src+")")
                .click(function(){
                    highlight.displayPicture($(this).data("picture"))
                })
            index++
            loadNextPicture()
        }
        function loadNextPicture(){
            if (run != self.run || index >= pictures.length){
                return
            }
            $photos.find("div:eq("+index+")").data("picture", pictures[index])
            image.src = pictures[index].thumb
        }
        loadNextPicture()
    }

    this.resizePictures = function(pictures){
        if (!pictures){
            return;
        }
        var resize = new Resize(pictures)
        resize.doResize($photos.width(), $(window).height())
        $photos.find("div").each(function(index, item){
            p = pictures[index]
            $(this).css("width", (p.newWidth-4)).css("height", (p.newHeight-4))
        })
    }

    init()
}

function AlbumAdminView(albumController, highlight, $albuns, $photos, $loading){

    var albumView = new AlbumView(albumController, highlight, $albuns, $photos, $loading);

    albumView.displayPictures = function(pictures){
        var resize = new Resize(pictures)
        resize.doResize($photos.width(), $(window).height())

        html = ""
        for (i in pictures){
            var p = pictures[i]
            style=""
            html += "<div class=\"photo\" style=\"width: "+(p.newWidth-4)+"px; height: "+(p.newHeight-4)+"px;\">"
            html += "<a class=\"star star-off\" href='#'><span>Star</span></a>"
            html += "</div>"
        }
        $photos
            .html(html)
            .filter("a.star").click(function(event){
                alert("...")
                event.preventDefault();
            })
        
        albumView.lazyLoadPictures(pictures)
    }

    return albumView
}