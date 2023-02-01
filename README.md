# OCR Server: Detect text from images

DMI developed a simple Flask based API that runs pre trained Optical Character
Recognition (OCR) models on provided images and returns the detected text  in
location based groups.

# Quick Setup

The OCR Server runs in a Docker container.

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop), and start it.
2. Clone the OCR Server repository (e.g. `git clone https://github.com/digitalmethodsinitiative/ocr_server.git`)
3. (Optional) Update or change any settings in the `config.yml` file
4. In a terminal/command prompt, navigate to the folder in which you just cloned OCR server (the folder that contains the `config.yml` file)
5. Run `docker build -t ocr_server .`
 - This will create a Docker image called `ocr_server` and may take a while to download and install necessary packages
6. Run `docker run --publish 4000:80 --name ocr_server --detach ocr_server`
 - This creates a running container of the `ocr_server` image
 - `--publish 4000:80` opens port `4000` on your machine and connects it to port `80` in the container; you may update `4000` to any port you wish
 - Add a [restart policy](https://docs.docker.com/config/containers/start-containers-automatically/) such as `--restart unless-stopped` and the OCR container will restart if host server is rebooted, Docker crashes, etc.

# Usage

DMI primarily designed the OCR Server to work as a processor with [4CAT](https://github.com/digitalmethodsinitiative/4cat).
Add the hosted server address (http://wherever:4000/api/detect_text) to 4CAT Settings
in the "OCR: Text from images" section and the processor should appear for any
dataset of images.

The OCR Server can also be used independently. It is essentially just an API
that can be accessed via python `requests`, `curl`, or any other framework.

Python for example:
```
import requests
server = 'http://localhost:4000/'
filename = 'any/dir/to/image.jpg'

with open(filename, "rb") as infile:
    api_response = requests.post(server + 'api/detect_text', files={'image': infile})
    # To specify a model type, you can use `paddle_ocr` or `keras_ocr` like so
    #api_response = requests.post(server + 'api/detect_text', files={'image': infile}, data={'model_type': 'paddle_ocr'})
```

The `api_response` should return a `200` status code and a JSON object containing
the `filename` and `simplified_text` which consists of a collection
of `groupings` and the `raw_text` alone.

# Available OCR models

Currently, the OCR Server has two available models that can be selected.

1. PaddleOCR: [The PaddleOCR package](https://github.com/PaddlePaddle/PaddleOCR#readme) provides access
to a [number of different OCR models](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_en/models_list_en.md).
We currently only support the english PP-OCRv3 model, but adding support for
other languages is possible if there is a desire (and they exist).
2. Keras-OCR: The keras-ocr package ([Keras OCR Documentation]( https://keras-ocr.readthedocs.io/en/latest/))
 first detects areas of an image that may contain text with the pretrained
[Character-Region Awareness For Text (CRAFT) text detection model](https://github.com/clovaai/CRAFT-pytorch)
and then attempts to predict the text inside each area using [Keras' implementation of a Convolutional Recurrent Neural
Network (CRNN) model](https://github.com/kurapan/CRNN) for text recognition. Once words are predicted, we developed an
[algorithm](https://github.com/digitalmethodsinitiative/ocr_server/blob/3682fdd97fbcf6c00f8523e19c4b13f4601077ec/ocr_detection/image_handler.py#L88)
to attempt to sort the text into likely groupings based on locations within the original image.

# Helpful Docker commands
 1. View container logs
  `docker container logs container_name`
 2. Stop running container
 `docker stop container_name`
 3. Start stopped container
 `docker start container_name`
 4. Connect to container command line
 `docker exec -it container_name /bin/bash`
 5. Remove container
 `docker container rm container_name`
 Useful to remove then recreate with new parameters (e.g. port mappings)
 6. Remove image
 `docker image rm image_name:image_tag`
 Useful if you need to change `Dockerfile` and rebuild
     - Note: must also remove any containers dependent on image; you could alternately create a new image with a different name:tag
 7. Copy files into container
 `docker cp path/to/file container_name:/app/path/to/desired/directory/`
 Can update and change files (e.g. `config.py` or other configuration files)
 Note: may require restarting the container to take effect
