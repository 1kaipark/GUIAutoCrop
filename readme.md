# GUIAutoCrop
* A (terrible looking) GUI to automatically crop histological images in a supervised manner.
  * Issue: automatically cropping based on selected contours is good in theory, in practice, images are often too noisy.
  * We can either implement classifiers (skill issue) or manually select valid rects.
* Using thresholding algorithm from: https://github.com/QBI-Microscopy/BatchCrop/releases/
* How it works:
  * choose your composite histological image 
  * based on the shown threshold, input the valid indices as integers separated by commas, then hit crop
  * after this, the user can choose to rotate images. The rotate button performs a 90 degree clockwise rotation.
  * finally, save images to a directory of your choice

# TODOS:
* keep a record of the names of input files. when saving images, just append the section number to this, to avoid the user having to create directories for each slide.
* GUI is very ugly -- lay it out better. This current version (06-03-2024) is just a pilot
* add ability for config with parameters like padding, lightbg, darkbg, etc
* Use and keep record of bugs to fix
  * bug: selecting an image, not cropping, then selecting another image will update the image in memory but will not display. this is due to the bool I have that ensures images won't be displayed twice.



 ／l、                KP❤️
（ﾟ､ ｡ ７
  l  ~ヽ
  じしf_,)ノ
