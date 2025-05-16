from setuptools import setup
import os

# Get the current directory
here = os.path.abspath(os.path.dirname(__file__))

# Read requirements from requirements.txt
def get_requirements():
    with open(os.path.join(here, 'requirements.txt')) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Get package data
package_data = {
    'back': [
        '*.py',
        'templates/*',
        'static/*'
    ]
}

setup(
    name='AyurvedaBackend',
    version='0.0.1',
    packages=['back'],
    package_dir={'': 'back'},
    package_data=package_data,
    include_package_data=True,
    install_requires=get_requirements(),
    entry_points={
        'console_scripts': [
            'ayurveda-backend=back.app:app'
        ]
    }
)
