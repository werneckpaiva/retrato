function AlbumAdminController(prefix, dataPrefix){
    var controller = new AlbumController(prefix, dataPrefix)
    
    controller.makeAlbumPrivate = function(){
        $.post()
    }
    
    controller.makeAlbumPublic = function(){
        alert("public")
    }
    
    return controller;
}

function AlbumAdminView(albumController, highlight, $albumName, $albuns, $photos, $loading){

    var albumView = new AlbumView(albumController, highlight, $albuns, $photos, $loading);

    function init(){
        addEventListener()
    }

    function addEventListener(){
        albumController.result(function(content){
            $albumName.find(".input").html(content.album);
        });
        $albumName.find(".star-on").click(function(){
            albumController.makeAlbumPrivate();
        })
        $albumName.find(".star-off").click(function(){
            albumController.makeAlbumPublic();
        })
    }

    albumView.displayPictures = function(pictures){
        var resize = new Resize(pictures)
        resize.doResize($photos.width(), $(window).height())

        html = ""
        for (i in pictures){
            var p = pictures[i]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            html += "<div class=\"photo-container\" style=\"width: "+width+"px; height: "+height+"px;\">"
            html += "<a class=\"star star-off\" href='#'><span>Star</span></a>"
            html += "<img class=\"photo\" width=\""+width+"\" height=\""+height+"\" />"
            html += "</div>"
        }
        $photos
            .html(html)
            .find("a.star").click(function(event){
                event.preventDefault();
            })
        
        albumView.lazyLoadPictures(pictures)
    }

    init()

    return albumView
}