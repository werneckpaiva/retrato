function AlbumAdminModel(albumDelegate){

    var model = new AlbumModel(albumDelegate);

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

    model.setAlbumCover = function(pictureIndex){
        albumDelegate.setAlbumCover(model.pictures[pictureIndex].url, 
                function(result){
                    model.loading = false
                    model.cover = model.pictures[pictureIndex]
                    callWatchers(model, "cover");
                }, 
                function(error){
                    model.loading = false
                });
        model.loading = true
    }

    model.revokeToken = function(){
        albumDelegate.revokeToken(model.path,
                function(result){
                    model.loading = false
                    model.token = result.token
                },
                function(error){
                    model.loading = false
                });
        model.loading = true
    }
    
    return model;
}

function AlbumAdminDelegate(){

    var delegate = new AlbumAjaxDelegate();

    delegate.changeVisibility = function(albumPath, visibility, resultHandler, failHandler){
        var data = {
                'visibility': visibility
        }
        var url = Settings.URL_DATA_PREFIX + albumPath;
        url = StringUtil.sanitizeUrl(url);
        $.post(url, data, function(result) {
            resultHandler(result)
        }, "json").fail(function(status, s){
            failHandler(status)
        }, "json");
    }

    delegate.changePictureVisibility = function(picturePath, visibility, resultHandler, failHandler){
        var data = {
                'visibility': visibility
        }
        var url = picturePath;
        $.post(url, data, function(result) {
            resultHandler(result)
        }, "json").fail(function(status, s){
            failHandler(status)
        }, "json");
    }

    delegate.setAlbumCover = function(picturePath, resultHandler, failHandler){
        var data = {
                'cover': true
        }
        var url = picturePath;
        $.post(url, data, function(result) {
            resultHandler(result)
        }, "json").fail(function(status, s){
            failHandler(status)
        }, "json");
    }

    delegate.revokeToken = function(albumPath, resultHandler, failHandler){
        var data = {
                'action': 'revokeToken'
        }
        var url = Settings.URL_DATA_PREFIX + albumPath;
        url = StringUtil.sanitizeUrl(url);
        $.post(url, data, function(result) {
            resultHandler(result)
        }, "json").fail(function(status, s){
            failHandler(status)
        }, "json");
    }

    return delegate;
}

function AlbumAdminMenu(model, conf){

    var albumMenu = new AlbumMenu(model,conf);
    var $publishButton = null;

    function init(){
        $publishButton = conf.publishButton;
        $revokeTokenButton = conf.revokeTokenButton;

        $publishButton.click(function(event){
            togglePublish();
        });

        $revokeTokenButton.click(function(event){
            revokeToken();
        })
        
        watch(model, "visibility", function(){
            showPublishButtonStatus();
        });

        watch(model, "selectedPictureIndex", function(){
            showPublishButtonStatus();
        });

        watch(model, "pictures", function(){
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

    function revokeToken(){
        if (confirm("Tem certeza que deseja criar um novo token para este album?")){
            model.revokeToken();
        }
    }
    
    init();
    return albumMenu;
}


function AlbumAdminPhotos(model, conf){

    var albumPhotos = new AlbumPhotos(model, conf);
    var $view = null;
    var $viewList = null;

    var self = this;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view

        watch(model, "cover", function(prop, action, newvalue, oldvalue){
            var picturesChanged = Array.isArray(newvalue);
            albumPhotos.displayPictures(picturesChanged);
        });
    }

    var _displayPictures = albumPhotos.displayPictures;
    albumPhotos.displayPictures = function(picturesChanged){
        _displayPictures(picturesChanged);
        $viewList.find('.photo-container').each(function(i, element){
            $element = $(element);
            setPicturePrivatePublicControl($element, i, picturesChanged);
            setPictureCoverControl($element, i, picturesChanged);
        })
    }

    function setPicturePrivatePublicControl($element, i, picturesChanged){
        var isPrivate = (model.pictures[i].visibility == "private");
        $element.toggleClass("private", isPrivate)
        if (picturesChanged){
            var publishBtn = $element.find(".photo-menu .publish")
            publishBtn.data("index", i)
            publishBtn.click(function(event){
                event.preventDefault();
                var dataIndex = $(this).data("index");
                var pictureVisibility = model.pictures[dataIndex].visibility
                if (pictureVisibility == "public"){
                    model.changePictureVisibility(dataIndex, "private")
                } else if (pictureVisibility == "private") {
                    model.changePictureVisibility(dataIndex, "public")
                }
            })
        }
    }

    function setPictureCoverControl($element, i, picturesChanged){
        var isCover = false;
        if (model.cover){
            isCover = model.cover.filename == model.pictures[i].filename;
            if (isCover) console.log(model.pictures[i].filename);
        }
        $element.toggleClass("cover", isCover)
        if (picturesChanged){
            var coverBtn = $element.find(".photo-menu .set-cover")
            coverBtn.data("index", i)
            coverBtn.click(function(event){
                event.preventDefault();
                var dataIndex = $(this).data("index");
                model.setAlbumCover(dataIndex);
            })
        }
    }

    var _resizePictures = albumPhotos.resizePictures;
    albumPhotos.resizePictures = function(){
        _resizePictures();
    }
    
    init();
    return albumPhotos;
}

function AlbumAdminBreadcrumb(model, conf){
    
    var albumBreadcrumb = new AlbumBreadcrumb(model, conf);

    var _super_getCurrentContext = albumBreadcrumb.getCurrentContext;

    function init(){
        watch(model, "token", function(){
            albumBreadcrumb.updatePath();
        });
    }

    albumBreadcrumb.getCurrentContext = function(){
        var context = _super_getCurrentContext.call(albumBreadcrumb);
        if (context.parts.length > 0 && model.token !== null){
            var part = context.parts.pop();
            part.url = "/album" + model.path + "?token=" + model.token;
            part.external = true;
            context.parts.push(part);
        }
        return context;
    }

    init();

    return albumBreadcrumb;
}

