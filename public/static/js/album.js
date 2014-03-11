function AlbumPage(h){

    var currentAlbum = null
    var pictures = null
    var self = this

    var highlight = h

    this.run = 0

    URL_PREFIX ="/album"
    URL_DATA_PREFIX = "/album-data"

    function init(){
        addEventListener()
        changeCurrentAlbum()
    }

    function addEventListener(){
        $(window)
            .bind('popstate', function(event){
                changeCurrentAlbum()
            })
            .resize(function(){
                resizePictures(pictures)
            })
        
    }

    function changeCurrentAlbum(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        loadAlbum(albumPath)
    }

    function changeUrl(album){
        history.pushState(null, null, URL_PREFIX+album)
    }

    this.changeAlbum = function(album){
        if (currentAlbum == album){
            return;
        }
        changeUrl(album)
        loadAlbum(album)
    }

    function loadAlbum(album){
        if (currentAlbum == album){
            return;
        }
        cleanContent()
        $("#loading").show();
        currentAlbum = album
        url = URL_DATA_PREFIX + album
        $.get(url, function(content) {
            $("#loading").hide();
            if (!content){
                displayInvalidAlbum()
            } else {
                pictures = content.pictures
                displayAlbuns(content.albuns)
                displayPictures(content.pictures)
            }
        });
    }

    function cleanContent(){
        $("#photos").html("")
    }

    function displayAlbuns(albuns){
        if (!albuns || albuns.length == 0){
            $("#albuns").html("").hide();
            return;
        }
        html = "<ul>"
        for (i in albuns){
            fullAlbum = currentAlbum + albuns[i] + "/"
            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
        }
        html += "</ul>"
        $("#albuns")
            .html(html)
            .show()
            .find("a").click(function(event){
                self.changeAlbum($(this).attr("data-album"))
                event.preventDefault();
            })
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