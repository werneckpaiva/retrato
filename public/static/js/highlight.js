function Highlight(selector){

    var self = this
    var $this = selector
    var opened = false

    var picture = null;

    function init(){
        addEventListeners()
    }

    function addEventListeners(){
        $this.click(function(){
            self.closePicture()
        })
        $(window).resize(function(){
            updateDisplay();
        })

        $this.find("#photo-details").bind("click", function(e){return false;})
    }

    this.displayPicture = function(p){
        picture = p;
        opened = true
        updateDisplay();
    }

    function updateDisplay(){
        if (!picture || !opened){
            return;
        }
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

        $highRes = $this.find(".high-res")
        $highRes.hide()
        $highRes.css("width", newWidth+"px").css("height", newHeight+"px");
        $highRes.css("left", x+"px").css("top", y+"px");

        var $lowRes = $this.find(".low-res");
        $lowRes.attr("src", picture.thumb)
        $lowRes.css("width", newWidth+"px").css("height", newHeight+"px");
        $lowRes.css("left", x+"px").css("top", y+"px");

        var $blur = $(".blur", $this);
        $blur.attr("src", picture.thumb);

        image = new Image()
        image.onload = function(){
            $highRes.attr("src", this.src)
            $highRes.fadeIn();
        }
        image.src = picture.highlight
        $this.fadeIn();

        setTimeout(function(){
            $blur.addClass("visible");
        }, 500)

        // photo details
        var $details = $this.find("#photo-details");
        $details.find(".name").html(picture.name);
        $details.find(".album").html( $("#photos").attr("data-album-name") );
        $details.find(".date").html( picture.date.split(" ")[0].split("-").reverse().join("/") );

    }

    this.closePicture = function(){
        $this.fadeOut();
        var $blur = $(".blur", $this);
        $blur.removeClass("visible");
        opened = false
    }

    init()
}