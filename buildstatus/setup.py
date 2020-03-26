from distutils.core import setup

setup(
    name="buildstatus",
    version="0.1",
    install_requires=['gpiozero', 'jenkins-webapi', 'sshtunnel'],
    py_modules=['buildstatus'],
    entry_points={"console_scripts":["buildstatus=buildstatus:main"]}
)
