from setuptools import setup

setup(
    name='ocr_server',
    version='1.1',
    packages=['server'],
    url='https://github.com/digitalmethodsinitiative/ocr_server',
    license='',
    author='Dale Wahl',
    author_email='dalewahl@gmail.com',
    description='Text detection API',
    install_requires=[
        'keras_ocr',
        'gunicorn',
        'pyyaml',
        'flask',
        'tensorflow',
        'paddlepaddle',
        'paddleocr',
    ]
)
