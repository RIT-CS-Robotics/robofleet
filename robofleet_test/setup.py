from setuptools import find_packages, setup

package_name = 'robofleet_test'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robofleet',
    maintainer_email='robofleet@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'init = robofleet_test.init:main',
            'drive = robofleet_test.drive:main',
            'scantest = robofleet_test.scantest:main'
        ],
    },
)
