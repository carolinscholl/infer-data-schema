from setuptools import setup, find_packages

setup(
    name='infer-data-schema',
    version='0.1.0',
    packages=["infer_schema", "infer_schema.utils"],
    url='',
    license='',
    author='Carolin Scholl',
    description='Inference of the json or csv schema from a given data file',
    entry_points={
        'console_scripts': [
            'run-schema-inference = infer_schema.main:main',
        ]
    },
    python_requires='>=3.8.10',
    install_requires=[
        'genson==1.2.2',
        'jsonschema==4.17.0',
        'pandas==1.5.2',
        'omegaconf==2.2.3',
        'pytest==6.2'
    ]
)
