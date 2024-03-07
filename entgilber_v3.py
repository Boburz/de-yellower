# reduces yellowing in image files
from PIL import Image, ImageColor
import time
import random

# calculate squared distance between points 1 and 2
# don't need to take square root, since we are only interested in which one is the largest
def squared_distance(point1, point2):
    return pow(point1[0] - point2[0], 2) + pow(point1[1] - point2[1], 2) + pow(point1[2] - point2[2], 2)

# k means clustering with three centers
def k_means_clustering(pixel_list, yellowish, whitish, blackish, max_iteration):
    print('  beginning to optimize:')

    # if there are too many points, just use 100k of them
    use_list = pixel_list.copy()
    if len(pixel_list) > 100000:
        random.shuffle(use_list)
        use_list = use_list[:100000]

    # start iterating
    for iteration in range(max_iteration):
        print('    iteration ' + str(iteration+1) + ' of ' + str(max_iteration) + ' ... ', end='')
        yellow_list = []
        white_list = []
        black_list = []

        # decide whether each of the data points is yellow, white, or black
        for point in range(len(use_list)):
            diff_to_yellow = squared_distance(use_list[point], yellowish)
            diff_to_white  = squared_distance(use_list[point], whitish)
            diff_to_black  = squared_distance(use_list[point], blackish)

            if diff_to_yellow < diff_to_white and diff_to_yellow < diff_to_black:
                yellow_list.append(point)
            elif diff_to_white < diff_to_black:
                white_list.append(point)
            else:
                black_list.append(point)

        # calculate new centers
        if len(yellow_list) > 0:
            yellowish = [0,0,0]
            for point in yellow_list:
                yellowish[0] += use_list[point][0]
                yellowish[1] += use_list[point][1]
                yellowish[2] += use_list[point][2]
            yellowish[0] = int( yellowish[0] / len(yellow_list) )
            yellowish[1] = int( yellowish[1] / len(yellow_list) )
            yellowish[2] = int( yellowish[2] / len(yellow_list) )
        if len(white_list) > 0:
            whitish = [0,0,0]
            for point in white_list:
                whitish[0] += use_list[point][0]
                whitish[1] += use_list[point][1]
                whitish[2] += use_list[point][2]
            whitish[0] = int( whitish[0] / len(white_list) )
            whitish[1] = int( whitish[1] / len(white_list) )
            whitish[2] = int( whitish[2] / len(white_list) )
        if len(black_list) > 0:
            blackish = [0,0,0]
            for point in black_list:
                blackish[0] += use_list[point][0]
                blackish[1] += use_list[point][1]
                blackish[2] += use_list[point][2]
            blackish[0] = int( blackish[0] / len(black_list) )
            blackish[1] = int( blackish[1] / len(black_list) )
            blackish[2] = int( blackish[2] / len(black_list) )

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
changerate_yellow = 0.99
changerate_white = 0.50
changerate_black = 0.50

################################################################################
################################################################################
################################################################################

print('START')
start_time = time.time()

# open input file
input_file = '38_bemalt.png'
input_image = Image.open(input_file)
width, height = input_image.size
print('  loaded file ' + str(input_file) + '...')

# determine output file
if input_file.endswith('.png'):
    output_file = input_file[:-4] + '_deyellowed_' + str(int(changerate_yellow*100)) \
    + '-' + str(int(changerate_white*100)) + '-' + str(int(changerate_black*100)) + '.png'
elif input_file.endswith('.jpg'):
    output_file = input_file[:-4] + '_deyellowed_' + str(int(changerate_yellow*100)) \
    + '-' + str(int(changerate_white*100)) + '-' + str(int(changerate_black*100)) + '.jpg'
else:
    print('ERROR: input file has invalid file extension')

# build list with pixels
print('  loading pixels...')
pixel_list = []
for y_coord in range(height):
    for x_coord in range(width):
        pixel_list.append( list(input_image.getpixel((x_coord, y_coord))[:3]) )

# do the k means clustering
(yellowish, whitish, blackish) = k_means_clustering(pixel_list, yellowish, whitish, blackish, max_iteration)
opti_time = time.time()

# for known problems, we can skip the k means clustering
#(yellowish, whitish, blackish) = ([222, 177, 134], [254, 254, 254], [51, 33, 27])

# calculate new pixels
print('  adjusting pixels...')
for y_coord in range(height):
    for x_coord in range(width):
        # get old pixel
        pixel_ID = (x_coord + width*y_coord)
        pixel = pixel_list[pixel_ID][:3]

        # calculate new pixel color
        diff_to_yellow = squared_distance(pixel, yellowish)
        diff_to_white  = squared_distance(pixel, whitish)
        diff_to_black  = squared_distance(pixel, blackish)
        if diff_to_yellow < diff_to_white and diff_to_yellow < diff_to_black:
            ideal = whitish
            changerate = changerate_yellow
        elif diff_to_white < diff_to_black:
            ideal = whitish
            changerate = changerate_white
        else:
            ideal = blackish
            changerate = changerate_black

        pixel[0] = int(changerate * (ideal[0] - pixel[0]) + pixel[0] )
        pixel[1] = int(changerate * (ideal[1] - pixel[1]) + pixel[1] )
        pixel[2] = int(changerate * (ideal[2] - pixel[2]) + pixel[2] )

        # put updated pixel into image
        input_image.putpixel((x_coord, y_coord), (pixel[0], pixel[1], pixel[2], 255))
adjust_time = time.time()

# write into output file
print('  writing to file ' + str(output_file) + '...')
input_image.save(output_file)
write_time = time.time()

# evaluating time used
print('  time consumed:')
print('    k means clustering: ' + str(int(opti_time - start_time)) + ' sec')
print('    adjusting pixels:   ' + str(int(adjust_time - opti_time)) + ' sec')
print('    saving image:       ' + str(int(write_time - adjust_time)) + ' sec')

print('DONE.')

