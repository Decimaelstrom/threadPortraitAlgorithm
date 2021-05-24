from PIL import Image, ImageOps, ImageDraw
from bresenham import bresenham
from skimage.color import rgb2gray
from skimage.draw import line
import numpy as np
import matplotlib.pyplot as plt
# import sys
from argparse import ArgumentParser as AP


#GET INPUT CONSTANTS HERE

parser = AP(description='Thread-Art Conversion Algorithm: converts image into thread art instructions')

# args = sys.argv
parser.add_argument('--board_width', '-w', type=int, default=58, help='board width in CM (default 58)')
parser.add_argument('--pixel_width', '-p', type=float, default=1, help='ex: 1 - suggest keeping this constant and changing board width only (default 1)')
parser.add_argument('--line_transparancy', '-t', type=float, default=0.2, help='value between 0 and 1 (default 0.2)')
parser.add_argument('--num_nails', '-n', type=int, default=300, help='number of nails (default:300)')
parser.add_argument('--max_iterations', '-i',  type=int, default=4000, help='number of iterations (default 4000)')
parser.add_argument('--image_file', '-f',  type=str, default='image.jpg', help='source image file to transform (default "image.jpg")')
args = parser.parse_args()
NAILS_SKIP = 10
OUTPUT_TITLE = "output"

pixels = int(args.board_width/args.pixel_width)
size = (pixels+1, pixels+1)

def cropToCircle(path):
    img = Image.open(path).convert("L")
    img = img.resize(size);
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    mask = mask.resize(img.size, Image.ANTIALIAS)
    img.putalpha(mask)

    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

#Cropping image to a circle
ref = cropToCircle(args.image_file)

base = Image.new('L', size, color=255)

#Calculating pixels and setting up nail perimeter
angles = np.linspace(0, 2*np.pi, args.num_nails)  # angles to the dots
cx, cy = (args.board_width/2/args.pixel_width, args.board_width/2/args.pixel_width)  # center of circle
xs = cx + args.board_width*0.5*np.cos(angles)/args.pixel_width
ys = cy + args.board_width*0.5*np.sin(angles)/args.pixel_width
nails = list(map(lambda x,y: (int(x),int(y)), xs,ys))
results = open("results.txt", "w")
res = ""

#Uncomment to show nails plot
plt.scatter(xs, ys, c = 'red', s=2)
plt.show()

cur_nail = 1        #start at arbitrary nail
ref_arr = np.transpose(np.array(ref)[:, :, 0])
base_arr = base.load()

for i in range(args.max_iterations):
    best_line = None
    new_nail = None
    min_avg_value = 10000
    for n in range(cur_nail+1+NAILS_SKIP,cur_nail+len(nails)-NAILS_SKIP):
        n = n%args.num_nails
        tmp_value = 0
        new_line = line(nails[cur_nail][0], nails[cur_nail][1], nails[n][0], nails[n][1])
        num_pts = len(new_line[0])

        tmp_value = np.sum(ref_arr[new_line])

        if tmp_value/num_pts < min_avg_value:
            best_line = new_line
            new_nail = n
            #print(new_nail,tmp_value/num_pts)
            min_avg_value = tmp_value/num_pts

    #Uncomment for progress pictures every x=200 iterations
    #if i%200 == 0:
    #    title = OUTPUT_TITLE+str(args.board_width)+'W-'+str(args.pixel_width)+"P-"+str(args.num_nails)+'N-'+str(i)+'-'+str(LINE_TRANSPARENCY)+'.png'
    #    print(title)
    #    base.save(title)
    #    res += "\n --- "+str(i)+" --- \n"

    ref_arr[best_line] = 255
    addLine = ImageDraw.Draw(base)
    addLine.line((nails[cur_nail][0],nails[cur_nail][1],nails[new_nail][0],nails[new_nail][1]), fill=0)
    res += " " + str(new_nail)
    print("Iteration ",i, " Complete: ","(",cur_nail,",",new_nail,")")
    cur_nail = new_nail

results.write(res)
results.close()
title = OUTPUT_TITLE+str(args.board_width)+'W-'+str(args.pixel_width)+"P-"+str(args.num_nails)+'N-'+str(args.max_iterations)+'-'+str(args.line_transparancy)+'.png'
base.save(title)
