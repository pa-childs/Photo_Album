# Photo Album

Photo album web application (Python Flask app)

Allows the user to place sets of images within that web application's image/sets directory. All image sets can be viewed on the initial page, and when a set is selected all of the contained images are displayed for that set.

* Each set has a meta.json file when contains:
  * Title
  * Tags
  * Description
* Image Sets on the main page can be:
  * Filtered by tags
  * Show set title, tags, and image count
* Images are shown in lightbox
  * Cycle through pictures with arrows or keys
  * Zoom and pan with mouse 
  * Close image by clicking outside of image/X button
