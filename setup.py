from setuptools import setup, find_packages

REQUIRED = [
    'numpy',
    'scikit_allel',
    'scikit_learn',
]

setup(
    name='VEF',
    version='0.1',
    url='https://github.com/ChuanyiZ/vef/blob/master/example/vef_clf.py',
    license='MIT',
    description='Variant Ensemble Filter, an ensemble based filter for VCF files.',
    author='Chuanyi Zhang',
    author_email='chuanyi5@illinois.edu',
    python_requires='>=3.4.0',
    packages=find_packages(),
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[\
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
