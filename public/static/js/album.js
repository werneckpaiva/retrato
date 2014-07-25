var Settings = {
    URL_PREFIX: "/",
    URL_DATA_PREFIX: "/api/"
}

var StringUtil = {
    sanitizeUrl: function(url){
        url = url.replace(/([^:])[\/]+/g, '$1/');
        return url
    },
    humanizeName: function(name){
        name = name.replace(/_/g, " ");
        return name
    }
}

function AlbumModel(albumDelegate){

    var delegate = albumDelegate
    var self = this

    this.path = null;
    this.albuns = null;
    this.pictures = null;
    this.visibility = null;

    this.loading = false;

    this.selectedPictureIndex = null;
    this.highlightOn = false;

    this.loadAlbum = function(albumPath){
        albumPath = albumPath.replace(Settings.URL_PREFIX, '')
        console.log("loading: "+albumPath);
        self.loading = true
        delegate.get(albumPath, loadAlbumResultHandler, loadAlbumFailHandler);
    }

    function loadAlbumResultHandler(result){
        for (var prop in result){
            if (self.hasOwnProperty(prop)){
                self[prop] = result[prop];
            }
        }
        console.log(self)
        self.loading = false
    }

    function loadAlbumFailHandler(error){
        self.loading = false
    }

    return this;
}

function AlbumDelegate(){

    this.get = function(albumPath, resultHandler, failHandler){
        var url = Settings.URL_DATA_PREFIX + albumPath;
        url = StringUtil.sanitizeUrl(url);
        console.log("URL: "+url)
        $.get(url, function(result) {
            resultHandler(result)
        }).fail(function(status){
            failHandler(status)
        });
    }
}

function Loading(model, conf){

    var $view = null

    function init(){
        $view = conf.view;
        watch(model, "loading", function(){
            $view.toggle(model.loading);
        });
        $view.hide();
    }

    init();
}

function AlbumNavigator(model, conf){

    var template = null;
    var $view = null;
    var $viewList = null;

    function init(){
        $view = conf.view;
        template = conf.template;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view

        watch(model, "albuns", function(){
            displayAlbuns();
        });
        
    }

    function getAlbumUrl(albumName){
        var url = Settings.URL_PREFIX + model.path + '/' + albumName;
        url = StringUtil.sanitizeUrl(url);
        return url;
    }
    
    function displayAlbuns(){
        if(!model.albuns || model.albuns.length == 0){
            $view.hide();
            return;
        }
        $view.show();
        content = "";
        for (var i=0; i<model.albuns.length; i++){
            var albumName = model.albuns[i]
            content += Mustache.render(template, {
                url: getAlbumUrl(albumName), 
                name: StringUtil.humanizeName(albumName)});
        }
        $viewList.html(content);
        enableAsynchronous();
    }

    function enableAsynchronous(){
        $view.find("a").click(function(){
            var $link = $(this);
//            $viewList.slideUp(function(){
                model.loadAlbum($link.attr("href"))
//            });
            return false;
        })
    }

    init();
}

function AlbumBreadcrumb(model, conf){

    var self = this;

    var $view = null;
    var $viewList = null;
    var templateHome = null;
    var template = null;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view
        templateHome = conf.templateHome
        template = conf.template
        
        watch(model, "path", function(){
            self.updatePath()
        });
    }

    function getAlbumUrl(albumName){
        var url = Settings.URL_PREFIX + model.path + '/' + albumName;
        url = StringUtil.sanitizeUrl(url);
        return url;
    }

    this.updatePath = function(){
        var parts = model.path.split("/");
        if (parts[parts.length - 1]==""){
            parts.pop();
        }
        var partial = '/'
        var content = Mustache.render(templateHome, {
            url: StringUtil.sanitizeUrl(Settings.URL_PREFIX + '/')
        });
        for (var i=1; i<parts.length; i++){
            partial += parts[i] + '/';
            params = {}
            if (i < parts.length - 1){
                params.url = StringUtil.sanitizeUrl(Settings.URL_PREFIX + partial);
            }
            params.name = StringUtil.humanizeName(parts[i])
            content += Mustache.render(template, params);
        }
        $viewList.html(content)
        enableAsynchronous();
    }

    function enableAsynchronous(){
        $viewList.find("a").click(function(){
            model.loadAlbum($(this).attr("href"));
            return false;
        })
    }

    init()
}


function AlbumDeepLinking(model){

    var self = this;

    function init(){
        watch(model, "path", function(){
            updateUrl()
        });

        $(window).bind('popstate', function(event){
            changeAlbumFromUrl()
        })

        changeAlbumFromUrl()
    }

    function extractPathFromUrl(){
        var albumPath = location.pathname
        albumPath = albumPath.replace(Settings.URL_PREFIX, "")
        if (!albumPath){
            albumPath = "/"
        }
        return albumPath;
    }

    function updateUrl(){
        var currentAlbumPath = location.pathname
        var newPath = Settings.URL_PREFIX + model.path
        if (currentAlbumPath == newPath){
            return;
        }
        newPath = StringUtil.sanitizeUrl(newPath)
        history.pushState(null, null, newPath)
    }

    function changeAlbumFromUrl(){
        var albumPath = extractPathFromUrl();
        if (albumPath == model.path){
            return;
        }
        model.loadAlbum(albumPath);
    }

    init();
}

function AlbumPhotos(model, conf){

    var $view = null;
    var $viewList = null;
    var template = null;
    var currentWidth = 0;

    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view
        template = conf.template

        watch(model, "pictures", function(){
            displayPictures();
        });

        $(window).resize(function(){
            resizePictures();
        })
    }

    function displayPictures(){
        $viewList.empty();
        if(!model.pictures || model.pictures.length == 0){
            $view.hide();
            return;
        }
        $view.show();

        var resize = new Resize(model.pictures);
        currentWidth = $view.width()
        console.log("currentWidth: "+currentWidth)
        var newPictures = resize.doResize(currentWidth, $(window).height());

        content = "";
        for (var i=0; i<newPictures.length; i++){
            var p = newPictures[i]
            var params = {
                    width: p.newWidth-4, 
                    height: p.newHeight-4
            }
            if (!conf.lazyLoad){
                params.src = p.thumb 
            }
            content += Mustache.render(template, params);
        }
        $viewList.html(content);
        $viewList.find("img").click(function(){
            model.selectedPictureIndex = $(this).data("index");
        })
        if (conf.lazyLoad){
            lazyLoad();
        }
    }

    function resizePictures(){
        var newWidth = $view.width()
        if (newWidth == currentWidth) return;
        currentWidth = $view.width()
        var resize = new Resize(model.pictures);
        var newPictures = resize.doResize(currentWidth, $(window).height());
        $viewList.children().each(function(index, item){
            var p = newPictures[index]
            var width = (p.newWidth-4);
            var height = (p.newHeight-4);
            $(this).css("width", width).css("height", height)
            $(this).find("img").attr("width", width).attr("height", height)
        })
    }
    
    function lazyLoad(){
        $viewList.find("img").hide();
        var index = 0;
        var image = new Image()
        image.onload = function(){
            $viewList.find("img:eq("+index+")")
                .attr("src", this.src)
                .show()
            index++
            loadNextPicture()
        }
        function loadNextPicture(){
            if (index >= model.pictures.length){
                return
            }
            $viewList.find("img:eq("+index+")").data("index", index)
            image.src = model.pictures[index].thumb
        }
        loadNextPicture()
    }

    init();
}

function Highlight(model, conf){

    var self = this;

    var $view = null;
    var $viewList = null;
    var template = null;

    var currentPictureIndex = null;
    var currentFrame = null;
    var prevFrame = null;
    var nextFrame = null;

    var isOpened = false;
    
    function init(){
        $view = conf.view;
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view;
        template = conf.template

        watch(model, "selectedPictureIndex", function(){
            if (isOpened) return;
            self.displayPicture();
        });

        $view.click(function(){
            self.close()
        })

        $(window).resize(function(){
            self.updateDisplay();
        })

        $('body').keyup(function (event) {
            if (event.keyCode == 37){
                self.displayPrevPicture();
            } else if (event.keyCode == 39){
                self.displayNextPicture();
            } else if (event.keyCode == 27){
                self.close();
            }
        });
    }

    this.hasPicturesToDisplay = function(){
        return (model.selectedPictureIndex!=null
                && model.selectedPictureIndex >= 0
                && model.pictures
                && model.pictures.length>=0);

    }
    
    this.close = function(){
        model.selectedPictureIndex = null;
        isOpened = false;
        $view.fadeOut("slow");
    }

    function createHighlight(){
        var $frame = $(Mustache.render(template, {}));
        return $frame;
    }

    this.displayPicture = function(){
        if (!self.hasPicturesToDisplay()){
            self.close();
            return;
        }
        isOpened = true;
        $viewList.empty()
        createCurrentHighlight();
        createLeftHighlight();
        createRightHighlight();
        self.updateDisplay();
    }

    // Move from left to right
    this.displayPrevPicture = function(){
        if (!self.hasPicturesToDisplay()) return;
        $viewList.find(".large-photo").stop()
        if (model.selectedPictureIndex == 0) return;
        var newRightPicture = model.pictures[model.selectedPictureIndex];
        model.selectedPictureIndex--;

        var newCurrentFrame = prevFrame;
        newCurrentFrame.removeClass("prev-frame").addClass("current-frame")
        var newCurrentPicture = model.pictures[model.selectedPictureIndex]
        var newCurrentDimension = calculateDimension(newCurrentPicture);
        newCurrentFrame.find(".box-blur").hide();
        newCurrentFrame.find(".large-photo").animate({
            left: newCurrentDimension.x
        }, 500, "swing", function(){
            showBlur(newCurrentFrame, newCurrentPicture);
            showHighResolution(newCurrentFrame, newCurrentPicture)
        });

        var newRightFrame = currentFrame
        newRightFrame.removeClass("current-frame").addClass("next-frame")
        var newRightDimension = calculateDimensionRight(newRightPicture);
        newRightFrame.find(".large-photo").animate({
            left: newRightDimension.x
        }, 500, "swing");

        if (nextFrame) nextFrame.remove();
        nextFrame = currentFrame;
        currentFrame = prevFrame;
        prevFrame = null;

        // Set Image to the new Left
        if (model.selectedPictureIndex > 0){
            createLeftHighlight()
            var newLeftPicture = model.pictures[model.selectedPictureIndex - 1];
            var dimension = calculateDimensionLeft(newLeftPicture);
            setPosition(prevFrame, dimension)
            showLowResolution(prevFrame, newLeftPicture)
        }
    }

    // Move from right to left
    this.displayNextPicture = function(){
        if (!self.hasPicturesToDisplay()) return;
        $viewList.find(".large-photo").stop()
        if (model.selectedPictureIndex >= (model.pictures.length - 1)) return;
        var newLeftPicture = model.pictures[model.selectedPictureIndex];
        model.selectedPictureIndex++;

        var newCurrentFrame = nextFrame;
        newCurrentFrame.removeClass("next-frame").addClass("current-frame")
        var newCurrentPicture = model.pictures[model.selectedPictureIndex]
        var newCurrentDimension = calculateDimension(newCurrentPicture);
        newCurrentFrame.find(".box-blur").hide();
        newCurrentFrame.find(".large-photo").animate({
            left: newCurrentDimension.x
        }, 500, "swing", function(){
            showBlur(newCurrentFrame, newCurrentPicture)
            showHighResolution(newCurrentFrame, newCurrentPicture)
        });

        var newLeftFrame = currentFrame;
        newLeftFrame.removeClass("current-frame").addClass("prev-frame")
        var newLeftDimension = calculateDimensionLeft(newLeftPicture);
        newLeftFrame.find(".large-photo").animate({
            left: newLeftDimension.x
        }, 500, "swing");

        if (prevFrame) prevFrame.remove();
        prevFrame = currentFrame;
        currentFrame = nextFrame;
        nextFrame = null;

        // Set Image to the new Right
        if (model.selectedPictureIndex < (model.pictures.length - 1)){
            createRightHighlight()
            var newRightPicture = model.pictures[model.selectedPictureIndex + 1];
            var dimension = calculateDimensionRight(newRightPicture);
            setPosition(nextFrame, dimension)
            showLowResolution(nextFrame, newRightPicture)
        }
    }

    function createCurrentHighlight(){
        currentFrame = createHighlight();
        currentFrame.addClass("current-frame");
        $viewList.append(currentFrame);
    }

    function createLeftHighlight(){
        if (prevFrame) prevFrame.remove();
        prevFrame = createHighlight();
        prevFrame.addClass("prev-frame");
        $viewList.append(prevFrame);
    }

    function createRightHighlight(){
        if (nextFrame) nextFrame.remove();
        nextFrame = createHighlight();
        nextFrame.addClass("next-frame");
        $viewList.append(nextFrame);
    }

    this.updateDisplay = function(){
        if (!self.hasPicturesToDisplay()) return;
        if (!isOpened) return;
        $view.fadeIn("slow");
        if (currentFrame) {
            var picture = model.pictures[model.selectedPictureIndex]
            var dimension = calculateDimension(picture);
            setPosition(currentFrame, dimension)
            showLowResolution(currentFrame, picture)
            showHighResolution(currentFrame, picture)
            showBlur(currentFrame, picture)
        }
        if (prevFrame && model.selectedPictureIndex > 0) {
            var picture = model.pictures[model.selectedPictureIndex - 1]
            var dimension = calculateDimensionLeft(picture);
            setPosition(prevFrame, dimension);
            showLowResolution(prevFrame, picture)
        }
        if (nextFrame && model.selectedPictureIndex < model.pictures.length - 1) {
            var picture = model.pictures[model.selectedPictureIndex + 1]
            var dimension = calculateDimensionRight(picture);
            setPosition(nextFrame, dimension);
            showLowResolution(nextFrame, picture)
        }
    }

    function calculateDimension(picture){
        var $window = $view;
        var newWidth = $window.width();
        var newHeight = Math.round(newWidth / picture.ratio)
        var x = 0
        var y = Math.round(($window.height() - newHeight) / 2)
        if (y < 0){
            newHeight = $window.height()
            newWidth = Math.round(newHeight * picture.ratio)
            y = 0;
            x = Math.round(($window.width() - newWidth) / 2)
        }
        return {newWidth: newWidth, newHeight: newHeight, x:x, y:y, fullWidth: $window.width(), fullHeight: $window.height()}
    }

    function calculateDimensionLeft(picture){
        var dimension = calculateDimension(picture);
        dimension.x = -1 * dimension.newWidth - 50;
        return dimension
    }

    function calculateDimensionRight(picture){
        var dimension = calculateDimension(picture);
        dimension.x = $view.width() + 50;
        return dimension
    }

    function showHighResolution(frame, picture){
        var $highRes = frame.find(".high-res");
        $highRes.hide()

        image = new Image()
        image.onload = function(){
            $highRes.attr("src", this.src);
            $highRes.fadeIn();
        }
        image.src = picture.highlight;
    }

    function showLowResolution(frame, picture){
        var $lowRes = frame.find(".low-res");
        $lowRes.attr("src", picture.thumb)
    }

    function setPosition(frame, dimension){
        var largePhoto = frame.find(".large-photo")
        largePhoto.css("left", dimension.x+"px").css("top", dimension.y+"px");
        largePhoto.css("width", dimension.newWidth+"px").css("height", dimension.newHeight+"px");
    }

    function showBlur(frame, picture){
        setTimeout(function(){
            blur = frame.find('.box-blur').hide()
            blur.fadeIn(2000)
            boxBlurImage(frame.find('.low-res').get(0), blur.get(0), 20, false, 2);
        }, 500);
    }

    init();
}
