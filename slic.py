import numpy
import sys
import cv2
import tqdm
import os
# using algorithm in 3.2 apply image gradients as computed in eq2:
# G(x,y) = ||I(x+1,y) - I(x-1,y)||^2+ ||I(x,y+1) - I(x,y-1)||^2

# SLIC implements a special case of k-means clustering algorithm. 
# Was recommended to use an off the shelf algorithm for clustering but
# because this algorithm is based on this special case of k-means, 
# I kept this implementation to stay true to the algorithm.

def generate_pixels(SLIC_m,step,SLIC_height,SLIC_width,SLIC_ITERATIONS,SLIC_centers,SLIC_labimg,img,SLIC_distances,SLIC_clusters,slic_fuse):
    indnp = numpy.mgrid[0:SLIC_height,0:SLIC_width].swapaxes(0,2).swapaxes(0,1)
    #print('1',numpy.mgrid[0:SLIC_height,0:SLIC_width].shape)#2,1024,1024
    #print('2 is:',numpy.mgrid[0:SLIC_height,0:SLIC_width].swapaxes(0,2))
    #print('3 is:',numpy.mgrid[0:SLIC_height,0:SLIC_width].swapaxes(0,2).swapaxes(0,1))
    #print('indnp',indnp.shape)#1024,1024,2
    for i in tqdm.tqdm(range(SLIC_ITERATIONS)):#4迭代4次
        SLIC_distances = 1 * numpy.ones(img.shape[:2])#1024，024
        for j in range(SLIC_centers.shape[0]):#400，5，shape[0]=400
            x_low, x_high = int(SLIC_centers[j][3] - step), int(SLIC_centers[j][3] + step)
            y_low, y_high = int(SLIC_centers[j][4] - step), int(SLIC_centers[j][4] + step)

            if x_low <= 0:
                x_low = 0
            #end
            if x_high > SLIC_width:
                x_high = SLIC_width
            #end
            if y_low <=0:
                y_low = 0
            #end
            if y_high > SLIC_height:
                y_high = SLIC_height
            #end

            cropimg = SLIC_labimg[y_low : y_high , x_low : x_high]
            #print('cropimg',cropimg.shape)#(96,96,3)
            color_diff = cropimg - SLIC_labimg[int(SLIC_centers[j][4]), int(SLIC_centers[j][3])]
            #print('color_diff',color_diff.shape)#(96,96,3)
            color_distance = numpy.sqrt(numpy.sum(numpy.square(color_diff), axis=2))
            #print('color_distance',color_distance.shape)#(96,96)
            yy, xx = numpy.ogrid[y_low : y_high, x_low : x_high]
            #print('yy',yy.shape)#(96,1)
            #print('xx',xx.shape)#(1,96)
            #print('yy',yy)
            pixdist = ((yy-SLIC_centers[j][4])**2 + (xx-SLIC_centers[j][3])**2)**0.5
            #print('dist',yy-SLIC_centers[j][4])#[[-48],[-47]...[47],[49]]
            # SLIC_m is "m" in the paper, (m/S)*dxy
            #print('pixdist',pixdist.shape)#(96,96)

            dist = ((color_distance/SLIC_m)**2 + (pixdist/step)**2)**0.5
            #print('dist',dist.shape)#(96,96)
            distance_crop = SLIC_distances[y_low : y_high, x_low : x_high]
            idx = dist < distance_crop
            distance_crop[idx] = dist[idx]
            SLIC_distances[y_low : y_high, x_low : x_high] = distance_crop
            #print('SLIC_distances',SLIC_distances[y_low : y_high, x_low : x_high])
            SLIC_clusters[y_low : y_high, x_low : x_high][idx] = j
            slic_fuse[y_low : y_high, x_low : x_high][idx] = j
            #print('j',j)
            #print('slic_fuse',SLIC_clusters[y_low : y_high, x_low : x_high])
        #end

        for k in range(len(SLIC_centers)):
            idx = (SLIC_clusters == k)
            #print('idx',idx)
            colornp = SLIC_labimg[idx]
            #print('colornp',colornp)
            #print('colornp',colornp.shape)#,无形状
            distnp = indnp[idx]
            SLIC_centers[k][0:3] = numpy.sum(colornp, axis=0)
            sumy, sumx = numpy.sum(distnp, axis=0)
            SLIC_centers[k][3:] = sumx, sumy
            SLIC_centers[k] /= numpy.sum(idx)
        #end
    return SLIC_centers,SLIC_clusters,slic_fuse
#end

# At the end of the process, some stray labels may remain meaning some pixels
# may end up having the same label as a larger pixel but not be connected to it
# In the SLIC paper, it notes that these cases are rare, however this 
# implementation seems to have a lot of strays depending on the inputs given
def create_connectivity(SLIC_width,SLIC_height,SLIC_centers,SLIC_clusters,img):
    label = 0
    adj_label = 0
    lims = int(SLIC_width * SLIC_height / SLIC_centers.shape[0])
    
    new_clusters = -1 * numpy.ones(img.shape[:2]).astype(numpy.int64)
    elements = []
    for i in range(SLIC_width):
        for j in range(SLIC_height):
            if new_clusters[j, i] == -1:
                elements = []
                elements.append((j, i))
                for dx, dy in [(-1,0), (0,-1), (1,0), (0,1)]:
                    x = elements[0][1] + dx
                    y = elements[0][0] + dy
                    if (x>=0 and x < SLIC_width and 
                        y>=0 and y < SLIC_height and 
                        new_clusters[y, x] >=0):
                        adj_label = new_clusters[y, x]
                    #end
                #end
            #end

            count = 1
            counter = 0
            while counter < count:
                for dx, dy in [(-1,0), (0,-1), (1,0), (0,1)]:
                    x = elements[counter][1] + dx
                    y = elements[counter][0] + dy

                    if (x>=0 and x<SLIC_width and y>=0 and y<SLIC_height):
                        if new_clusters[y, x] == -1 and SLIC_clusters[j, i] == SLIC_clusters[y, x]:
                            elements.append((y, x))
                            new_clusters[y, x] = label
                            count+=1
                        #end
                    #end
                #end

                counter+=1
            #end
            if (count <= lims >> 2):
                for counter in range(count):
                    new_clusters[elements[counter]] = adj_label
                #end

                label-=1
            #end

            label+=1
        #end
    #end

    SLIC_new_clusters = new_clusters
    #print('SLIC_new_clusters',SLIC_new_clusters.shape)
    return SLIC_new_clusters
#end

def display_contours(color,img,SLIC_width,SLIC_height,SLIC_clusters):
    is_taken = numpy.zeros(img.shape[:2], numpy.bool)
    contours = []

    for i in range(SLIC_width):
        for j in range(SLIC_height):
            nr_p = 0
            for dx, dy in [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (1,1), (0,1), (-1,1)]:
                x = i + dx
                y = j + dy
                if x>=0 and x < SLIC_width and y>=0 and y < SLIC_height:
                    if is_taken[y, x] == False and SLIC_clusters[j, i] != SLIC_clusters[y, x]:
                        nr_p += 1
                    #end
                #end
            #end

            if nr_p >= 2:
                is_taken[j, i] = True
                contours.append([j, i])
            #end
        #end
    #end
    for i in range(len(contours)):
        img[contours[i][0], contours[i][1]] = color

    return img
    #end
#end

def find_local_minimum(center,SLIC_labimg):
    min_grad = 1
    loc_min = center
    for i in range(center[0] - 1, center[0] + 2):
        for j in range(center[1] - 1, center[1] + 2):
            c1 = SLIC_labimg[j+1, i]
            #print('c1 shape',c1)#像素点值，[1,2,4]
            c2 = SLIC_labimg[j, i+1]
            #print('c2 shape',c2.shape)
            c3 = SLIC_labimg[j, i]
            #print('c3 shape',c3.shape)
            if ((c1[0] - c3[0])**2)**0.5 + ((c2[0] - c3[0])**2)**0.5 < min_grad:
                min_grad = abs(c1[0] - c3[0]) + abs(c2[0] - c3[0])
                loc_min = [i, j]
            #end
        #end
    #end
    return loc_min
#end

def calculate_centers(SLIC_width,SLIC_height,SLIC_labimg,step):
    centers = []
    for i in range(step, SLIC_width - int(step/2), step):
        for j in range(step, SLIC_height - int(step/2), step):
            #print(i,j)#48,48 48,96 48,144...
            nc = find_local_minimum((i, j),SLIC_labimg)
            color = SLIC_labimg[nc[1], nc[0]]
            center = [color[0], color[1], color[2], nc[0], nc[1]]
            centers.append(center)
        #end
    #end
    return centers
#end

# global variables
def slic(path,output_path):
    img = cv2.imread(path)
    #print('img',img.shape)#1024,1024

    step = int((img.shape[0]*img.shape[1]/int(4096))**0.5)
    #print('step',step)#48

    SLIC_m = int(30)
    #print('SLIC_m',SLIC_m)

    SLIC_ITERATIONS = 4
    SLIC_height, SLIC_width = img.shape[:2]
    #print('SLIC_height',SLIC_height)
    #print('SLIC_width',SLIC_width)

    SLIC_labimg = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(numpy.float64)
    #print('SLIC_labimg',SLIC_labimg.shape)#1024,1024,3

    SLIC_distances = 1 * numpy.ones(img.shape[:2])
    #print('SLIC_distances',SLIC_distances.shape)#1024,1024,3

    SLIC_clusters = -1 * SLIC_distances
    slic_fuse = -1 * SLIC_distances
    #print('SLIC_clusters',SLIC_clusters.shape)
    #print('SLIC_clusters',SLIC_clusters)

    SLIC_center_counts = numpy.zeros(len(calculate_centers(SLIC_width,SLIC_height,SLIC_labimg,step)))
    #print('SLIC_center_counts',SLIC_center_counts.shape)#400个center

    SLIC_centers = numpy.array(calculate_centers(SLIC_width,SLIC_height,SLIC_labimg,step))
    #print('SLIC_centers',SLIC_centers.shape)#400,5
    # main

    s_centers,s_clusters,s_fuse = generate_pixels(SLIC_m,step,SLIC_height,SLIC_width,SLIC_ITERATIONS,SLIC_centers,SLIC_labimg,img,SLIC_distances,SLIC_clusters,slic_fuse)
    new_s_clusters = create_connectivity(SLIC_width,SLIC_height,s_centers,s_clusters,img)
    #calculate_centers()
    image = display_contours([0.0, 0.0, 0.0],img,SLIC_width,SLIC_height,new_s_clusters)
    #cv2.imshow("superpixels", img)
    #cv2.waitKey(0)
    cv2.imwrite(output_path, image)
    return s_centers,s_fuse

if __name__=='__main__':
    path = os.path.join('inputs', 'shuiti', 'images', '1_1.png')
    path_output = os.path.join('superpixel.png')
    center, fuse = slic(path, path_output)


