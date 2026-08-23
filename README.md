# ***Photo Album***

Photo Album Web Application (Python Flask app)

Allows the user to set up image galleries within the web application's static/sets directory. All image 
galleries can be viewed by clicking the gallery's cover image. When the gallery loads all the galleries images 
are displayed.

**Python Packages**
  * Flask
  * Flask-Login
  * Flask-Bcrypt
  * Jinja2
  * Python-dotenv

**Application Settings**
The following settings are set within the applications config.env file
SECRET_KEY = [set this with a long random string]
REQUIRE_LOGIN = True        # Set to False to disable authentication entirely
ART_SECTION = True          # Set to False to hide the art section entirely from the UI
LIGHTBOX_THUMBNAILS = True  # Set to False to hide the thumbnail strip at the bottom of the lightbox

**Login Setup**
Currently if Login is used it is pretty basic. There are no individual profiles or image galleries tied to different 
user ids at this time.

If the login functionality is used, it just makes a person provide credentials so that they can view the contained 
images.

Users and their encrypted passwords are saved in a users.json file. This file is used to confirm a login and allow a
user access. New users can be created using the create_user.py file for now.

**Photo Archive:**  
Image Collections on the Photo Archive page:
  * Can be filtered by the Collection Name, Person, or Tag.
  * Can be sorted by Image Sets (Date Added), Recent Updates, Image Count,or Randomly.
  * Show set title, and image count.

**Art Section (optional):**  
If Art section is used (enabled with ART_SECTION = True)
  * The Art section can be used for a separate display collections of Art, Comics, Drawings, ect.
  * A drop-down appears that allows the user to switch between the two sections.
  * The Art section lists all series of images as separate image sets.
  * Can be filtered by the Series name or the Set name.

**Image Set Meta Files:**  
Each photo set has a meta.json file which contains:
  * Title - title of the gallery
  * People - used to sort image galleries on the People page
  * Tags - used to sort image galleries on the Tags page
  * Cover - used to determine which image is used as a cover image for the gallery

If the Art section option is used, those images will need to contain additional metadata:
  * Type - used to separate normal photo collections from art collections
  * Series - used as the title for a collection of related art
  * Issue - used to order art collections sequentially 
  
**Collections**
Individual images from the various galleries can be added or removed from Collections by right-clicking the images and 
adding them to existing Collections or by creating new Collections. Empty collections are deleted automatically.

**Image Tagging:**  
Galleries can be tagged in one of two ways:
  * By Tags that describe the image.
  * By People that are in the image.
  * Tags/People that have been added can be removed as needed.
  * There are separate pages where existing Tags/People are listed. Clicking on links on those pages loads all images
  that share the Tag/People designation.
  * Each Gallery page will list all Tags/People as links, allowing one to click the links to find other similar or 
  related images.

**Lightbox:**  
Images are shown in a lightbox viewer which has the ability to:
  * User can cycle through pictures with arrows on screen or arrow keys on keyboard.
  * User can select picture to view from thumbnail image navigation (if enabled).
  * User can zoom with the mouse wheel when the CTRL key is pressed
  * User can view the image full screen.
  * User can download image with a click of a button.
  * User can close image by clicking the X button.
  * Image counter added to the viewing area.

**Image Notes:**  
The site expects three sets of image sizes
  * Full sized images are shown in the Lightbox display for the selected image
  * Thumbnail sized image (400px wide) for the archive and gallery image displays
  * Thumbnail sized image for the thumbnail image navigation within the Lightbox
  * Images are stored in the static/sets folder. Each set folder has a thumbnails subdirectory where all thumbnails 
  for that set are stored.
  * Image preparation for this photo album is made easier with this companion tool:
    * https://github.com/pa-childs/Image_Processor