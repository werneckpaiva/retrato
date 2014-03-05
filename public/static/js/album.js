function AlbumPage(){

    var currentAlbum = null
    var self = this

    URL_PREFIX ="/album"
    URL_DATA_PREFIX = "/album-data"

    function init(){
        addEventListener()
        changeCurrentAlbum()
    }

    function addEventListener(){
        $(window).bind('popstate', function(event){
            changeCurrentAlbum()
        })
    }

    function changeCurrentAlbum(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        self.loadAlbum(albumPath)
    }

    function changeToAlbum(album){
        history.pushState(null, null, URL_PREFIX+album)
    }

    this.loadAlbum = function(album){
        if (currentAlbum == album){
            return;
        }
        currentAlbum = album
        url = URL_DATA_PREFIX + album
        $.get(url, function(content) {
            console.log(content)
            if (!content){
                displayInvalidAlbum()
            } else {
                displayAlbuns(content.albuns)
                displayPictures(content.pictures)
            }
        });
    }

    function displayAlbuns(albuns){
        html = "<ul>"
        for (i in albuns){
            fullAlbum = currentAlbum + albuns[i]
            html += "<li><a data-album=\""+fullAlbum+"\" href=\""+URL_PREFIX+fullAlbum+"\">"+albuns[i]+"</a></li>"
        }
        html += "</ul>"

        $("#albuns")
            .html(html)
            .find("a").click(function(){
                changeUrl($(this).attr("data-album"))
            })
    }

    function displayPictures(pictures){
        html = ""
        for (i in pictures){
            html += "<div><img src=\""+pictures[i].url  +"\" /></div>"
        }
        html += ""
        $("#photos").html(html)
    }

    init()
}