function Highlight(selector){

    var self = this
    var $this = selector

    function init(){
        addEventListeners()
    }

    function addEventListeners(){
        $this.click(function(){
            self.closePicture()
        })
    }

    this.displayPicture = function(picture){
        $window = $(window)
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

        $content = $this.find(".content")
        $content.hide()
        $content.css("background-size", newWidth+"px "+newHeight+"px");
        $content.css("background-position", x+"px "+y+"px");

        $this.css("background-image", "url("+picture.thumb+")")
        $this.css("background-size", newWidth+"px "+newHeight+"px");
        $this.css("background-position", x+"px "+y+"px");
        
        var $fundo = $(".blur", $this);
        $fundo.attr("src", picture.thumb);
        
        image = new Image()
        image.onload = function(){
            $content.css("background-image", "url("+this.src+")")
            $content.fadeIn();
        }
        image.src = picture.highlight
        $this.fadeIn();
        
        $fundo.addClass("visivel");
    }
    
    this.closePicture = function(){
        $this.fadeOut();
        var $fundo = $(".blur", $this);
        $fundo.removeClass("visivel");
    }

    init()
}