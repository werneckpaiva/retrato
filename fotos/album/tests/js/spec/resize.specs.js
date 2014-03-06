var LANDSCAPE = 1.333
var PORTRAIT = 0.750

describe("Resize pictures", function() {

    it("should resize 2 landscape pictures to fit all in the screen", function(){
        var pictures = [{ratio: LANDSCAPE}, {ratio:LANDSCAPE}]
        var resize = new Resize(pictures)
        resize.doResize(1100, 800)

        for (i in pictures){
            expect(pictures[i].newHeight).toBe(400);
            expect(pictures[i].newWidth).toBe(533);
        }
    });

    
    it("should resize 4 pictures in 2 rows", function(){
        var pictures = [{ratio: LANDSCAPE}, {ratio:PORTRAIT}, {ratio:PORTRAIT}, {ratio:LANDSCAPE}]
        var resize = new Resize(pictures)
        resize.doResize(1100, 800)

        expect(pictures[0].newHeight).toBe(400);
        expect(pictures[0].newWidth).toBe(533);
    });

});


describe("Linear partition", function() {
   
    it("should create one partition for each element", function(){
        var s=[1, 2, 3]
        partitions = linearPartition([1,2,3], 5)

        expect(partitions.length).toBe(3);
        for (var i in s){
            expect(partitions[i].length).toBe(1);
            expect(partitions[i][0]).toBe(s[i]);
        }
    });
});