from setuptools import setup, find_packages


setup(
    name='untold',
    version='0.1.0',
    description='Storytelling engine',
    url='http://github.com/TheCheapestPixels/untold',
    author='Sebastian Hoffmann',
    author_email='TheCheapestPixels@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['docs', 'tests', 'sample_stories']),
    install_requires=[
        'PyYAML',
    ],
    entry_points={
        'console_scripts': [
            'game_repl=untold.tools.game_repl:run_repl',
        ],
    },
    zip_safe=False,
)
