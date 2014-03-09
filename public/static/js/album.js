function AlbumPage(){

    var currentAlbum = null
    var pictures = null
    var self = this

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
                if (pictures){
                    displayPictures(pictures)
                }
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
        currentAlbum = album
        url = URL_DATA_PREFIX + album
        $.get(url, function(content) {
            if (!content){
                displayInvalidAlbum()
            } else {
                pictures = content.pictures
                displayAlbuns(content.albuns)
                displayPictures(content.pictures)
            }
        });
    }

    function displayAlbuns(albuns){
        html = "<ul>"
        for (i in albuns){
            fullAlbum = currentAlbum + albuns[i] + "/"
            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
        }
        html += "</ul>"

        $("#albuns")
            .html(html)
            .find("a").click(function(event){
                self.changeAlbum($(this).attr("data-album"))
                event.preventDefault();
            })
    }

    function displayPictures(pictures){
        var resize = new Resize(pictures)
        resize.doResize($(window).width(), $(window).height())
        html = ""
        for (i in pictures){
            p = pictures[i]
            style=""
            html += "<div class=\"photo\" style=\"width: "+(p.newWidth-4)+"px; height: "+(p.newHeight-4)+"px; background-image: url("+p.url+");\"></div>"
        }
        console.log(html)
        $("#photos").html(html)
    }

    init()
}