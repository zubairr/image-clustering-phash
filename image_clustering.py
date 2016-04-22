#!/usr/bin/env python
_author_="M. Zubair Rafique rafique.zubair@gmail.com"

"""
 This script is a part of NDSS'16 and several other papers (DIMVA'13, WWW'14, MALICIA-IJIS'15). 
 Given a name of folder containing images, it cluster 
 the images and output a file  (format: imagename cluster_number).
 *      Publication: It's free for a reason: Exploring the ecosystem of free live streaming services
 *      Where: Proceedings of the 23rd Network and Distributed System Security Symposium (NDSS 2016)
 *      Cite: https://distrinet.cs.kuleuven.be/research/publications/bibtex.do?publicationID=521207
 *      Contact: M. Zubair Rafique (rafique.zubair@gmail.com)
 *      License: See attached    
""" 

import os
from operator import itemgetter
import Image
import math, operator


# directory that contains images
IMAGE_DIR = 'images_dir'
# clustering output file containg name of image and cluster number it belong
RESULTS = "clusters.txt"
# threshold value used to comapre the images
THRESHOLD = 0.3 



class Cluster:
        """ Simple cluster object """
        def __init__(self, image_filename, image_phash):
            # candidate instance's hash value 
            self.candidate_phash = image_phash
            # list of the filenames of all instances in this cluster
            self.cluster_images_list = [image_filename]
            
        def add_image(self, image):
            self.cluster_images_list.append(image)

def compare_avphash(candidate_phash,image_phash,threshold):
        """
        Comparing perceptual hashes of the images.
        :param threshold type: integer
        """
        # comparing average hashes with given threshold value
        h, d = 0, candidate_phash ^ image_phash
        while d:
             h += 1
             d &= d - 1
        if h > threshold:
            return False
        return True

def avhash(image):
        """
        Computing average perceptual hash of the image.
        :param image type: Image.open
        """
        # computing avhash of the image
        im = image.resize((8, 8), Image.ANTIALIAS).convert('L')
        avg = reduce(lambda x, y: x + y, im.getdata()) / 64.
        return reduce(lambda x, (y, z): x | (z << y),
                   enumerate(map(lambda i: 0 if i < avg else 1, im.getdata())),
                   0)  

def clustering(threshold):
        """ 
        The simple clustering algorithm. 
        Depending on the number of similar images and
        a threshold value, the comparisons will be always
        less than nxn (where n is the number of instances).        
        """
        # reading filenames 
        file_names = list_files(IMAGE_DIR)
        # list of clusters
        clusters = []
        print "Processing %s files..." %len(file_names)
        # iterating over images
        for file_name in file_names:
            found_similar = False
            # reading images
            try:
                image = Image.open(file_name)
                image_phash = avhash(image)
            except:
                continue
            # itetrating over clusters
            for cluster in clusters:
               # comparing clusters' candidate Phash with image phash to find match (similarity)
               if compare_avphash(cluster.candidate_phash,image_phash,threshold):
                    # adding image in this cluster
                    cluster.add_image(file_name)
                    found_similar = True
                    # not looking beyond this cluster, first match hard clustering --- **mmm! 
                    break
            # no match found, creating new cluster  
            if not found_similar:
                clusters.append(Cluster(file_name, image_phash))
        # printing clusters
        print_clusters(clusters,threshold)

def list_files(images_dir):
        # reading filanmes of the images from directory
        file_names = []
        files = os.listdir(images_dir)
        for f in files:
            file_names.append('%s/%s' %(images_dir, f))
        return file_names

def print_clusters(clusters,threshold):
        """ Printing clusters in a file clusters.txt """
        print "Printing Clusters...%s" %len(clusters)
        # sorting clusters according to their size
        items = []    
        for cluster in clusters:
            items.append([cluster,len(cluster.cluster_images_list)])
        items.sort(key=itemgetter(1), reverse=True)
        #     
        fp = open(RESULTS,'w')
        # cluster numbers
        cluster_number = 1
        for item in items:
            cluster = item[0]
            output = ""
            for md5 in cluster.cluster_images_list:
                output += md5
                output += ",%s" %str(cluster_number)
                output += "\n"
            fp.write(output)
            cluster_number += 1
        fp.close()

if __name__ == "__main__":
    clustering(THRESHOLD)
        
