function Resize(pictures, heightProportion){
    this.pictures = pictures;
    this.HEIGHT_PROPORTION = 0.45;
    if (heightProportion){
        this.HEIGHT_PROPORTION = heightProportion
    }
}

Resize.prototype.doResize = function(viewWidth, viewHeight){
    var idealHeight = parseInt(viewHeight * this.HEIGHT_PROPORTION)

    var sumWidths = this.sumWidth(idealHeight)
    var rows = Math.ceil(sumWidths / viewWidth)

//    if (rows <= 1){
//        // fallback to standard size
//        console.log("1 row")
//        this.resizeToSameHeight(idealHeight)
//    } else {
      return this.resizeUsingLinearPartitions(rows, viewWidth)
//    }
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
    var weights = []
    var p;
    for (var i in this.pictures){
        p = this.pictures[i]
        weights.push(parseInt(p.ratio * 100))
    }
    var partitions = linearPartition(weights, rows)
    var index = 0;
    var newDimensions = []
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
            var dimension = {}
            dimension.newWidth = parseInt((viewWidth / summedRatios) * p.ratio)
            dimension.newHeight = parseInt(viewWidth / summedRatios)
            newDimensions.push(dimension)
        }
    }
    return newDimensions;
}

function linearPartition(seq, k){
    if (k <= 0){
        return []
    }

    var n = seq.length - 1;
    var partitions = []
    if (k > n){
        for (i in seq){
            partitions.push([seq[i]])
        }
        return partitions;
    }
    var solution = linearPartitionTable(seq, k)
    k = k - 2;
    var ans = []
    while (k >= 0){
        var partial = seq.slice(solution[n-1][k]+1, n+1)
        ans = [partial].concat(ans)
        n = solution[n-1][k]
        k = k - 1;
    }
    ans = [seq.slice(0, n+1)].concat(ans)
    return ans
}

function linearPartitionTable(seq, k){
    var n = seq.length
    var table = []
    var row = []
    for (var i=0; i<k; i++) row.push(0)
    for (var i=0; i<n; i++) table.push( row.slice() )

    var solution = []
    row = []
    for (var i=0; i<(k-1); i++) row.push(0)
    for (var i=0; i<(n-1); i++) solution.push( row.slice() )

    for (var i=0; i<n; i++){
        var value = seq[i]
        if (i>0){
            value += table[i-1][0]
        }
        table[i][0] = value
    }
    for (var j=0; j<k; j++){
        table[0][j] = seq[0]
    }
    for (var i=1; i<n; i++){
        for (var j=1; j<k; j++){
            var min = null
            var minx = null
            for (var x = 0; x < i; x++) {
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
    return solution
}
