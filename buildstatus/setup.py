from distutils.core import setup

setup(
    name="buildstatus",
    version="0.1",
    scripts=['buildstatus.py'],
    install_requires=['gpiozero', 'jenkins-webapi', 'sshtunnel'],
)
