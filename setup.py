# setup.py
#
# Copyright 2019 Martin Abente Lahaye
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import sys

from setuptools import setup
from setuptools.command.install import install


class CheckRequirementsAndInstall(install):

    requirements = {
        'PyGObject': 'gi',
        'sugar3': 'sugar3',
    }

    def run(self):
        for package, module in self.requirements.items():
            try:
                __import__(module)
            except BaseException:
                print('Package %s not found' % package)
                sys.exit(1)
        install.run(self)


setup(name='sugarapp',
      version='1.13',
      description='Port Sugar activities to other desktops',
      url='https://github.com/tchx84/sugarapp',
      author='Martín Abente Lahaye',
      author_email='tch@sugarlabs.org',
      license='GNU LGPL',
      packages=['sugarapp'],
      zip_safe=False,
      scripts=[
          'bin/sugarapp',
          'utils/sugarapp-gen-appdata',
          'utils/sugarapp-gen-desktop',
          'utils/sugarapp-gen-mimetypes'],
      cmdclass={
          'install': CheckRequirementsAndInstall,
      })
