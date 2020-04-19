from setuptools import setup

setup(name='papechan',
      version='0.1',
      description='Automated wallpaper management tool',
      url='http://github.com/Boot-Error/papechan',
      author='Boot-Error',
      author_email='booterror99@gmail.com',
      license='MIT',
      packages=['papechan'],
      zip_safe=False,
      entry_points={
          'console_scripts': ['papechan=papechan:main',
              '4chan-img-dl=papechan:fchan_download']})
