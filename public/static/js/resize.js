function Resize(pictures){
    this.pictures = pictures
}

Resize.prototype.HEIGHT_PROPORTION = 0.5

Resize.prototype.doResize = function(viewWidth, viewHeight){
    var idealHeight = parseInt(viewHeight * this.HEIGHT_PROPORTION)

    var sumWidths = this.sumWidth(idealHeight)
    var rows = Math.round(sumWidths / viewWidth)

    if (rows <= 1){
        // fallback to standard size
        this.resizeToSameHeight(idealHeight)
    } else {
        this.resizeUsingLinearPartitions(rows, viewWidth)
    }
}

Resize.prototype.sumWidth = function(height){
    var sumWidths = 0;
    var p
    for (var i in this.pictures){
        p = this.pictures[i]
        sumWidths += p.ratio * height
    }
    return sumWidths;
}

Resize.prototype.resizeToSameHeight = function(height){
    var p
    for (var i in this.pictures){
        p = this.pictures[i]
        p.newWidth = parseInt(height * p.ratio)
        p.newHeight = height
    }
    return this.pictures
}

Resize.prototype.resizeUsingLinearPartitions = function(rows, viewWidth){
    var weights = 0
    var p;
    for (var i in this.pictures){
        p = this.pictures[i]
        weights += parseInt(p.ratio * 100)
    }
    var partitions = linearPartition(weights, rows)
    var index = 0;
    for(var i in partitions){
        partition = partitions[i]
        var rowList = []
        for(j in partition){
            rowList.push(this.pictures[index])
            index++
        }
        var summedRatios = 0;
        for (j in rowList){
            p = rowList[j]
            summedRatios += p.ratio
        }
        for (j in rowList){
            p = rowList[j]
            p.newWidth = parseInt((viewWidth / summedRatios) * p.ratio)
            p.newHeight = parseInt(viewWidth / summedRatios)
        }
    }
}


function linearPartition(seq, k){
    if (k <= 0){
        return []
    }

    var n = seq.length;
    var partitions = []
    if (k > n){
        for (i in seq){
            partitions.push([seq[i]])
        }
        return partitions;
    }

}