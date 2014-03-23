function AlbumAdminController(prefix, dataPrefix){
    var controller = new AlbumController(prefix, dataPrefix)
    
    controller.changeVisibility = function(visibility){
        data = {
            'visibility': visibility
        }
        url = controller.URL_DATA_PREFIX + controller.getCurrentAlbumPath()
        $.post(url, data, function(content) {
            controller.$eventManager.trigger("visibility.result", content);
        }).fail(function(status, s){
            controller.$eventManager.trigger("visibility.fail");
        });
    }
    
    return controller;
}

function AlbumAdminView(albumController, highlight, $albumName, $albuns, $photos, $loading){

    var albumView = new AlbumView(albumController, highlight, $albuns, $photos, $loading);

    function init(){
        addEventListener()
    }

    function addEventListener(){
        albumController.result(function(albumData){
            showAlbumData(albumData)
        });
        $albumName.find(".star").click(function(event){
            var album = albumController.currentAlbum
            if (album.visibility == 'public'){
                albumController.changeVisibility('private');
            } else {
                albumController.changeVisibility('public');
            }
            event.preventDefault();
        })
        albumController.$eventManager.bind('visibility.result', function(event, content){
            albumController.currentAlbum.visibility = content.visibility
            showAlbumData(content)
        })
        albumController.$eventManager.bind('visibility.fail', function(){
            alert("Can't change album visibility")
        })
    }

    function showAlbumData(albumData){
        $albumName.find(".input").html(albumData.album);
        if (albumData.visibility == "public"){
            $("#album-name .star").addClass("star-on").removeClass("star-off")
        } else {
            $("#album-name .star").addClass("star-off").removeClass("star-on")
        }
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