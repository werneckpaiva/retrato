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


function AlbumView(controller, highlightController, $albumNode, $photoNode, $loadingNode){

    var albumController = controller;

    var $albuns = $albumNode;
    var $photos = $photoNode;
    var highlight = highlightController
    var $loading = $loadingNode

    var pictures = null
    var self = this

    this.run = 0

    function init(){
        addEventListener()
        albumController.changeCurrentAlbum()
    }

    function addEventListener(){
        $(window).resize(function(){
            resizePictures(pictures)
        })
        albumController
            .before(function(){
                cleanContent()
                $loading.show();
            })
            .result(function(content){
                onLoadAlbum(content)
            })
            .fail(function(status){
                displayInvalidAlbum()
            })
        
    }

    function onLoadAlbum(content){
        $loading.hide();
        if (!content){
            displayInvalidAlbum()
        } else {
            pictures = content.pictures
            displayAlbuns(content.albuns)
            displayPictures(content.pictures)
        }
    }

    function cleanContent(){
        highlight.closePicture()
        $("#photos").html("")
        $loading.hide();
    }

    function displayAlbuns(albuns){
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

    function displayInvalidAlbum(){
        cleanContent()
    }

    function displayPictures(pictures){
        var resize = new Resize(pictures)
        resize.doResize($("#photos").width(), $(window).height())

        html = ""
        for (i in pictures){
            var p = pictures[i]
            style=""
                // : ; 
            html += "<div class=\"photo\" style=\"width: "+(p.newWidth-4)+"px; height: "+(p.newHeight-4)+"px;\"></div>"
        }
        $("#photos").html(html)
        lazyLoadPictures(pictures)
    }

    function lazyLoadPictures(pictures){
        var index = 0;
        self.run++
        var run = self.run
        var image = new Image()
        image.onload = function(){
            var url = 
            $("#photos div:eq("+index+")")
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
            $("#photos div:eq("+index+")").data("picture", pictures[index])
            image.src = pictures[index].thumb
        }
        loadNextPicture()
    }

    function resizePictures(pictures){
        if (!pictures){
            return;
        }
        var resize = new Resize(pictures)
        resize.doResize($("#photos").width(), $(window).height())
        $("#photos div").each(function(index, item){
            p = pictures[index]
            $(this).css("width", (p.newWidth-4)).css("height", (p.newHeight-4))
        })
    }

    init()
}