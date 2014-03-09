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

    
    it("should resize 4 landscape pictures in 2 rows", function(){
        var pictures = [{ratio: LANDSCAPE}, {ratio:LANDSCAPE}, {ratio:LANDSCAPE}, {ratio:LANDSCAPE}]
        var resize = new Resize(pictures)
        resize.doResize(1100, 800)

        for (i in pictures){
            expect(pictures[i].newHeight).toBe(412);
            expect(pictures[i].newWidth).toBe(550);
        }
    });

});


describe("Linear partition", function() {
   
    it("should create one partition for each element", function(){
        var s=[1, 2, 3]
        var partitions = linearPartition(s, 5)

        expect(partitions.length).toBe(3);
        for (var i in partitions){
            expect(partitions[i].length).toBe(1);
            expect(partitions[i][0]).toBe(s[i]);
        }
    });

    it("should create 3 partition equal size", function(){
        var s=[1, 1, 1, 1, 1, 1]
        var partitions = linearPartition(s, 3)

        expect(partitions.length).toBe(3);
        for (var i in partitions){
            expect(partitions[i].length).toBe(2);
        }
    });

    it("parition [9,2,6,3,8,5,8,1,7,3,4], 3) should get [[9,2,6,3],[8,5,8],[1,7,3,4]", function(){
        var s=[9,2,6,3,8,5,8,1,7,3,4]
        var partitions = linearPartition(s, 3)

        expect(partitions.length).toBe(3);
        
        expect(partitions[0][0]).toBe(9);
        expect(partitions[0][1]).toBe(2);
        expect(partitions[0][2]).toBe(6);
        expect(partitions[0][3]).toBe(3);

        expect(partitions[1][0]).toBe(8);
        expect(partitions[1][1]).toBe(5);
        expect(partitions[1][2]).toBe(8);

        expect(partitions[2][0]).toBe(1);
        expect(partitions[2][1]).toBe(7);
        expect(partitions[2][2]).toBe(3);
        expect(partitions[2][3]).toBe(4);
    });
});