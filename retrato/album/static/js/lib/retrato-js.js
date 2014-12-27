var Settings = {
    URL_PREFIX: "/",
    URL_DATA_PREFIX: "/api/"
};

var StringUtil = {
    sanitizeUrl: function(url){
        url = url.replace(/([^:])[\/]+/g, '$1/');
        return url;
    },
    humanizeName: function(name){
        name = name.replace(/_/g, " ");
        name = name.replace(/\.jpe?g/i, "");
        return name;
    }
};


var Fullscreen = {
    open: function(element){
        if (element.requestFullscreen) {
            element.requestFullscreen();
        } else if (element.webkitRequestFullscreen) {
            element.webkitRequestFullscreen();
        } else if (element.mozRequestFullScreen) {
            element.mozRequestFullScreen();
        } else if (element.msRequestFullscreen) {
            element.msRequestFullscreen();
        }
    },

    close: function close() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
    },

    onchange: function(handler){
        document.addEventListener("fullscreenchange", handler);
        document.addEventListener("webkitfullscreenchange", handler);
        document.addEventListener("mozfullscreenchange", handler);
        document.addEventListener("MSFullscreenChange", handler);
    },

    isActive: function(){
        return document.fullscreenElement || 
        document.mozFullScreenElement || 
        document.webkitFullscreenElement || 
        document.msFullscreenElement;
    }
};

function AlbumPhotos(model, conf){

    var self = this;
    var $view = null;
    var $viewList = null;
    var template = null;
    var currentWidth = 0;
    var heightProportion = null;
    var lazyLoad = false;

    var margin = 0;

    function init(){
        setConfiguration();

        watch(model, "pictures", function(prop, action, newvalue, oldvalue){
            var picturesChanged = Array.isArray(newvalue);
            self.displayPictures(picturesChanged);
        });

        $(window).resize(function(){
            self.resizePictures();
        });
    }

    function setConfiguration(){
        // Required
        $view = conf.view;
        template = conf.template;

        // Optional
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : $view;
        heightProportion = (conf.heightProportion)? conf.heightProportion : 0.45;
        lazyLoad = (conf.lazyLoad)? conf.lazyLoad : false;
        margin = (conf.margin)?  conf.margin : 0;
    }
    
    this.displayPictures = function(picturesChanged){
        if (picturesChanged===false){
            return;
        }

        $viewList.empty();
        if(!model.pictures || model.pictures.length === 0){
            $view.hide();
            return;
        }
        $view.show();

        var resize = new Resize(model.pictures, heightProportion);
        currentWidth = $view.width();
        var newPictures = resize.doResize(currentWidth, $(window).height());

        var content = "";
        for (var i=0; i<newPictures.length; i++){
            var p = newPictures[i];
            var params = {
                    width: p.newWidth-margin,
                    height: p.newHeight-margin
            };
            if (!lazyLoad){
                params.src = model.pictures[i].thumb;
            }
            content += Mustache.render(template, params);
        }
        $viewList.html(content);
        $viewList.find("img")
            .each(function(i, el){
                $(el).data("index", i);
            })
            .click(function(){
                model.selectedPictureIndex = $(this).data("index");
            });
        if (lazyLoad){
            startLazyLoading();
        }
    };

    this.resizePictures = function(){
        var newWidth = $view.width();
        if (newWidth == currentWidth) return;
        currentWidth = $view.width();
        var resize = new Resize(model.pictures, heightProportion);
        var newPictures = resize.doResize(currentWidth, $(window).height());
        $viewList.children().each(function(index, item){
            var p = newPictures[index];
            var width = (p.newWidth-margin);
            var height = (p.newHeight-margin);
            $(this).css("width", width).css("height", height);
            $(this).find("img").attr("width", width).attr("height", height);
        });
    };

    function startLazyLoading(){

        function loadNextPicture(){
            if (index >= model.pictures.length){
                return;
            }
            if (image.src == model.pictures[index].thumb){
                index++;
                loadNextPicture();
            } else {
                image.src = model.pictures[index].thumb;
            }
        }

        var index = 0;
        var image = new Image();
        image.onload = function(){
            $viewList.find("img:eq("+index+")")
                .attr("src", this.src)
                .show();
            index++;
            loadNextPicture();
        };

        loadNextPicture();
    }

    init();
};/*

Superfast Blur - a fast Box Blur For Canvas

Version:     0.5
Author:        Mario Klingemann
Contact:     mario@quasimondo.com
Website:    http://www.quasimondo.com/BoxBlurForCanvas
Twitter:    @quasimondo

In case you find this class useful - especially in commercial projects -
I am not totally unhappy for a small donation to my PayPal account
mario@quasimondo.de

Or support me on flattr:
https://flattr.com/thing/140066/Superfast-Blur-a-pretty-fast-Box-Blur-Effect-for-CanvasJavascript

Copyright (c) 2011 Mario Klingemann

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
*/
var mul_table = [ 1,57,41,21,203,34,97,73,227,91,149,62,105,45,39,137,241,107,3,173,39,71,65,238,219,101,187,87,81,151,141,133,249,117,221,209,197,187,177,169,5,153,73,139,133,127,243,233,223,107,103,99,191,23,177,171,165,159,77,149,9,139,135,131,253,245,119,231,224,109,211,103,25,195,189,23,45,175,171,83,81,79,155,151,147,9,141,137,67,131,129,251,123,30,235,115,113,221,217,53,13,51,50,49,193,189,185,91,179,175,43,169,83,163,5,79,155,19,75,147,145,143,35,69,17,67,33,65,255,251,247,243,239,59,29,229,113,111,219,27,213,105,207,51,201,199,49,193,191,47,93,183,181,179,11,87,43,85,167,165,163,161,159,157,155,77,19,75,37,73,145,143,141,35,138,137,135,67,33,131,129,255,63,250,247,61,121,239,237,117,29,229,227,225,111,55,109,216,213,211,209,207,205,203,201,199,197,195,193,48,190,47,93,185,183,181,179,178,176,175,173,171,85,21,167,165,41,163,161,5,79,157,78,154,153,19,75,149,74,147,73,144,143,71,141,140,139,137,17,135,134,133,66,131,65,129,1];

var shg_table = [0,9,10,10,14,12,14,14,16,15,16,15,16,15,15,17,18,17,12,18,16,17,17,19,19,18,19,18,18,19,19,19,20,19,20,20,20,20,20,20,15,20,19,20,20,20,21,21,21,20,20,20,21,18,21,21,21,21,20,21,17,21,21,21,22,22,21,22,22,21,22,21,19,22,22,19,20,22,22,21,21,21,22,22,22,18,22,22,21,22,22,23,22,20,23,22,22,23,23,21,19,21,21,21,23,23,23,22,23,23,21,23,22,23,18,22,23,20,22,23,23,23,21,22,20,22,21,22,24,24,24,24,24,22,21,24,23,23,24,21,24,23,24,22,24,24,22,24,24,22,23,24,24,24,20,23,22,23,24,24,24,24,24,24,24,23,21,23,22,23,24,24,24,22,24,24,24,23,22,24,24,25,23,25,25,23,24,25,25,24,22,25,25,25,24,23,24,25,25,25,25,25,25,25,25,25,25,25,25,23,25,23,24,25,25,25,25,25,25,25,25,25,24,22,25,25,23,25,25,20,24,25,24,25,25,22,24,25,24,25,24,25,25,24,25,25,25,25,22,25,25,25,24,25,24,25,18];

function boxBlurImage( img, canvas, radius, blurAlphaChannel, iterations){

    var w = canvas.width;
    var h = canvas.height;

    var context = canvas.getContext("2d");
    context.clearRect( 0, 0, canvas.width, canvas.height);
    context.drawImage( img, 0, 0, canvas.width, canvas.height);

    if ( isNaN(radius) || radius < 1 ) return;

    if ( blurAlphaChannel ) {
        boxBlurCanvasRGBA( canvas, 0, 0, w, h, radius, iterations );
    } else {
        boxBlurCanvasRGB( canvas, 0, 0, w, h, radius, iterations );
    }
    var widthCenter = Math.round(canvas.width / 2);
    var heightCenter = Math.round(canvas.height / 2);
    var grd=context.createRadialGradient(widthCenter, 
            heightCenter,
            0, 
            widthCenter, 
            heightCenter,
            widthCenter + 0);
    grd.addColorStop(0,"rgba(0,0,0,0)");
    grd.addColorStop(1,"rgba(0,0,0,0.6)");
    // Fill with gradient
    context.fillStyle=grd;
    context.fillRect(0, 0, canvas.width, canvas.height);
    
}


function boxBlurCanvasRGBA( canvas, top_x, top_y, width, height, radius, iterations ){
    if ( isNaN(radius) || radius < 1 ) return;
    
    radius |= 0;
    
    if ( isNaN(iterations) ) iterations = 1;
    iterations |= 0;
    if ( iterations > 3 ) iterations = 3;
    if ( iterations < 1 ) iterations = 1;
    
    var context = canvas.getContext("2d");
    var imageData;
    
    try {
      try {
        imageData = context.getImageData( top_x, top_y, width, height );
      } catch(e) {
      
        // NOTE: this part is supposedly only needed if you want to work with local files
        // so it might be okay to remove the whole try/catch block and just use
        // imageData = context.getImageData( top_x, top_y, width, height );
        try {
            netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");
            imageData = context.getImageData( top_x, top_y, width, height );
        } catch(error) {
            throw new Error("unable to access local image data: " + error);
        }
      }
    } catch(e) {
      throw new Error("unable to access image data: " + e);
    }
            
    var pixels = imageData.data;
        
    var rsum,gsum,bsum,asum,x,y,i,p,p1,p2,yp,yi,yw,idx,pa;        
    var wm = width - 1;
      var hm = height - 1;
    var wh = width * height;
    var rad1 = radius + 1;
    
    var mul_sum = mul_table[radius];
    var shg_sum = shg_table[radius];

    var r = [];
    var g = [];
    var b = [];
    var a = [];
    
    var vmin = [];
    var vmax = [];
  
    while ( iterations-- > 0 ){
        yw = yi = 0;
     
        for ( y=0; y < height; y++ ){
            rsum = pixels[yw]   * rad1;
            gsum = pixels[yw+1] * rad1;
            bsum = pixels[yw+2] * rad1;
            asum = pixels[yw+3] * rad1;
            
            
            for( i = 1; i <= radius; i++ ){
                p = yw + (((i > wm ? wm : i )) << 2 );
                rsum += pixels[p++];
                gsum += pixels[p++];
                bsum += pixels[p++];
                asum += pixels[p];
            }
            
            for ( x = 0; x < width; x++ ) {
                r[yi] = rsum;
                g[yi] = gsum;
                b[yi] = bsum;
                a[yi] = asum;

                if(y===0) {
                    vmin[x] = ( ( p = x + rad1) < wm ? p : wm ) << 2;
                    vmax[x] = ( ( p = x - radius) > 0 ? p << 2 : 0 );
                } 
                
                p1 = yw + vmin[x];
                p2 = yw + vmax[x];
                  
                rsum += pixels[p1++] - pixels[p2++];
                gsum += pixels[p1++] - pixels[p2++];
                bsum += pixels[p1++] - pixels[p2++];
                asum += pixels[p1]   - pixels[p2];
                     
                yi++;
            }
            yw += ( width << 2 );
        }
      
        for ( x = 0; x < width; x++ ) {
            yp = x;
            rsum = r[yp] * rad1;
            gsum = g[yp] * rad1;
            bsum = b[yp] * rad1;
            asum = a[yp] * rad1;
            
            for( i = 1; i <= radius; i++ ) {
              yp += ( i > hm ? 0 : width );
              rsum += r[yp];
              gsum += g[yp];
              bsum += b[yp];
              asum += a[yp];
            }
            
            yi = x << 2;
            for ( y = 0; y < height; y++) {
                
                pixels[yi+3] = pa = (asum * mul_sum) >>> shg_sum;
                if ( pa > 0 )
                {
                    pa = 255 / pa;
                    pixels[yi]   = ((rsum * mul_sum) >>> shg_sum) * pa;
                    pixels[yi+1] = ((gsum * mul_sum) >>> shg_sum) * pa;
                    pixels[yi+2] = ((bsum * mul_sum) >>> shg_sum) * pa;
                } else {
                    pixels[yi] = pixels[yi+1] = pixels[yi+2] = 0;
                }                
                if( x === 0 ) {
                    vmin[y] = ( ( p = y + rad1) < hm ? p : hm ) * width;
                    vmax[y] = ( ( p = y - radius) > 0 ? p * width : 0 );
                } 
              
                p1 = x + vmin[y];
                p2 = x + vmax[y];

                rsum += r[p1] - r[p2];
                gsum += g[p1] - g[p2];
                bsum += b[p1] - b[p2];
                asum += a[p1] - a[p2];

                yi += width << 2;
            }
        }
    }
    
    context.putImageData( imageData, top_x, top_y );
    
}

function boxBlurCanvasRGB( canvas, top_x, top_y, width, height, radius, iterations ){
    if ( isNaN(radius) || radius < 1 ) return;
    
    radius |= 0;
    
    if ( isNaN(iterations) ) iterations = 1;
    iterations |= 0;
    if ( iterations > 3 ) iterations = 3;
    if ( iterations < 1 ) iterations = 1;
    
    var context = canvas.getContext("2d");
    var imageData;
    
    try {
      try {
        imageData = context.getImageData( top_x, top_y, width, height );
      } catch(e) {
      
        // NOTE: this part is supposedly only needed if you want to work with local files
        // so it might be okay to remove the whole try/catch block and just use
        // imageData = context.getImageData( top_x, top_y, width, height );
        try {
            netscape.security.PrivilegeManager.enablePrivilege("UniversalBrowserRead");
            imageData = context.getImageData( top_x, top_y, width, height );
        } catch(error) {
            throw new Error("unable to access local image data: " + error);
        }
      }
    } catch(error) {
      throw new Error("unable to access image data: " + error);
    }
            
    var pixels = imageData.data;
        
    var rsum,gsum,bsum,asum,x,y,i,p,p1,p2,yp,yi,yw,idx;
    var wm = width - 1;
      var hm = height - 1;
    var wh = width * height;
    var rad1 = radius + 1;
   
    var r = [];
    var g = [];
    var b = [];
    
    var mul_sum = mul_table[radius];
    var shg_sum = shg_table[radius];
    
    var vmin = [];
    var vmax = [];
  
    while ( iterations-- > 0 ){
        yw = yi = 0;
     
        for ( y=0; y < height; y++ ){
            rsum = pixels[yw]   * rad1;
            gsum = pixels[yw+1] * rad1;
            bsum = pixels[yw+2] * rad1;
            
            for( i = 1; i <= radius; i++ ){
                p = yw + (((i > wm ? wm : i )) << 2 );
                rsum += pixels[p++];
                gsum += pixels[p++];
                bsum += pixels[p++];
            }
            
            for ( x = 0; x < width; x++ ){
                r[yi] = rsum;
                g[yi] = gsum;
                b[yi] = bsum;
                
                if(y===0) {
                    vmin[x] = ( ( p = x + rad1) < wm ? p : wm ) << 2;
                    vmax[x] = ( ( p = x - radius) > 0 ? p << 2 : 0 );
                } 
                
                p1 = yw + vmin[x];
                p2 = yw + vmax[x];
                  
                rsum += pixels[p1++] - pixels[p2++];
                gsum += pixels[p1++] - pixels[p2++];
                bsum += pixels[p1++] - pixels[p2++];
                 
                yi++;
            }
            yw += ( width << 2 );
        }
      
        for ( x = 0; x < width; x++ ){
            yp = x;
            rsum = r[yp] * rad1;
            gsum = g[yp] * rad1;
            bsum = b[yp] * rad1;
                
            for( i = 1; i <= radius; i++ ){
              yp += ( i > hm ? 0 : width );
              rsum += r[yp];
              gsum += g[yp];
              bsum += b[yp];
            }
            
            yi = x << 2;
            for ( y = 0; y < height; y++){
                pixels[yi]   = (rsum * mul_sum) >>> shg_sum;
                pixels[yi+1] = (gsum * mul_sum) >>> shg_sum;
                pixels[yi+2] = (bsum * mul_sum) >>> shg_sum;
           
                if( x === 0 ) {
                    vmin[y] = ( ( p = y + rad1) < hm ? p : hm ) * width;
                    vmax[y] = ( ( p = y - radius) > 0 ? p * width : 0 );
                } 
                  
                p1 = x + vmin[y];
                p2 = x + vmax[y];

                rsum += r[p1] - r[p2];
                gsum += g[p1] - g[p2];
                bsum += b[p1] - b[p2];
                  
                yi += width << 2;
            }
        }
    }
    context.putImageData( imageData, top_x, top_y );
};function Highlight(model, conf){
    var self = this;

    var $view = null;
    var $viewList = null;
    var template = null;
    var $detailsView = null;

    var currentPictureIndex = null;
    var currentFrame = null;

    var isOpened = false;

    var padding = 10;
    var headerHeight = 0;

    var blurContainer = null;

    function init(){
        setConfiguration();

        createBlurContainer();

        watch(model, "selectedPictureIndex", function(){
            onPictureSelected();
            updateDetailValues();
        });
        watch(model, "detailsOn", function(){
            if (model.detailsOn){
                showDetails();
            } else {
                hideDetails();
            }
        });

        $view.click(function(){
            self.close();
        });

        $(window).resize(function(){
            self.updateDisplay();
        });

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

    function setConfiguration(){
        // Required
        $view = conf.view;
        template = conf.template;

        // Optional
        $viewList = (conf.listClass)? $view.find("."+conf.listClass) : createFramesContainer();
        $detailsView = (conf.detailsView)? conf.detailsView : [];
        headerHeight = (conf.headerHeight)? parseInt(conf.headerHeight) : 0;
    }

    function createFramesContainer(){
        var $container = $("<div class='frame-container'></div>");
        $view.append($container);
        return $container;
    }
    
    function createBlurContainer(){
        blurContainer = $('<div class="blur-container"></div>');
        $view.append(blurContainer);
        return blurContainer;
    }
    
    function onPictureSelected(){
        if (isOpened) {
            if (model.selectedPictureIndex === null){
                self.close();
            }
            return;
        }
        self.handleScroll();
        self.displayPicture();
        blurContainer.empty();
    }
    
    function disableScroll(e){
        if (e.target.id == 'el') return;
        e.preventDefault();
        e.stopPropagation();
    }
    
    this.handleScroll = function(){
        $('body').on('mousewheel', disableScroll);
    };

    this.unhandleScroll = function(){
        $('body').off('mousewheel', disableScroll);
    };

    this.hasPicturesToDisplay = function(){
        return (model.selectedPictureIndex !== null && 
                model.selectedPictureIndex >= 0 && 
                model.pictures && 
                model.pictures.length>=0);
    };

    this.close = function(){
        isOpened = false;
        self.unhandleScroll();
        $view.fadeOut("slow");
        model.selectedPictureIndex = null;
        Fullscreen.close();
    };

    function createHighlight(){
        var $frame = $(Mustache.render(template, {}));
        return $frame;
    }

    function createCanvas(){
        var $canvas = $('<canvas class="blur"/>');
        blurContainer.append($canvas);
        return $canvas;
    }

    this.displayPicture = function(){
        if (!self.hasPicturesToDisplay()){
            self.close();
            return;
        }
        isOpened = true;
        $viewList.empty();
        createCurrentHighlight();
        self.updateDisplay();
    };

    // Move from right to left
    this.displayNextPicture = function(){
        if (!self.hasPicturesToDisplay()) return;
        $viewList.find(".large-photo").stop();
        if (model.selectedPictureIndex >= (model.pictures.length - 1)) return;

        model.selectedPictureIndex++;

        self.showCurrentSelectedPicture();

    };

    // Move from left to right
    this.displayPrevPicture = function(){
        if (!self.hasPicturesToDisplay()) return;
        $viewList.find(".large-photo").stop();
        if (model.selectedPictureIndex === 0) return;

        model.selectedPictureIndex--;

        self.showCurrentSelectedPicture();
    };

    this.showCurrentSelectedPicture = function(){
        var previousFrame = currentFrame;
        if (previousFrame !== null){
            previousFrame.remove();
        }
        createCurrentHighlight();
        self.updateDisplay();
    };

    function createCurrentHighlight(){
        currentFrame = createHighlight();
        currentFrame.addClass("current-frame");
        $viewList.append(currentFrame);
    }

    this.updateDisplay = function(){
        if (!self.hasPicturesToDisplay()) return;
        if (!isOpened) return;
        $view.show();
        if (currentFrame) {
            var picture = model.pictures[model.selectedPictureIndex];
            var dimension = calculateDimension(picture);
            currentFrame.find(".large-photo").addClass("visible");
            setPosition(currentFrame, dimension);
            showLowResolution(currentFrame, picture);
            showHighResolution(currentFrame, picture);
            showBlur(currentFrame, picture);
        }
    };

    function calculateDimension(picture){
        var $window = $view;
        var windowWidth = $window.width();
        var windowHeight = $window.height();

        if (model.detailsOn){
            windowWidth -= $detailsView.width();
        }

        var newWidth = windowWidth - (padding * 2);
        var newHeight = Math.round(newWidth / picture.ratio);
        var x = 0;
        var y = Math.round((windowHeight - newHeight) / 2);
        if (y < headerHeight){
            newHeight = windowHeight - (headerHeight + (padding * 2));
            newWidth = Math.round(newHeight * picture.ratio);
            y = 0;
            x = Math.round(($window.width() - newWidth) / 2);
        }
        x = (windowWidth - newWidth) / 2;
        y = ((windowHeight - headerHeight - newHeight) / 2) + headerHeight;
        return {newWidth: newWidth, newHeight: newHeight, x:x, y:y};
    }

    function calculateDimensionLeft(picture){
        var dimension = calculateDimension(picture);
        dimension.x = -1 * dimension.newWidth - 50;
        return dimension;
    }

    function calculateDimensionRight(picture){
        var dimension = calculateDimension(picture);
        dimension.x = $view.width() + 50;
        return dimension;
    }

    function showHighResolution(frame, picture){
        var $highRes = frame.find(".high-res");
        $highRes.hide();

        image = new Image();
        image.onload = function(){
            $highRes.attr("src", this.src);
            $highRes.fadeIn();
        };
        image.src = picture.highlight;
    }

    function showLowResolution(frame, picture){
        var $lowRes = frame.find(".low-res");
        $lowRes.attr("src", picture.thumb);
    }

    function setPosition(frame, dimension){
        var largePhoto = frame.find(".large-photo");
        largePhoto.css("left", dimension.x+"px").css("top", dimension.y+"px");
        largePhoto.css("width", dimension.newWidth+"px").css("height", dimension.newHeight+"px");
    }

    function animateToPosition(frame, dimension){
        currentFrame.find(".large-photo").animate({
            left:dimension.x,
            top: dimension.y,
            width: dimension.newWidth,
            height: dimension.newHeight
        }, 500);
    }

    function showBlur(frame, picture){
        clearTimeout(self.blurTimeout);
        self.blurTimeout = setTimeout(function(){
            blurContainer.children().fadeOut(2000, function(){
                $(this).remove();
            });
            var $blur = createCanvas();
            boxBlurImage(frame.find('.low-res').get(0), $blur.get(0), 20, false, 2);
            $blur.fadeIn(2000);
        }, 500);
    }

    function showDetails(){
        $detailsView.animate({right: 0}, 500);
        var p = model.pictures[model.selectedPictureIndex];
        var dimension = calculateDimension(p);
        animateToPosition(currentFrame, dimension);
    }

    function hideDetails(){
        $detailsView.animate({right: -$detailsView.width()}, 500);
        if (currentFrame){
            var p = model.pictures[model.selectedPictureIndex];
            var dimension = calculateDimension(p);
            animateToPosition(currentFrame, dimension);
        }
    }

    function updateDetailValues(){
        var picture = model.pictures[model.selectedPictureIndex];
        if (!picture) return;
        $detailsView.find(".file-name").html(picture.filename);
        $detailsView.find(".file-date").html(picture.date);
        $detailsView.find(".file-width").html(picture.width);
        $detailsView.find(".file-height").html(picture.height);
    }

    init();
}
;function AlbumModel(albumDelegate){

    var delegate = albumDelegate;
    var self = this;

    this.path = null;
    this.albuns = null;
    this.pictures = null;
    this.visibility = null;
    this.token = null;

    this.loading = false;

    this.selectedPictureIndex = null;
    this.highlightOn = false;
    this.detailsOn = false;

    this.loadAlbum = function(albumPath, resultHandler, errorHandler){
        self.loading = true;
        delegate.get(albumPath, 
                function(result){
                    loadAlbumResultHandler(result);
                    if (resultHandler !== undefined) resultHandler(result);
                }, 
                function(error){
                    loadAlbumFailHandler(error);
                    if (errorHandler !== undefined) errorHandler(error);
                });
    };

    function loadAlbumResultHandler(result){
        for (var prop in result){
            if (self.hasOwnProperty(prop)){
                self[prop] = result[prop];
            }
        }
        self.loading = false;
        self.selectedPictureIndex = null;
    }

    function loadAlbumFailHandler(error){
        self.loading = false;
        alert("Album does not exist");
    }

    return this;
}

function AlbumAjaxDelegate(){

    this.get = function(albumPath, resultHandler, failHandler){
        var url = albumPath.replace(Settings.URL_PREFIX, '');
        url = Settings.URL_DATA_PREFIX + url;
        url = StringUtil.sanitizeUrl(url);
        $.get(url, function(result) {
            resultHandler(result);
        }).fail(function(status){
            failHandler(status);
        });
    };
}

function AlbumHtmlDelegate(imgs){
    this.get = function(albumPath, resultHandler, failHandler){
        var result = {
                path: albumPath,
                pictures: []
        };
        imgs.each(function(i, element){
            $el = $(element);
            var ratio = parseFloat($el.attr("width")) / parseFloat($el.attr("height"));
            ratio = Math.round(ratio * 1000) / 1000;
            var picture = {
                    width: $el.attr("width"),
                    height: $el.attr("height"),
                    thumb: $el.attr("src"),
                    url: $el.data("photo"),
                    highlight: $el.data("photo"),
                    ratio: ratio
            };
            result.pictures.push(picture);
        });
        resultHandler(result);
    };
};function Resize(pictures, heightProportion){
    this.pictures = pictures;
    this.HEIGHT_PROPORTION = 0.45;
    if (heightProportion){
        this.HEIGHT_PROPORTION = heightProportion;
    }
}

Resize.prototype.doResize = function(viewWidth, viewHeight){
    viewWidth = Math.floor(viewWidth);
//    viewWidth--;
    var idealHeight = parseInt(viewHeight * this.HEIGHT_PROPORTION);

    var sumWidths = this.sumWidth(idealHeight);
    var rows = Math.ceil(sumWidths / viewWidth);

//    if (rows <= 1){
//        // fallback to standard size
//        console.log("1 row")
//        this.resizeToSameHeight(idealHeight)
//    } else {
      return this.resizeUsingLinearPartitions(rows, viewWidth);
//    }
};

Resize.prototype.sumWidth = function(height){
    var sumWidths = 0;
    var p;
    for (var i in this.pictures){
        p = this.pictures[i];
        sumWidths += p.ratio * height;
    }
    return sumWidths;
};

Resize.prototype.resizeToSameHeight = function(height){
    var p;
    for (var i in this.pictures){
        p = this.pictures[i];
        p.newWidth = parseInt(height * p.ratio);
        p.newHeight = height;
    }
    return this.pictures;
};

Resize.prototype.resizeUsingLinearPartitions = function(rows, viewWidth){
    var weights = [];
    var p, i, j;
    for (i in this.pictures){
        p = this.pictures[i];
        weights.push(parseInt(p.ratio * 100));
    }
    var partitions = linearPartition(weights, rows);
    var index = 0;
    var newDimensions = [];
    for(i in partitions){
        partition = partitions[i];
        var rowList = [];
        for(j in partition){
            rowList.push(this.pictures[index]);
            index++;
        }
        var summedRatios = 0;
        for (j in rowList){
            p = rowList[j];
            summedRatios += p.ratio;
        }
        var rowHeight = (viewWidth / summedRatios);
        var rowWidth = 0;
        for (j in rowList){
            p = rowList[j];
            var dimension = {};
            dimension.newWidth = parseInt(rowHeight * p.ratio);
            rowWidth += dimension.newWidth;
            dimension.newHeight = parseInt(rowHeight);
            newDimensions.push(dimension);
        }
    }
    return newDimensions;
};

function linearPartition(seq, k){
    if (k <= 0){
        return [];
    }

    var n = seq.length - 1;
    var partitions = [];
    if (k > n){
        for (var i in seq){
            partitions.push([seq[i]]);
        }
        return partitions;
    }
    var solution = linearPartitionTable(seq, k);
    k = k - 2;
    var ans = [];
    while (k >= 0){
        var partial = seq.slice(solution[n-1][k]+1, n+1);
        ans = [partial].concat(ans);
        n = solution[n-1][k];
        k = k - 1;
    }
    ans = [seq.slice(0, n+1)].concat(ans);
    return ans;
}

function linearPartitionTable(seq, k){
    var n = seq.length;
    var table = [];
    var row = [];
    var i, j, x;
    for (i=0; i<k; i++) row.push(0);
    for (i=0; i<n; i++) table.push( row.slice() );

    var solution = [];
    row = [];
    for (i=0; i<(k-1); i++) row.push(0);
    for (i=0; i<(n-1); i++) solution.push( row.slice() );

    for (i=0; i<n; i++){
        var value = seq[i];
        if (i>0){
            value += table[i-1][0];
        }
        table[i][0] = value;
    }
    for (j=0; j<k; j++){
        table[0][j] = seq[0];
    }
    for (i=1; i<n; i++){
        for (j=1; j<k; j++){
            var min = null;
            var minx = null;
            for (x = 0; x < i; x++) {
                var cost = Math.max(table[x][j - 1], table[i][0] - table[x][0]);
                if (min === null || cost < min) {
                    min = cost;
                    minx = x;
                }
            }
            table[i][j] = min;
            solution[i - 1][j - 1] = minx;
        }
    }
    return solution;
}
