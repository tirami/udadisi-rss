import extract

lines = tuple(open("tweets.txt", 'r'))
for l in lines:
    print ""
    print l
    print extract.process_status(l)

