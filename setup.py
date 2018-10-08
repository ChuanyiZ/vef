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
    # If your package is a single module, use this instead of 'packages':
    # py_modules=['mypackage'],

    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[\
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
)
