from PIL import Image
import numpy as np

def dither_matrix(n:int):
    """make dithering matrix of size n*n"""
    if n == 1:
        return np.array([[0]])
    else:
        first = (n ** 2) * dither_matrix(int(n/2))
        second = (n ** 2) * dither_matrix(int(n/2)) + 2
        third = (n ** 2) * dither_matrix(int(n/2)) + 3
        fourth = (n ** 2) * dither_matrix(int(n/2)) + 1
        first_row = np.concatenate((first, second), axis=1)
        second_row = np.concatenate((third, fourth), axis=1)
        return (1/n**2) * np.concatenate((first_row, second_row), axis=0)

def read_bw_image(img:np.array):
    """get image and make it balck and white"""
    R, G, B = img[:, :, 0], img[:, :, 1], img[:, :, 2]
    gray_img = R * 299/1000 + G * 587/1000 + B * 114/1000
    Image.fromarray(gray_img).convert('L').save('grayscale.png')
    return gray_img / 255

def ordered_dithering(pixels:np.array, dm:np.array):
    """dithering image with ordered dithering's algorithm

    Args:
        pixels (np.array): input image
        dm (np.array): dithering matrix
    """
    n = dm.shape[0]
    x_max = pixels.shape[1]
    y_max = pixels.shape[0]

    for x in range(x_max):
        for y in range(y_max):
            i = x % n
            j = y % n
            if pixels[y][x] > dm[i][j]:
                pixels[y][x] = 255
            else:
                pixels[y][x] = 0

    Image.fromarray(pixels).convert('L').save('o_dithered.png', bit=1)

def floyed_steinberg(pixels:np.array, cn:int):
    """dithering image with floyed steinberg's algorithm

    Args:
        pixels (np.array): input image
        cn (int): number of colors per channel (for example nc=2 means we have 2*2*2 = 8 color and 3 bit)
    """
    pixels = np.array(pixels, dtype=float) / 255
    x_max = pixels.shape[1]
    y_max = pixels.shape[0]
    for y in range(y_max):
        for x in range(x_max):
            oldpixel = pixels[y][x].copy()
            newpixel = find_closet_palette_color(oldpixel, cn)
            pixels[y][x] = newpixel
            quant_error = oldpixel - newpixel
            
            # handle border pixels(ignore them:))
            if x < x_max - 1:
                pixels[y, x+1] = pixels[y, x+1] + quant_error * 7/16
            if y < y_max - 1:
                if x > 0:
                    pixels[y+1, x-1] = pixels[y+1, x-1] + quant_error * 3/16
                pixels[y+1, x] = pixels[y+1, x] + quant_error * 5/16
                if x < x_max - 1:
                    pixels[y+1, x+1] = pixels[y+1, x+1] + quant_error * 1/16

        result = np.array(pixels / np.max(pixels, axis=(0,1)) * 255, dtype=np.uint8)
        Image.fromarray(result).save('FS_dithered.png')

def find_closet_palette_color(old_val, nc):
    """find closet color due to number of color we want to have in each channel
    Args:
        old_val: old value of pixel
    Returns:
        new value of pixel
    """
    nc = 2
    return np.round(old_val * (nc - 1)) / (nc - 1)

if __name__ == '__main__':
    img_array = np.array(Image.open('s.jpg'))
    img = read_bw_image(img_array)
    dm = dither_matrix(4)
    ordered_dithering(img, dm)
    
    img_array = np.array(Image.open('1665_girl_with_a_pearl_earring_sm.jpg'))
    floyed_steinberg(img_array)


    
