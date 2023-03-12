# Blurry

Blurry is a Python application that allows you to blur parts of an image. This can be useful for anonymizing personal information or obscuring sensitive data.

## Usage

To start Blurry, run the following command from the project directory:

```shell
python blurry.py
```

This will open a file dialog prompting you to select a directory containing images you wish to edit. Once you have selected a directory, Blurry loads the first image in the folder and displays it in a window.

You can use the following keyboard shortcuts:

`Esc`: Quit the application\
`Space`: Save changes and move to the next image\
`S`: Save changes\
`R`: Reset the current image and start blurring again\
`N` or `→`: Skip the current image and open the next one\
`P` or `←`: Skip the current image and open the previous one

To blur parts of an image, click and drag the mouse over the area you wish to blur. A red rectangle will appear around the selected area. When you release the mouse, the area will be blurred. You can adjust the size of the blur by moving the slider in the toolbar.

## Installation

To run Blurry, you must have Python 3 installed on your computer. Clone this repository and navigate to the project directory. Install the necessary dependencies by running the following command:

```shell
pip install -r requirements.txt
```

## License

This project is licensed under the MIT License.