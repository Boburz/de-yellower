# reduces yellowing in image files
from PIL import Image, ImageColor
import time
import random

# calculate squared distance between points 1 and 2
# don't need to take square root, since we are only interested in which one is the largest
def squaredDistance(point1, point2):
    return pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2) + pow(point1[2] - point2[2], 2)

# k means clustering with three centers
def kMeansClustering(pixelList, yellowish, whitish, blackish, max_iteration):
    print('  beginning to optimize:')

    # if there are too many points, just use 100k of them
    useList = pixelList.copy()
    if len(pixelList) > 100000:
        random.shuffle(useList)
        useList = useList[:100000]

    # start iterating
    for iteration in range(max_iteration):
        print('    iteration ' + str(iteration+1) + ' of ' + str(max_iteration) + ' ... ', end='')
        yellowList = []
        whiteList = []
        blackList = []

        # decide whether each of the data points is yellow, white, or black
        for point in range(len(useList)):
            diffToYellow = squaredDistance(useList[point], yellowish)
            diffToWhite  = squaredDistance(useList[point], whitish)
            diffToBlack  = squaredDistance(useList[point], blackish)

            if diffToYellow < diffToWhite and diffToYellow < diffToBlack:
                yellowList.append(point)
            elif diffToWhite < diffToBlack:
                whiteList.append(point)
            else:
                blackList.append(point)

        # calculate new centers
        if len(yellowList) > 0:
            yellowish = [0,0,0]
            for point in yellowList:
                yellowish[0] += useList[point][0]
                yellowish[1] += useList[point][1]
                yellowish[2] += useList[point][2]
            yellowish[0] = int( yellowish[0] / len(yellowList) )
            yellowish[1] = int( yellowish[1] / len(yellowList) )
            yellowish[2] = int( yellowish[2] / len(yellowList) )
        if len(whiteList) > 0:
            whitish = [0,0,0]
            for point in whiteList:
                whitish[0] += useList[point][0]
                whitish[1] += useList[point][1]
                whitish[2] += useList[point][2]
            whitish[0] = int( whitish[0] / len(whiteList) )
            whitish[1] = int( whitish[1] / len(whiteList) )
            whitish[2] = int( whitish[2] / len(whiteList) )
        if len(blackList) > 0:
            blackish = [0,0,0]
            for point in blackList:
                blackish[0] += useList[point][0]
                blackish[1] += useList[point][1]
                blackish[2] += useList[point][2]
            blackish[0] = int( blackish[0] / len(blackList) )
            blackish[1] = int( blackish[1] / len(blackList) )
            blackish[2] = int( blackish[2] / len(blackList) )

        print(yellowish, whitish, blackish)

    print('  optimization done')
    return (yellowish, whitish, blackish)

##############
# Parameters #
##############

max_iteration = 5

# start values for cluster centers
yellowish = [200, 170, 130]
whitish = [255, 255, 255]
blackish = [0, 0, 0]

# how much will points of each cluster be moved to their "ideal" values?
# 0.00: no movement; 1.00: set to "ideal"
# "ideal" is "white" for white and yellow, and "black" for black
cRY = 0.99
cRW = 0.50
cRB = 0.50

################################################################################
################################################################################
################################################################################

print('START')
start_time = time.time()

# open input file
inFile = '38_bemalt.png'
inImage = Image.open(inFile)
width, height = inImage.size
print('  loaded file ' + str(inFile) + '...')

# determine output file
if inFile.endswith('.png'):
    outFile = inFile[:-4] + '_deyellowed_' + str(int(cRY*100)) + '-' + str(int(cRW*100)) + '-' + str(int(cRB*100)) + '.png'
elif inFile.endswith('.jpg'):
    outFile = inFile[:-4] + '_deyellowed_' + str(int(cRY*100)) + '-' + str(int(cRW*100)) + '-' + str(int(cRB*100)) + '.jpg'
else:
    print('ERROR: input file has invalid file extension')

# build list with pixels
print('  loading pixels...')
pixelList = []
for yCoord in range(height):
    for xCoord in range(width):
        pixelList.append( list(inImage.getpixel((xCoord, yCoord))[:3]) )

# do the k means clustering
(yellowish, whitish, blackish) = kMeansClustering(pixelList, yellowish, whitish, blackish, max_iteration)
opti_time = time.time()

# for known problems, we can skip the k means clustering
#(yellowish, whitish, blackish) = ([222, 177, 134], [254, 254, 254], [51, 33, 27])

# calculate new pixels
print('  adjusting pixels...')
for yCoord in range(height):
    for xCoord in range(width):
        # get old pixel
        pixelID = (xCoord + width*yCoord)
        pixel = pixelList[pixelID][:3]

        # calculate new pixel color
        diffToYellow = squaredDistance(pixel, yellowish)
        diffToWhite  = squaredDistance(pixel, whitish)
        diffToBlack  = squaredDistance(pixel, blackish)
        if diffToYellow < diffToWhite and diffToYellow < diffToBlack:
            ideal = whitish
            changeRate = cRY
        elif diffToWhite < diffToBlack:
            ideal = whitish
            changeRate = cRW
        else:
            ideal = blackish
            changeRate = cRB

        pixel[0] = int(changeRate * (ideal[0] - pixel[0]) + pixel[0] )
        pixel[1] = int(changeRate * (ideal[1] - pixel[1]) + pixel[1] )
        pixel[2] = int(changeRate * (ideal[2] - pixel[2]) + pixel[2] )

        # put updated pixel into image
        inImage.putpixel((xCoord, yCoord), (pixel[0], pixel[1], pixel[2], 255))
adjust_time = time.time()

# write into output file
print('  writing to file ' + str(outFile) + '...')
inImage.save(outFile)
write_time = time.time()

# evaluating time used
print('  time consumed:')
print('    k means clustering: ' + str(int(opti_time - start_time)) + ' sec')
print('    adjusting pixels:   ' + str(int(adjust_time - opti_time)) + ' sec')
print('    saving image:       ' + str(int(write_time - adjust_time)) + ' sec')

print('DONE.')

