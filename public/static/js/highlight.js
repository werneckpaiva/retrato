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
