from setuptools import setup, find_packages

setup(
    name="sdcopy",
    version="0.1.0",
    description="Tool for saving files off SD cards",
    author="Dmitry Gerasimenko",
    author_email="kiddima@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'sdcopy = sdcopy:main',
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Video",
    ]
)