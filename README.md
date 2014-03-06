fotos
=====

Inspirado pelo projeto http://www.chromatic.io/

Requirements:

Django==1.6.2
Pillow=2.3.0


viewport_width = $(window).width()
ideal_height = parseInt($(window).height() / 2)
summed_width = photos.reduce ((sum, p) -> sum += p.get('aspect_ratio') * ideal_height), 0
rows = Math.round(summed_width / viewport_width)
 
if rows < 1
  # (2a) Fallback to just standard size 
  photos.each (photo) -> photo.view.resize parseInt(ideal_height * photo.get('aspect_ratio')), ideal_height
else
  # (2b) Distribute photos over rows using the aspect ratio as weight
  weights = photos.map (p) -> parseInt(p.get('aspect_ratio') * 100)
  partition = linear_partition(weights, rows)

  # (3) Iterate through partition
  index = 0
  row_buffer = new Backbone.Collection
  _.each partition, (row) ->
    row_buffer.reset()
    _.each row, -> row_buffer.add(photos.at(index++))
    summed_ratios = row_buffer.reduce ((sum, p) -> sum += p.get('aspect_ratio')), 0
    row_buffer.each (photo) -> photo.view.resize parseInt(viewport_width / summed_ratios * photo.get('aspect_ratio')), parseInt(viewport_width / summed_ratios)
    
    

    
# Linear partition
# Partitions a sequence of non-negative integers into k ranges
# Based on Óscar López implementation in Python (http://stackoverflow.com/a/7942946)
# Also see http://www8.cs.umu.se/kurser/TDBAfl/VT06/algorithms/BOOK/BOOK2/NODE45.HTM
# Dependencies: UnderscoreJS (http://www.underscorejs.org)
# Example: linear_partition([9,2,6,3,8,5,8,1,7,3,4], 3) => [[9,2,6,3],[8,5,8],[1,7,3,4]]
 
linear_partition = (seq, k) =>
  n = seq.length
  
  return [] if k <= 0
  return seq.map((x) -> [x]) if k > n
 
  table = (0 for x in [0...k] for y in [0...n])
  solution = (0 for x in [0...k-1] for y in [0...n-1])
  table[i][0] = seq[i] + (if i then table[i-1][0] else 0) for i in [0...n]
  table[0][j] = seq[0] for j in [0...k]
  for i in [1...n]
    for j in [1...k]
      m = _.min(([_.max([table[x][j-1], table[i][0]-table[x][0]]), x] for x in [0...i]), (o) -> o[0])
      table[i][j] = m[0]
      solution[i-1][j-1] = m[1]
 
  n = n-1
  k = k-2
  ans = []
  while k >= 0
    ans = [seq[i] for i in [(solution[n-1][k]+1)...n+1]].concat ans
    n = solution[n-1][k]
    k = k-1
 
  [seq[i] for i in [0...n+1]].concat ans
  
  
  
  
  from operator import itemgetter

def linear_partition(seq, k):
    if k <= 0:
        return []
    n = len(seq) - 1
    if k > n:
        return map(lambda x: [x], seq)
    table, solution = linear_partition_table(seq, k)
    k, ans = k-2, []
    while k >= 0:
        ans = [[seq[i] for i in xrange(solution[n-1][k]+1, n+1)]] + ans
        n, k = solution[n-1][k], k-1
    return [[seq[i] for i in xrange(0, n+1)]] + ans

def linear_partition_table(seq, k):
    n = len(seq)
    table = [[0] * k for x in xrange(n)]
    solution = [[0] * (k-1) for x in xrange(n-1)]
    for i in xrange(n):
        table[i][0] = seq[i] + (table[i-1][0] if i else 0)
    for j in xrange(k):
        table[0][j] = seq[0]
    for i in xrange(1, n):
        for j in xrange(1, k):
            table[i][j], solution[i-1][j-1] = min(
                ((max(table[x][j-1], table[i][0]-table[x][0]), x) for x in xrange(i)),
                key=itemgetter(0))
    return (table, solution)
    
    
    
    
    
row_buffer.each (photo) -> 
   photo.view.resize 
      parseInt(viewport_width / summed_ratios * photo.get('aspect_ratio')), 
      parseInt(viewport_width / summed_ratios)