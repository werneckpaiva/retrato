function AlbumAdminModel(albumDelegate){
    var model = AlbumModel(albumDelegate);

    model.changeVisibility = function(visibility){
        albumDelegate.changeVisibility(model.path, visibility, 
                function(result){
                    model.loading = false
                    model.visibility = result.visibility;
                }, 
                function(error){
                    model.loading = false
                });
        model.loading = true
    }

    model.changePictureVisibility = function(pictureIndex, visibility){
        albumDelegate.changePictureVisibility(model.pictures[pictureIndex].url, visibility, 
                function(result){
                    model.loading = false
                    model.pictures[pictureIndex].visibility = result.visibility;
                    callWatchers(model, "pictures");
                }, 
                function(error){
                    model.loading = false
                });
        model.loading = true
    }

    return model;
}

function AlbumAdminDelegate(){

    var delegate = new AlbumDelegate();

    delegate.changeVisibility = function(albumPath, visibility, resultHandler, failHandler){
        var data = {
                'visibility': visibility
        }
        var url = Settings.URL_DATA_PREFIX + albumPath;
        $.post(url, data, function(result) {
            resultHandler(result)
        }).fail(function(status, s){
            failHandler(status)
        });
    }

    delegate.changePictureVisibility = function(picturePath, visibility, resultHandler, failHandler){
        var data = {
                'visibility': visibility
        }
        var url = "/admin" + picturePath; // TODO: Move to another URL
        $.post(url, data, function(result) {
            resultHandler(result)
        }).fail(function(status, s){
            failHandler(status)
        });
    }
    return delegate;
}

function AlbumAdminMenu(model, conf){

    var albumMenu = new AlbumMenu(model,conf);
    var $publishButton = null;

    function init(){
        $publishButton = conf.publishButton;

        $publishButton.click(function(event){
            event.preventDefault();
            togglePublish();
        });

        watch(model, "visibility", function(){
            showPublishButtonStatus();
        });

        watch(model, "selectedPictureIndex", function(){
            showPublishButtonStatus();
        });

        watch(model, "pictures", function(){
            console.log("pictures changed")
            showPublishButtonStatus();
        }, 2);

        showPublishButtonStatus()
    }

    function togglePublish(){
        if (model.selectedPictureIndex == null){
            var albumVisibility = model.visibility;
            if (albumVisibility=="public"){
                model.changeVisibility("private");
            } else if (albumVisibility=="private"){
                model.changeVisibility("public");
            }
        } else {
            var pictureVisibility = model.pictures[model.selectedPictureIndex].visibility
            if (pictureVisibility == "public"){
                model.changePictureVisibility(model.selectedPictureIndex, "private")
            } else if (pictureVisibility == "private") {
                model.changePictureVisibility(model.selectedPictureIndex, "public")
            }
        }
    }

    function showPublishButtonStatus(){
        if (model.selectedPictureIndex == null){
            if (model.visibility=="public"){
                $publishButton.addClass("selected");
            } else if (model.visibility=="private"){
                $publishButton.removeClass("selected");
            }
        } else {
            
            var pictureVisibility = model.pictures[model.selectedPictureIndex].visibility
            if (pictureVisibility=="public"){
                $publishButton.addClass("selected");
            } else if (pictureVisibility=="private"){
                $publishButton.removeClass("selected");
            }
        }
    }

    init();
    return albumMenu;
}


//function AlbumAdminController(albumPresentationModel){
//    var controller = new AlbumController(albumPresentationModel)
//    
//    controller.changeVisibility = function(visibility){
//        data = {
//            'visibility': visibility
//        }
//        url = albumPresentationModel.URL_DATA_PREFIX + controller.getCurrentAlbumPath()
//        $.post(url, data, function(content) {
//            controller.$eventManager.trigger("visibility.result", content);
//        }).fail(function(status, s){
//            controller.$eventManager.trigger("visibility.fail");
//        });
//    }
//    
//    return controller;
//}
//
//function AlbumAdminView(albumController, highlight, $albumName, $albuns, $photos, $loading, albumPresentationModel){
//
//    var albumView = new AlbumView(albumController, highlight, $albuns, $photos, $loading, albumPresentationModel);
//
//    function init(){
//        addEventListener()
//    }
//
//    function addEventListener(){
//        albumController.result(function(albumData){
//            showAlbumData(albumData)
//        });
//        $albumName.find(".star").click(function(event){
//            var album = albumController.currentAlbum
//            if (album.visibility == 'public'){
//                albumController.changeVisibility('private');
//            } else {
//                albumController.changeVisibility('public');
//            }
//            event.preventDefault();
//        })
//        albumController.$eventManager.bind('visibility.result', function(event, content){
//            albumController.currentAlbum.visibility = content.visibility
//            showAlbumData(content)
//        })
//        albumController.$eventManager.bind('visibility.fail', function(){
//            alert("Can't change album visibility")
//        })
//    }
//
//    function showAlbumData(albumData){
//        $albumName.find(".input").html(albumData.album);
//        if (albumData.visibility == "public"){
//            $("#album-name .star").addClass("star-on").removeClass("star-off")
//        } else {
//            $("#album-name .star").addClass("star-off").removeClass("star-on")
//        }
//    }
//
//    albumView.displayPictures = function(pictures){
//        var resize = new Resize(pictures)
//        resize.doResize($photos.width(), $(window).height())
//
//        highlight.setPictures(pictures);
//
//        html = ""
//        for (i in pictures){
//            var p = pictures[i]
//            var width = (p.newWidth-4);
//            var height = (p.newHeight-4);
//            html += "<div class=\"photo-container\" style=\"width: "+width+"px; height: "+height+"px;\">"
//            html += "<a class=\"star star-off\" href='#'><span>Star</span></a>"
//            html += "<img class=\"photo\" width=\""+width+"\" height=\""+height+"\" />"
//            html += "</div>"
//        }
//        $photos
//            .html(html)
//            .find("a.star").click(function(event){
//                event.preventDefault();
//            })
//        
//        albumView.lazyLoadPictures(pictures)
//    }
//
//    init()
//
//    return albumView
//}