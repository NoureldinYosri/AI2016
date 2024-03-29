#!/usr/bin/env python
#
# Sudoku Generator and Solver in 250 lines of python
# Copyright (c) 2006 David Bau.  All rights reserved.
#
# Can be used as either a command-line tool or as a cgi script.
#
# As a cgi-script, generates puzzles and estimates their level of
# difficulty.  Uses files sudoku-template.pdf/.ps/.txt/.html
# in which it can fill in 81 underscores with digits for a puzzle.
# The suffix of the request URL determines which template is used.
#
# On a command line without any arguments, prints text for a
# random sudoku puzzle, with an estimate of its difficulty.
# On a command line with a filename, solves the given puzzles
# (files should look like the text generated by the generator).

import sys, os, random, getopt, re

def main():
  args = sys.argv[1:]
  if len(args) > 0:
    puzzles = [loadboard(filename) for filename in args]
  else:
    puzzles = [makepuzzle(solution([None] * 81))]
  for puzzle in puzzles:
    print "PUZZLE:"
    print printboard(puzzle)
    print "RATING:", ratepuzzle(puzzle, 4)
    if True: #len(args) > 0:
      print
      print "SOLUTION:"
      answer = solution(puzzle)
      if answer is None: print "NO SOLUTION"
      else: print printboard(answer)

def cgimain():
  query = os.getenv('QUERY_STRING', '')
  pathinfo = os.getenv('REQUEST_URI', '').split('?', 1)[0] or ''
  for ext in ['pdf', 'ps', 'txt', 'html']:
    if pathinfo.endswith(ext): break
  template = loadsudokutemplate(ext)
  texttype = {'pdf':'application/pdf', 'ps':'application/postscript',
              'txt':'text/plain', 'html':'text/html'}[ext]
  print "Content-Type: %s" % texttype
  print "Content-Length: %d" % len(template)
  print "Cache-Control: no-cache"
  print "Expires: Sat, 01 Jan 2000 00:00:00 GMT"
  print
  segments = template.split('_', 81)
  sys.stdout.write(segments[0])
  sys.stdout.flush()
  digits = re.search(r'\d{81}', query)
  if digits:
    puzzle = parseboard(digits.group(0))
  else:
    puzzle = makepuzzle(solution([None] * 81))
  if ext in ['pdf', 'ps']:
    puzzle = [puzzle[x % 9 + 72 - (x - x % 9)] for x in xrange(81)]
  ratingstr = '%1.2f' % ratepuzzle(puzzle, 4)
  for pos in xrange(81):
    if puzzle[pos] is None: sys.stdout.write(' ')
    else: sys.stdout.write(str(puzzle[pos] + 1))
    sys.stdout.write(segments[pos + 1].replace('####', ratingstr))

def makepuzzle(board):
  puzzle = []; deduced = [None] * 81
  order = random.sample(xrange(81), 81)
  for pos in order:
    if deduced[pos] is None:
      puzzle.append((pos, board[pos]))
      deduced[pos] = board[pos]
      deduce(deduced)
  random.shuffle(puzzle)
  for i in xrange(len(puzzle) - 1, -1, -1):
    e = puzzle[i]; del puzzle[i]
    rating = checkpuzzle(boardforentries(puzzle), board)
    if rating == -1: puzzle.append(e)
  return boardforentries(puzzle)

def ratepuzzle(puzzle, samples):
  total = 0
  for i in xrange(samples):
    state, answer = solveboard(puzzle)
    if answer is None: return -1
    total += len(state)
  return float(total) / samples

def checkpuzzle(puzzle, board = None):
  state, answer = solveboard(puzzle)
  if answer is None: return -1
  if board is not None and not boardmatches(board, answer): return -1
  difficulty = len(state)
  state, second = solvenext(state)
  if second is not None: return -1
  return difficulty

def solution(board):
  return solveboard(board)[1]

def solveboard(original):
  board = list(original)
  guesses = deduce(board)
  if guesses is None: return ([], board)
  track = [(guesses, 0, board)]
  return solvenext(track)

def solvenext(remembered):
  while len(remembered) > 0:
    guesses, c, board = remembered.pop()
    if c >= len(guesses): continue
    remembered.append((guesses, c + 1, board))
    workspace = list(board)
    pos, n = guesses[c]
    workspace[pos] = n
    guesses = deduce(workspace)
    if guesses is None: return (remembered, workspace)
    remembered.append((guesses, 0, workspace))
  return ([], None)

def deduce(board):
  while True:
    stuck, guess, count = True, None, 0
    # fill in any spots determined by direct conflicts
    allowed, needed = figurebits(board)
    for pos in xrange(81):
      if None == board[pos]:
        numbers = listbits(allowed[pos])
        if len(numbers) == 0: return []
        elif len(numbers) == 1: board[pos] = numbers[0]; stuck = False
        elif stuck:
          guess, count = pickbetter(guess, count, [(pos, n) for n in numbers])
    if not stuck: allowed, needed = figurebits(board)
    # fill in any spots determined by elimination of other locations
    for axis in xrange(3):
      for x in xrange(9):
        numbers = listbits(needed[axis * 9 + x])
        for n in numbers:
          bit = 1 << n
          spots = []
          for y in xrange(9):
            pos = posfor(x, y, axis)
            if allowed[pos] & bit: spots.append(pos)
          if len(spots) == 0: return []
          elif len(spots) == 1: board[spots[0]] = n; stuck = False
          elif stuck:
            guess, count = pickbetter(guess, count, [(pos, n) for pos in spots])
    if stuck:
      if guess is not None: random.shuffle(guess)
      return guess

def figurebits(board):
  allowed, needed = [e is None and 511 or 0 for e in board], []
  for axis in xrange(3):
    for x in xrange(9):
      bits = axismissing(board, x, axis)
      needed.append(bits)
      for y in xrange(9):
        allowed[posfor(x, y, axis)] &= bits
  return allowed, needed

def posfor(x, y, axis = 0):
  if axis == 0: return x * 9 + y
  elif axis == 1: return y * 9 + x
  else: return ((0,3,6,27,30,33,54,57,60)[x] + (0,1,2,9,10,11,18,19,20)[y])

def axisfor(pos, axis):
  if axis == 0: return pos / 9
  elif axis == 1: return pos % 9
  else: return (pos / 27) * 3 + (pos / 3) % 3

def axismissing(board, x, axis):
  bits = 0
  for y in xrange(9):
    e = board[posfor(x, y, axis)]
    if e is not None: bits |= 1 << e
  return 511 ^ bits
  
def listbits(bits):
  return [y for y in xrange(9) if 0 != bits & 1 << y]

def allowed(board, pos):
  bits = 511
  for axis in xrange(3):
    x = axisfor(pos, axis)
    bits &= axismissing(board, x, axis)
  return bits

def pickbetter(b, c, t):
  if b is None or len(t) < len(b): return (t, 1)
  if len(t) > len(b): return (b, c)
  if random.randint(0, c) == 0: return (t, c + 1)
  else: return (b, c + 1)

def entriesforboard(board):
  return [(pos, board[pos]) for pos in xrange(81) if board[pos] is not None]

def boardforentries(entries):
  board = [None] * 81
  for pos, n in entries: board[pos] = n
  return board

def boardmatches(b1, b2):
  for i in xrange(81):
    if b1[i] != b2[i]: return False
  return True

def printcode(n):
  if n is None: return '_'
  return str(n + 1)

def printboard(board):
  out = ""
  for row in xrange(9):
    for col in xrange(9):
      out += (""," "," ","  "," "," ","  "," "," ")[col]
      out += printcode(board[posfor(row, col)])
    out += ('\n','\n','\n\n','\n','\n','\n\n','\n','\n','\n')[row]
  return out

def parseboard(str):
  result = []
  for w in str.split():
    for x in w:
      if x in '|-=+': continue
      if x in '123456789': result.append(int(x) - 1)
      else: result.append(None)
      if len(result) == 81: return result

def loadboard(filename):
  f = file(filename, 'r')
  result = parseboard(f.read())
  f.close()
  return result

def basedir():
  if hasattr(sys.modules[__name__], '__file__'):
    return os.path.split(__file__)[0]
  elif __name__ == '__main__':
    if len(sys.argv) > 0 and sys.argv[0] != '':
      return os.path.split(sys.argv[0])[0]
    else:
      return os.curdir

def loadsudokutemplate(ext):
  f = open(os.path.join(basedir(), 'sudoku-template.%s' % ext), 'r')
  result = f.read()
  f.close()
  return result

if __name__ == "__main__":
  if os.getenv('GATEWAY_INTERFACE') is not None: sys.exit(cgimain())
  sys.exit(main())

