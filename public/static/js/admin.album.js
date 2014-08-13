function AlbumAdminModel(albumDelegate){
    var model = AlbumModel(albumDelegate);

    model.changeVisibility = function(visibility){
        albumDelegate.changeVisibility(model.path, visibility, 
                function(result){
                    model.loading = false
                    model.visibility = result.visibility;
                    model.loadAlbum(model.path)
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


function AlbumAdminPhotos(model, conf){

    var albumPhotos = new AlbumPhotos(model, conf);
    var $view = null;
    var $viewList = null;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view
    }

    var _displayPictures = albumPhotos.displayPictures;
    albumPhotos.displayPictures = function(){
        _displayPictures();
        $viewList.find('.photo-container').each(function(i, element){
            var isPrivate = (model.pictures[i].visibility == "private");
            $element = $(element)
            $element.toggleClass("private", isPrivate)
            var photoShare = $element.find(".photo-share")
            photoShare.data("index", i)
            photoShare.click(function(){
                var dataIndex = $(this).data("index")
                model.selectedPictureIndex = dataIndex;
                console.log(dataIndex)
            })
            
        })
    }

    var _resizePictures = albumPhotos.resizePictures;
    albumPhotos.resizePictures = function(){
        _resizePictures();
        
    }
    
    init();
    return albumPhotos;
}