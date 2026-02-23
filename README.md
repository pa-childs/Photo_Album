# Photo Album

Photo Album web application (Python Flask app)

Allows the user to place collections of images within that web application's static/sets directory. All image 
collections can be viewed by clicking the collection image/link. When the collection loads all the contained images 
are displayed.

* Each photo collection has a meta.json file which contains:
  * Title
  * People
  * Tags
  * Description
  * Cover

* If the Art section option is used, those images will need to contain additional meta data:
  * Type
  * Series
  * Issue

The Art section can be used to display collections of Art, Comics, Drawings, ect.

* Image Collections on the Photo Archive page:
  * Can be filtered by the Collection name.
  * Can be sorted by Most Recent or Most Images.
  * Show set title, and image count.

* If Art section is used
  * A drop-down appears that allows the user to switch between the two sections.
  * The Art section lists all series of images as separate collections.
  * Can be filtered by the Series name or the Collection name.

* Image collections can be tagged in on of two ways:
  * By Tags that describe the image.
  * By People that are in the image.
  * Tags/People can be removed as well.
  * There are separate pages where existing Tags/People are listed. Clicking on links there will load just image 
  collections that have those Tags/People.
  * Each image collection page will list all Tags/People as links, allowing one to click the links to find related 
  images.

* Images are shown in lightbox which has the ability to:
  * User can cycle through pictures with arrows on screen or arrow keys on keyboard.
  * User can select picture to view from thumbnail image navigation.
  * User can zoom and pan with mouse scroll wheel.
  * User can view the image full screen.
  * User can download image with a click of a button.
  * User can close image by clicking outside the image or the X button.
  * Image counter added to the viewing area.
