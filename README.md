# Photo Album

Photo album web application (Python Flask app)

Allows the user to place collections of images within that web application's static/sets directory. All image 
collections can be viewed by clicking the collection link, and the collection loads all the contained images 
are displayed.

* Each image collection has a meta.json file which contains:
  * Title
  * People
  * Tags
  * Description
  * Cover

* Image Collection on the Image Archive page:
  * Can be sorted by Most Recent or Most Images
  * Show set title, and image count

* Images are shown in lightbox which has the ability to:
  * Cycle through pictures with arrows on screen or arrow keys on keyboard
  * Zoom and pan with mouse scroll wheel 
  * Close image by clicking outside of the image or the X button
