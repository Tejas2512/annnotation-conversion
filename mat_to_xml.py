'''
This file converts the hand dataset (https://www.robots.ox.ac.uk/~vgg/data/hands/) to Pascal Format
'''

import scipy.io as sio
from os import listdir
from os.path import isfile, join
import math
from xml.etree import ElementTree as et
import cv2
from xml.dom import minidom

MAT_FILES_PATH = 'annotations'
IMG_FILES_PATH = 'images'
XML_FILES_PATH = 'annotations_xml'


def get_img_size_node(img_path):
    img = cv2.imread(img_path)
    img_size = img.shape
    size_node = et.Element('size')

    width_node = et.Element('width')
    width_node.text = str(img_size[0])
    size_node.append(width_node)

    height_node = et.Element('height')
    height_node.text = str(img_size[1])
    size_node.append(height_node)

    depth_node = et.Element('depth')
    depth_node.text = str(img_size[2])
    size_node.append(depth_node)

    return size_node


def get_object_node(hand):
    hand_node = et.Element('object')

    name_node = et.Element('name')
    name_node.text = 'hand'
    hand_node.append(name_node)

    pose_node = et.Element('pose')
    pose_node.text = 'Unspecified'
    hand_node.append(pose_node)

    truncated_node = et.Element('truncated')
    truncated_node.text = '0'
    hand_node.append(truncated_node)

    difficult_node = et.Element('difficult')
    difficult_node.text = '0'
    hand_node.append(difficult_node)

    bbox_node = et.Element('bndbox')
    xmin_node = et.Element('xmin')
    xmin_node.text = '{0:.2f}'.format(hand[0])
    bbox_node.append(xmin_node)

    ymin_node = et.Element('ymin')
    ymin_node.text = '{0:.2f}'.format(hand[1])
    bbox_node.append(ymin_node)

    xmax_node = et.Element('xmax')
    xmax_node.text = '{0:.2f}'.format(hand[2])
    bbox_node.append(xmax_node)

    ymax_node = et.Element('ymax')
    ymax_node.text = '{0:.2f}'.format(hand[3])
    bbox_node.append(ymax_node)

    hand_node.append(bbox_node)

    return hand_node


# Read the given mat file and add hand objects to the corresponding XML file
def read_mat_file(filepath, filename):
    mat_data = sio.loadmat(filepath)
    hand_pos = []  # To store the hand positions in an image

    # For all hands in the image align the bounding box to an axis
    for i in range(len(mat_data['boxes'][0])):
        xmin = math.inf
        ymin = math.inf
        xmax = -1
        ymax = -1

        for j in range(4):
            x, y = mat_data['boxes'][0][i][0][0][j][0]
            if xmin > x:
                xmin = x
            if ymin > y:
                ymin = y
            if xmax < x:
                xmax = x
            if ymax < y:
                ymax = y

        hand_pos.insert(0, [xmin, ymin, xmax, ymax])

    # Create the XML file
    create_xml_file(hand_pos, filename)


def create_xml_file(hand_pos, filename):
    # Generate the image file name
    img_filename = filename.split('.')[0] + '.jpg'
    xml_filename = filename.split('.')[0] + '.xml'

    root = et.Element('annotation')
    tree = et.ElementTree(root)  # Create a XML tree with root as 'annotation'

    # Create an element folder
    folder = et.Element('folder')
    folder.text = 'imgs/'
    root.append(folder)

    # Add filename
    filename_node = et.Element('filename')
    filename_node.text = img_filename
    root.append(filename_node)

    # Add filepath
    filepath_node = et.Element('path')
    filepath_node.text = filename_node.text
    root.append(filepath_node)

    # Node for the size of the image
    img_path = join(IMG_FILES_PATH, img_filename)
    size_node = get_img_size_node(img_path)
    root.append(size_node)

    # Add segmented node
    segmented_node = et.Element('segmented')
    segmented_node.text = '0'
    root.append(segmented_node)

    # Add the objects
    for hand in hand_pos:
        hand_node = get_object_node(hand)
        root.append(hand_node)

    rough_xml = et.tostring(root, 'utf-8')
    rough_xml = minidom.parseString(rough_xml)
    pretty_xml = rough_xml.toprettyxml()
    # print(pretty_xml)

    # Save the XML file
    xml_path = join(XML_FILES_PATH, xml_filename)
    with open(xml_path, 'w') as xml_file:
        xml_file.write(pretty_xml)


def main():
    # Read a .mat file and convert it to a pascal format

    # List all files in the MAT_FILES_PATH and ignore hidden files (.DS_STORE for Macs)
    mat_files = [[join(MAT_FILES_PATH, x), x] for x in listdir(MAT_FILES_PATH) if
                 isfile(join(MAT_FILES_PATH, x)) and x[0] is not '.']
    # Iterate through all files and convert them to XML
    for mat_file in mat_files:
        # print(mat_file)
        read_mat_file(mat_file[0], mat_file[1])
        # break


if __name__ == '__main__':
    main()