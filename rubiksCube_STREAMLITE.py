# Importing essential libraries

from io import BytesIO
import numpy as np     # Used for using multi-dimensional arrays , matrices and other mathematical functions
import os              # Operating System library to include system dependent functionality like clearing terminal , manipulating paths and interacting with operating system
import copy            # To copy array
from PIL import Image
import numpy as np
import streamlit as st
import zipfile

os.system("cls")     

RES_H = 0
RES_W = 0

# Define Rubik’s Cube standard colors (approximate RGB)
CUBE_COLORS = np.array([
        [255, 255, 255],   # White
        [255, 255,   0],   # Yellow
        [255,   0,   0],   # Red
        [  0, 255,   0],   # Green
        [  0,   0, 255],   # Blue
        [255, 153,   0],   # Orange
    ])

TOLERANCE = 30  # How strict the color match should be

img1_cubic= []
img2_cubic= []

color_code = {"red":[255, 0, 0],"green":[0,255,0],"white":[255,255,255],"orange":[255, 153, 0],"blue":[0, 0, 255],"yellow":[255,255, 0]}
opp_color = {"white":"yellow","yellow":"white","green":"blue","blue":"green","orange":"red","red":"orange"}
corner_count = {"red":0, "blue":0, "orange":0, "yellow":0, "green":0, "white":0}
edge_count = {"red":0, "blue":0, "orange":0, "yellow":0, "green":0, "white":0}

priority_color_queue_img1 = {"white":["yellow","orange","blue","green","red"],
                            "yellow":["white","orange","red","green","blue"],
                            "green":["blue","yellow","red","white","orange"],
                            "blue":["green","yellow","red","orange","white"],
                            "orange":["red","yellow","white","green","blue"],
                            "red":["orange","yellow","blue","green","white"]}

priority_color_queue_img2 = {"white":["yellow","orange","green","blue","red"],
                  "yellow":["white","orange","red","green","blue"],
                  "green":["blue","yellow","white","orange","red"],
                  "blue":["green","yellow","orange","red","white"],
                  "orange":["red","yellow","white","green","blue"],
                  "red":["orange","yellow","blue","green","white",]}

adjacent_colors = {"white":["green","red","blue","orange"],
                  "yellow":["red","green","orange","blue"],
                  "green":["yellow","red","white","orange"],
                  "blue":["red","yellow","orange","white"],
                  "orange":["yellow","green","white","blue"],
                  "red":["green","yellow","blue","white"]}

change_in_img1 = True
prior_color_no = 0
prior_color_no_img1 = 0
prior_color_no_img2 = 0
flag1 = 0
flag2 = 0


def get_color(code):
    for key, val in color_code.items():
        if val == code:
            return key
    return None 

def clear_color_count():
    for key, val in edge_count.items():
        corner_count[key] = 0
        edge_count[key] = 0

def check_common_pieces(i,j,k):
    global change_in_img1, flag1, flag2, prior_color_no_img1, prior_color_no_img2, piece_color_img1, piece_color_img2
    if change_in_img1:
        if flag1 == 0:
            piece_color_img1 = get_color(img1_cubic[i][j][k])
        img1_cubic[i][j][k] = color_code[priority_color_queue_img1[piece_color_img1][prior_color_no_img1]]
        flag1 += 1
        prior_color_no_img1 += 1

    elif not change_in_img1:
        if flag2 == 0:
            piece_color_img2 = get_color(img2_cubic[i][j][k])
           
        img2_cubic[i][j][2-k] = color_code[priority_color_queue_img2[piece_color_img2][prior_color_no_img2]]
        flag2 += 1
        prior_color_no_img2 += 1

def check_if_adjacent_clockwise(center_color, color_1, color_2):
    for i in adjacent_colors[center_color]:
        if i == color_1:
            if adjacent_colors[center_color].index(i) == 0 and adjacent_colors[center_color][-1] == color_2:
                return False
            else:
                return True
        elif i == color_2:
            if adjacent_colors[center_color].index(i) == 0 and adjacent_colors[center_color][-1] == color_1:
                return True
            else:
                return False
            
def find_side_piece(corner_1, corner_2, position):
    index = adjacent_colors[corner_2].index(corner_1)
    if position == "up":
        if(index == 0):
            corner_count[adjacent_colors[corner_2][-1]] += 1
        else:
            corner_count[adjacent_colors[corner_2][index-1]] += 1
    elif position == "down":
        if(index == 3):
            corner_count[adjacent_colors[corner_2][0]] += 1
        else:
            corner_count[adjacent_colors[corner_2][index+1]] += 1
    
def process_images(img1, img2):
    global piece_color_img1, piece_color_img2, flag1, flag2, change_in_img1, prior_color_no_img1, prior_color_no_img2, prior_color_no, img1_cubic, img2_cubic
    
    final_array = []
    img1_3d_to_4d = []
    img2_3d_to_4d = []

    for i in img1:
        for elem in i:
            img1_3d_to_4d.append(list(elem))
    for i in img2:
        for elem in i:
            img2_3d_to_4d.append(list(elem))

    final_array = [
        [
            [i + k + (j * (RES_W*3)) for k in range(3)] 
            for j in range(3)
        ] 
        for i in range(0, (RES_W*3)*(RES_H*3), 3)
    ]
        
    img1_cubic = [final_array[i] for i in range((RES_W*3)*RES_H) if i % (RES_W*3) < RES_W]
    temp_array = copy.deepcopy(img1_cubic)
    img2_cubic = copy.deepcopy(img1_cubic)

    for i in range(RES_H*RES_W):
        for j in range(3):
            for k in range(3):
                t1 = img1_cubic[i][j][k]   
                try:
                    img1_cubic[i][j][k] = list(img1_3d_to_4d[t1])
                    img2_cubic[i][j][k] = list(img2_3d_to_4d[t1])
                except:
                    st.error("PLease upload images with same resolution!")
                    exit(1)

    for i in range(len(img1_cubic)):
        clear_color_count()
        while True:
            if img1_cubic[i][0][2] == img2_cubic[i][0][0] or get_color(img1_cubic[i][0][2]) == opp_color[get_color(img2_cubic[i][0][0])]:
                check_common_pieces(i,0,2)
            else:
                corner_count[get_color(img1_cubic[i][0][2])] += 1
                corner_count[get_color(img2_cubic[i][0][0])] += 1
                find_side_piece(get_color(img1_cubic[i][0][2]),get_color(img2_cubic[i][0][0]),"up")
                prior_color_no_img1 = 0
                prior_color_no_img2 = 0
                flag1 = 0
                flag2 = 0
                change_in_img1 = not change_in_img1
                break
                
        while True:
            if img1_cubic[i][2][2] == img2_cubic[i][2][0] or get_color(img1_cubic[i][2][2]) == opp_color[get_color(img2_cubic[i][2][0])] or (img1_cubic[i][0][2] == img2_cubic[i][2][0] and img1_cubic[i][2][2] == img2_cubic[i][0][0]):
                check_common_pieces(i,2,2)
            else:
                corner_count[get_color(img1_cubic[i][2][2])] += 1
                corner_count[get_color(img2_cubic[i][2][0])] += 1
                find_side_piece(get_color(img1_cubic[i][2][2]),get_color(img2_cubic[i][2][0]),"down")
                prior_color_no_img1 = 0
                prior_color_no_img2 = 0
                flag1 = 0
                flag2 = 0
                change_in_img1 = not change_in_img1
                break
                
        if(img2_cubic[i][0][0] == img2_cubic[i][2][0] and get_color(img1_cubic[i][0][2]) != opp_color[get_color(img1_cubic[i][2][2])] and (not check_if_adjacent_clockwise(get_color(img2_cubic[i][0][0]),get_color(img1_cubic[i][0][2]),get_color(img1_cubic[i][2][2])))):
            temp = img1_cubic[i][0][2]
            img1_cubic[i][0][2] = img1_cubic[i][2][2]
            img1_cubic[i][2][2] = temp
        if(img1_cubic[i][0][2] == img1_cubic[i][2][2] and get_color(img2_cubic[i][0][0]) != opp_color[get_color(img2_cubic[i][2][0])] and (not check_if_adjacent_clockwise(get_color(img1_cubic[i][0][2]),get_color(img2_cubic[i][2][0]),get_color(img2_cubic[i][0][0])))):
            temp = img2_cubic[i][0][0]
            img2_cubic[i][0][0] = img2_cubic[i][2][0]
            img2_cubic[i][2][0] = temp

        while True:
            if img1_cubic[i][1][2] == img2_cubic[i][1][0] or get_color(img1_cubic[i][1][2]) == opp_color[get_color(img2_cubic[i][1][0])]:
                if change_in_img1:
                    if flag1 == 0:
                        piece_color_img1 = get_color(img1_cubic[i][1][2])
                    if(prior_color_no_img1 >= 5):
                        break    
                        
                    img1_cubic[i][1][2] = color_code[priority_color_queue_img1[piece_color_img1][prior_color_no_img1]]
                    flag1 += 1
                    prior_color_no_img1 += 1
                elif not change_in_img1:
                    if flag2 == 0:
                        piece_color_img2 = get_color(img2_cubic[i][1][0])
                    img2_cubic[i][1][0] = color_code[priority_color_queue_img2[piece_color_img2][prior_color_no_img2]]
                    flag2 += 1
                    prior_color_no_img2 += 1

            else:
                edge_count[get_color(img1_cubic[i][1][2])] += 1
                edge_count[get_color(img2_cubic[i][1][0])] += 1
                prior_color_no_img1 = 0
                prior_color_no_img2 = 0
                prior_color_no = 0
                flag1 = 0
                flag2 = 0
                change_in_img1 = not change_in_img1
                break
                
        for j in range(3): 
            for k in range(3):
                visited_1 = False
                visited_2 = False
                if k != 2:

                    while True:   
                        if (k == 0 and (j == 0 or j == 2)):
                            if not visited_1:
                                if corner_count[get_color(img1_cubic[i][j][k])] != 4:
                                    corner_count[get_color(img1_cubic[i][j][k])] += 1
                                    visited_1 = True
                                else:
                                    if(flag1 == 0):
                                        piece_color_img1 = get_color(img1_cubic[i][j][k])
                                    img1_cubic[i][j][k] = color_code[priority_color_queue_img1[piece_color_img1][prior_color_no_img1]]
                                    flag1 += 1
                                    prior_color_no_img1 += 1

                            if not visited_2:
                                if corner_count[get_color(img2_cubic[i][j][2-k])] != 4:
                                    corner_count[get_color(img2_cubic[i][j][2-k])] += 1
                                    visited_2 = True
                                else:
                                    if(flag2 == 0):
                                        piece_color_img2 = get_color(img2_cubic[i][j][k])
                                    img2_cubic[i][j][2-k] = color_code[priority_color_queue_img2[piece_color_img2][prior_color_no_img2]]
                                    flag2 += 1
                                    prior_color_no_img2 += 1

                            if visited_1 and visited_2:
                                prior_color_no_img1 = 0
                                prior_color_no_img2 = 0
                                flag1 = 0
                                flag2 = 0
                                break
                                
                        elif ((k == 1 and (j == 0 or j == 2)) or (k == 0 and j == 1)):
                            if not visited_1:
                                if edge_count[get_color(img1_cubic[i][j][k])] != 4:
                                    edge_count[get_color(img1_cubic[i][j][k])] += 1
                                    visited_1 = True
                                else:
                                    if(flag1 == 0):
                                        piece_color_img1 = get_color(img1_cubic[i][j][k])
                                    img1_cubic[i][j][k] = color_code[priority_color_queue_img1[piece_color_img1][prior_color_no_img1]]
                                    flag1 += 1
                                    prior_color_no_img1 += 1

                            if not visited_2:
                                if edge_count[get_color(img2_cubic[i][j][2-k])] != 4:
                                    edge_count[get_color(img2_cubic[i][j][2-k])] += 1
                                    visited_2 = True
                                else:
                                    if(flag2 == 0):
                                        piece_color_img2 = get_color(img2_cubic[i][j][k])
                                    img2_cubic[i][j][2-k] = color_code[priority_color_queue_img2[piece_color_img2][prior_color_no_img2]]
                                    flag2 += 1
                                    prior_color_no_img2 += 1

                            if visited_1 and visited_2:
                                prior_color_no_img1 = 0
                                prior_color_no_img2 = 0
                                flag1 = 0
                                flag2 = 0
                                break
                                
                        else:
                            if img1_cubic[i][j][k] == img2_cubic[i][j][2-k] or get_color(img1_cubic[i][j][k]) == opp_color[get_color(img2_cubic[i][j][2-k])]:
                                if change_in_img1:
                                    if flag1 == 0:
                                        piece_color_img1 = get_color(img1_cubic[i][j][k])
                                    img1_cubic[i][j][k] = color_code[priority_color_queue_img1[piece_color_img1][prior_color_no]]
                                    prior_color_no += 1
                                    flag1 += 1

                                elif not change_in_img1:
                                    if flag2 == 0:
                                        piece_color_img2 = get_color(img2_cubic[i][j][k])
                                    img2_cubic[i][j][2-k] = color_code[priority_color_queue_img2[piece_color_img2][prior_color_no]]
                                    prior_color_no += 1
                                    flag2 += 1

                            else:
                                prior_color_no = 0
                                flag1 = 0
                                flag2 = 0
                                change_in_img1 = not change_in_img1
                                break
    

    new_img1 = [[0 for _ in range((RES_W*3))] for _ in range((RES_H*3))]
    new_img2 = [[0 for _ in range((RES_W*3))] for _ in range((RES_H*3))]

    my_1d_list = [value for dim1 in temp_array for dim2 in dim1 for value in dim2]
    new_img1_1d = [value for dim1 in img1_cubic for dim2 in dim1 for value in dim2]
    new_img2_id = [value for dim1 in img2_cubic for dim2 in dim1 for value in dim2]
    x = 0

    for i in my_1d_list:
        new_img1[i//(RES_W*3)][i%(RES_W*3)] = new_img1_1d[x]
        new_img2[i//(RES_W*3)][i%(RES_W*3)] = new_img2_id[x]
        x += 1

    new_img1 = np.array(new_img1)
    new_img2 = np.array(new_img2)
    new_img1 = new_img1.astype(np.uint8)
    new_img2 = new_img2.astype(np.uint8)

    return new_img1, new_img2

def adjust_and_crop_image(img):
    """Crop image so both width and height are multiples of 3."""
    width, height = img.size
    new_width = width - (width % 3)
    new_height = height - (height % 3)
    # Crop the image from bottom/right if necessary
    if (new_width != width) or (new_height != height):
        img = img.crop((0, 0, new_width, new_height))
    return img

def get_upscaled_images(img_array, upscale_factor, RES_H, RES_W):
    import numpy as np
    from PIL import Image

    # Repeat each input pixel to make each output pixel a square of upscale_factor × upscale_factor pixels
    upscaled_array = np.kron(img_array, np.ones((upscale_factor, upscale_factor, 1)))
    img = Image.fromarray(upscaled_array.astype('uint8'), 'RGB')

    # Calculate final upscaled shape based on RES_H, RES_W and upscale factor
    final_width = RES_W * 3 * upscale_factor
    final_height = RES_H * 3 * upscale_factor

    # This guarantees the upscaled image fills the entire mosaic grid area, regardless of aspect ratio
    return img.resize((final_width, final_height))

def main():
    st.markdown("""
    <style>
        /* Increase sidebar width */
        [data-testid="stSidebar"] {
            min-width: 400px;
            max-width: 400px;
        }
    </style>
""", unsafe_allow_html=True)

    VIDEO_URL = "https://raw.githubusercontent.com/AnshVP/DualSided_RubiksCube/main/video.mp4"

    st.sidebar.markdown(f"""
        <p style="display: flex; justify-content: center;">
            <video autoplay loop muted playsinline style="max-width: 370px; max-height: 400px; border-radius: 10px;">
                <source src="{VIDEO_URL}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </p>
    """, unsafe_allow_html=True)


    col1, col2 = st.columns([2, 8])  # Adjust width ratios as needed
    
    with col1:
        st.image("cube.png", use_container_width=True)  # Or use a URL or other local path

    with col2:  
        st.markdown("<h1 style='padding-top: 10px;'>Dual-Sided Rubik's Cube Mosaic 1.0</h1>", unsafe_allow_html=True)
    st.write("---") 
    
    st.sidebar.markdown("<div style='font-size:18px; font-weight:bold;'>This application creates a dual-sided Rubik's Cube mosaic from two input images. Cubes are arranged so that 2 adjacent faces displays a different image, revealing a second view when seen from a side angle. Designed for hands-on learning and public engagement, it's a powerful tool for showing how art and algorithms can work together in one space.</div>", unsafe_allow_html=True)
    
    st.markdown("<h4 style='text-align: left;'>Step 1:</h4>", unsafe_allow_html=True)
    st.markdown("Generate mosaic for individual images from here (https://bestsiteever.ru/mosaic/).")

    st.markdown("</br>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: left;'>Step 2: Drag and Drop Mosaic Images</h4>", unsafe_allow_html=True)

    # Upload the first image
    img1 = st.file_uploader("Upload Image 1", type=["png", "jpg", "jpeg"])

    # Upload the second image
    img2 = st.file_uploader("Upload Image 2", type=["png", "jpg", "jpeg"])
    st.write("---")

    # Process the images if both are uploaded
    if img1 is not None and img2 is not None:
        global RES_H, RES_W

        try:
            img1 = Image.open(img1).convert('RGB')
            img1 = adjust_and_crop_image(img1)
            st.info(f"Image 1 automatically cropped to {img1.size} for mosaic compatibility.")
        
            img2 = Image.open(img2).convert('RGB')
            img2 = adjust_and_crop_image(img2)
            st.info(f"Image 2 automatically cropped to {img2.size} for mosaic compatibility.")
        
        except Exception as e:
            st.error("❌ Failed to open one or both files. Make sure they're valid images.")
            st.stop()

        if img1.size != img2.size:
            st.error("❌ Make sure to upload images with same resolution.")
            st.stop()

        else:
            # Convert the RGB image to a NumPy array
            img1_array = np.array(img1)
            img2_array = np.array(img2)

            RES_H = img1_array.shape[0] // 3  # Height in cube blocks
            RES_W = img1_array.shape[1] // 3  # Width in cube blocks

            upscale_factor = 8  
            upscaled_img1 = get_upscaled_images(img1_array, upscale_factor, RES_H, RES_W)
            upscaled_img2 = get_upscaled_images(img2_array, upscale_factor, RES_H, RES_W)

            st.subheader("Image 1")
            st.image(upscaled_img1,  use_container_width=True)

            st.subheader("Image 2")
            st.image(upscaled_img2,  use_container_width=True)

            if st.button("Process Images"):
                try:
                    new_img1, new_img2 = process_images(img1_array, img2_array)
                except Exception as e:
                    st.error("❌ Please upload valid Rubik's Cube miniature mosaic image.")
                    st.stop()

                upscale_factor = 8  

                upscaled_img1 = get_upscaled_images(new_img1, upscale_factor, RES_H, RES_W)
                upscaled_img2 = get_upscaled_images(new_img2, upscale_factor, RES_H, RES_W)

                st.subheader("Processed Image 1")
                st.image(upscaled_img1,  use_container_width=True)

                st.subheader("Processed Image 2")
                st.image(upscaled_img2,  use_container_width=True)

                st.success("Images processed successfully!")

                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    for image, filename in zip([Image.fromarray(new_img1), Image.fromarray(new_img2)], ['converted_img1.png', 'converted_img2.png']):
                        # Create an in-memory stream for each image
                        image_stream = BytesIO()
                        image.save(image_stream, format='PNG')
                        image_bytes = image_stream.getvalue()
                        # Add the image bytes to the ZIP file
                        zip_file.writestr(filename, image_bytes)

                # Provide the ZIP file for download
                zip_data = zip_buffer.getvalue()
                st.download_button(
                    label="Download Images",
                    data=zip_data,
                    file_name="DualSided_Rubik'sCube_images.zip",
                    mime="application/zip",
                )

                st.markdown("</br>", unsafe_allow_html=True)
                st.markdown("<h4 style='text-align: left;'>Step 3:</h4>", unsafe_allow_html=True)
                st.markdown("Paste the downloaded images for building mosaic here (https://bestsiteever.ru/mosaic/) and download the pdf.")
        

if __name__ == "__main__":
    main()
