function Highlight(selector){

    var ANIMATION_DURATION = 2 * 100;
    
    var self = this
    var $this = selector
    var opened = false

    var pictures = null;
    var currentPictureIndex = null;

    var currentFrame = null;
    var prevFrame = null;
    var nextFrame = null;

    function init(){
        addEventListeners()
    }

    function addEventListeners(){
        $this.click(function(){
            self.closePicture()
        })
        $(window).resize(function(){
            self.updateDisplay();
        })
        $('body').keyup(function (event) {
            if (event.keyCode == 37){
                self.displayPrevPicture()
            } else if (event.keyCode == 39){
                self.displayNextPicture()
            } else if (event.keyCode == 27){
                self.closePicture();
            }
        });
    }

    this.setPictures = function(ps){
        pictures = ps
    }

    this.displayPicture = function(index){
        currentPictureIndex = index;
        opened = true
        createCurrentHighlight();
        createLeftHighlight();
        createRightHighlight();
        createDetails();
        self.updateDisplay();
    }

    // Move from left to right
    this.displayPrevPicture = function(){
        if (!pictures || currentPictureIndex <= 0) return;
        $this.find(".large-photo").stop()
        var newRightPicture = pictures[currentPictureIndex];
        currentPictureIndex--;

        var newCurrentFrame = prevFrame;
        newCurrentFrame.removeClass("prev-frame").addClass("current-frame")
        var newCurrentPicture = pictures[currentPictureIndex]
        var newCurrentDimension = calculateDimension(newCurrentPicture);
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
        newRightFrame.find(".blur").removeClass("visible");

        if (nextFrame) nextFrame.remove();
        nextFrame = currentFrame;
        currentFrame = prevFrame;
        prevFrame = null;

        // Set Image to the new Left
        if (currentPictureIndex > 0){
            createLeftHighlight()
            var newLeftPicture = pictures[currentPictureIndex - 1];
            var dimension = calculateDimensionLeft(newLeftPicture);
            setPosition(prevFrame, dimension)
            showLowResolution(prevFrame, newLeftPicture)
        }
    }

    // Move from right to left
    this.displayNextPicture = function(){
        $this.find(".large-photo").stop()
        if (!pictures || currentPictureIndex >= (pictures.length - 1)) return;
        var newLeftPicture = pictures[currentPictureIndex];
        currentPictureIndex++;

        var newCurrentFrame = nextFrame;
        newCurrentFrame.removeClass("next-frame").addClass("current-frame")
        var newCurrentPicture = pictures[currentPictureIndex]
        var newCurrentDimension = calculateDimension(newCurrentPicture);
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
        newLeftFrame.find(".blur").removeClass("visible");

        if (prevFrame) prevFrame.remove();
        prevFrame = currentFrame;
        currentFrame = nextFrame;
        nextFrame = null;

        // Set Image to the new Right
        if (currentPictureIndex < (pictures.length - 1)){
            createRightHighlight()
            var newRightPicture = pictures[currentPictureIndex + 1];
            var dimension = calculateDimensionRight(newRightPicture);
            setPosition(nextFrame, dimension)
            showLowResolution(nextFrame, newRightPicture)
        }
    }

    function createHighlight(){
        if (window.location.hash=="#canvas"){
            var $frame = $("<div class=\"photo-frame\"><canvas class=\"box-blur\"/><div class=\"large-photo\"><img class=\"low-res\" /><img class=\"high-res\"/></div></div>");
        } else {
            var $frame = $("<div class=\"photo-frame\"><img class=\"blur\" /><div class=\"large-photo\"><img class=\"low-res\" /><img class=\"high-res\"/></div></div>");
        }
        return $frame;
    }

    function createDetails(){
        $this.append("<div class=\"photo-details\"><div class='name item-detail'></div><div class='album item-detail'></div><div class='date item-detail'></div></div>")
    }
    
    function createCurrentHighlight(){
        currentFrame = createHighlight();
        currentFrame.addClass("current-frame")
        $this.append(currentFrame)
    }

    function createLeftHighlight(){
        if (prevFrame) prevFrame.remove()
        prevFrame = createHighlight();
        prevFrame.addClass("prev-frame")
        $this.append(prevFrame)
    }

    function createRightHighlight(){
        if (nextFrame) nextFrame.remove()
        nextFrame = createHighlight();
        nextFrame.addClass("next-frame")
        $this.append(nextFrame)
    }

    function calculateDimension(picture){
        var $window = $this
        var newWidth = $window.width()
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
        dimension.x = $this.width() + 50;
        return dimension
    }

    function showHighResolution(frame, picture){
        var $highRes = frame.find(".high-res")
        $highRes.hide()

        image = new Image()
        image.onload = function(){
            $highRes.attr("src", this.src)
            $highRes.fadeIn();
        }
        image.src = picture.highlight
    }

    function showLowResolution(frame, picture){
        var $lowRes = frame.find(".low-res");
        $lowRes.attr("src", picture.thumb)
        showInfoDetails()
    }

    function setPosition(frame, dimension){
        var largePhoto = frame.find(".large-photo")
        largePhoto.css("left", dimension.x+"px").css("top", dimension.y+"px");
        largePhoto.css("width", dimension.newWidth+"px").css("height", dimension.newHeight+"px");
    }

    function showBlur(frame, picture){
        if (window.location.hash=="#canvas"){
            setTimeout(function(){
                blur = frame.find('.box-blur').hide()
                blur.fadeIn(2000)
                boxBlurImage(frame.find('.low-res').get(0), blur.get(0), 20, false, 2);
            }, 500)
        } else {
           var $blur = frame.find(".blur");
            $blur.attr("src", picture.thumb);
            setTimeout(function(){
                $blur.addClass("visible");
            }, 500)
        }
    }

    function showInfoDetails(){
        var $details = $this.find(".photo-details");
        var picture = pictures[currentPictureIndex]
        $details.find(".name").html(picture.name);
        $details.find(".album").html( $("#photos").attr("data-album-name") );
        $details.find(".date").html( picture.date.split(" ")[0].split("-").reverse().join("/") );
    }

    this.updateDisplay = function(){
        $this.fadeIn("slow");
        if (!opened || !pictures || pictures.length==0) return;
        if (currentFrame) {
            var picture = pictures[currentPictureIndex]
            var dimension = calculateDimension(picture);
            setPosition(currentFrame, dimension)
            showLowResolution(currentFrame, picture)
            showHighResolution(currentFrame, picture)
            showBlur(currentFrame, picture)
        }
        if (prevFrame && currentPictureIndex > 0) {
            var picture = pictures[currentPictureIndex - 1]
            var dimension = calculateDimensionLeft(picture);
            setPosition(prevFrame, dimension);
            showLowResolution(prevFrame, picture)
        }
        if (nextFrame && currentPictureIndex < pictures.length - 1) {
            var picture = pictures[currentPictureIndex + 1]
            var dimension = calculateDimensionRight(picture);
            setPosition(nextFrame, dimension);
            showLowResolution(nextFrame, picture)
        }
    }

    this.closePicture = function(){
        $this.fadeOut("slow", function(){
            $this.empty();
        });
        currentFrame = null;
        prevFrame = null;
        nextFrame = null;
        opened = false
    }

    this.isOpened = function(){
        return opened;
    }

    init()
}
